"""CLI entrypoint for the audit issue engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Preload torch early on Windows so later sklearn/UMAP-related native imports
# do not interfere with PyTorch DLL initialization in the dense encoder path.
try:  # pragma: no cover - optional dependency / environment-specific
    import torch  # noqa: F401
except Exception:  # pragma: no cover - keep CPU-only setups working
    torch = None

import pandas as pd
import typer
from rich.console import Console

from audit_issue_engine.assignment.matcher import assign_issue_labels
from audit_issue_engine.config.settings import load_runtime_config
from audit_issue_engine.discovery.clusterer import cluster_issue_space
from audit_issue_engine.discovery.outlier_handler import resolve_outliers
from audit_issue_engine.discovery.reducer import reduce_features
from audit_issue_engine.discovery.title_generator import build_working_types
from audit_issue_engine.extraction.fact_extractor import extract_issue_facts
from audit_issue_engine.ingest.loader import load_input_table
from audit_issue_engine.ingest.validator import validate_required_fields, validate_ticket_ids
from audit_issue_engine.ingest.writer import write_tickets_artifacts
from audit_issue_engine.issue_split.issue_segmenter import build_issue_records
from audit_issue_engine.reporting.excel_reports import write_excel_reports
from audit_issue_engine.reporting.markdown_summary import write_run_summary
from audit_issue_engine.reporting.parquet_exports import export_parquet_tables
from audit_issue_engine.representation.dense_encoder import encode_dense_features
from audit_issue_engine.representation.feature_store import persist_feature_store
from audit_issue_engine.representation.sparse_features import build_sparse_features
from audit_issue_engine.taxonomy.canonical_store import load_canonical_store
from audit_issue_engine.taxonomy.promoter import promote_working_types
from audit_issue_engine.term_mining.ngram_miner import mine_ngram_terms
from audit_issue_engine.term_mining.normalizer import normalize_terms
from audit_issue_engine.term_mining.pmi_miner import mine_pmi_terms


app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()


def get_project_root() -> Path:
    """Resolve the repository root from the CLI module location."""

    return Path(__file__).resolve().parents[2]


def _run_ingest(runtime) -> pd.DataFrame:
    tickets = load_input_table(runtime.input_path_or_uri).fillna("")
    validate_required_fields(tickets, runtime.required_fields)
    validate_ticket_ids(tickets)
    write_tickets_artifacts(tickets, runtime)
    return tickets


def _run_discovery(runtime, tickets: pd.DataFrame) -> dict[str, Any]:
    issues = build_issue_records(tickets, runtime.primary_text_field, runtime.secondary_text_field)
    if issues.empty:
        empty = pd.DataFrame()
        export_parquet_tables(
            runtime.run_dir,
            {
                "issues.parquet": issues,
                "term_catalog.parquet": empty,
                "issue_facts.parquet": empty,
                "working_types.parquet": empty,
                "issue_working_map.parquet": empty,
            },
        )
        return {
            "issues": issues,
            "term_catalog": empty,
            "facts": empty,
            "working_types": empty,
            "issue_working_map": empty,
            "diagnostics": {
                "dense_encoder_mode": "skipped",
                "reducer": "skipped",
                "clusterer": "skipped",
            },
        }

    ngram_terms = mine_ngram_terms(issues["issue_text"].astype(str).tolist(), top_k=runtime.profile.term_top_k)
    pmi_terms = mine_pmi_terms(issues["issue_text"].astype(str).tolist())
    term_catalog = normalize_terms(ngram_terms, pmi_terms)
    facts = extract_issue_facts(issues, term_catalog)

    sparse_matrix, sparse_artifacts = build_sparse_features(issues["issue_text"].astype(str).tolist())
    dense_embeddings, dense_meta = encode_dense_features(
        issues["issue_text"].astype(str).tolist(),
        runtime.profile,
        runtime.project_root / runtime.base.paths["cache_dir"],
    )
    persist_feature_store(runtime.run_dir, sparse_matrix, sparse_artifacts, dense_embeddings, dense_meta)

    reduced_features, reducer_name = reduce_features(sparse_matrix, dense_embeddings, runtime.profile)
    raw_labels, clusterer_name = cluster_issue_space(reduced_features, runtime.profile)
    resolved_labels = resolve_outliers(
        raw_labels,
        reduced_features,
        issues["issue_id"].astype(str).tolist(),
        runtime.profile.outlier_similarity_threshold,
    )
    working_types, issue_working_map = build_working_types(issues, facts, resolved_labels)

    export_parquet_tables(
        runtime.run_dir,
        {
            "issues.parquet": issues,
            "term_catalog.parquet": term_catalog,
            "issue_facts.parquet": facts,
            "working_types.parquet": working_types,
            "issue_working_map.parquet": issue_working_map,
        },
    )
    return {
        "issues": issues,
        "term_catalog": term_catalog,
        "facts": facts,
        "working_types": working_types,
        "issue_working_map": issue_working_map,
        "diagnostics": {
            "dense_encoder_mode": dense_meta.get("encoder_mode", "unknown"),
            "reducer": reducer_name,
            "clusterer": clusterer_name,
        },
    }


def _run_assignment(runtime, artifacts: dict[str, Any]) -> pd.DataFrame:
    if artifacts["issues"].empty:
        assignments = pd.DataFrame(
            columns=[
                "issue_id",
                "ticket_id",
                "assigned_type_id",
                "type_level",
                "display_name",
                "score",
                "assignment_reason",
                "evidence_text",
            ]
        )
        export_parquet_tables(runtime.run_dir, {"issue_assignments.parquet": assignments})
        return assignments

    canonical_types = load_canonical_store(runtime.project_root)
    assignments = assign_issue_labels(
        issues=artifacts["issues"],
        facts=artifacts["facts"],
        issue_working_map=artifacts["issue_working_map"],
        working_types=artifacts["working_types"],
        canonical_types=canonical_types,
        max_secondary_labels=runtime.max_secondary_labels,
    )
    export_parquet_tables(runtime.run_dir, {"issue_assignments.parquet": assignments})
    return assignments


def _run_reporting(runtime, tickets: pd.DataFrame, artifacts: dict[str, Any], assignments: pd.DataFrame) -> None:
    write_excel_reports(runtime.run_dir, assignments, artifacts["working_types"])
    write_run_summary(
        runtime.run_dir,
        runtime.dataset.display_name,
        runtime.profile.profile_name,
        tickets,
        artifacts["issues"],
        artifacts["working_types"],
        assignments,
        artifacts["diagnostics"],
    )


def _execute_pipeline(dataset: str, profile: str, run_id: str | None, stop_after: str) -> Path:
    runtime = load_runtime_config(get_project_root(), dataset, profile, run_id=run_id)
    console.print(f"[bold cyan]Run ID:[/bold cyan] {runtime.run_id}")
    tickets = _run_ingest(runtime)
    if stop_after == "ingest":
        return runtime.run_dir

    artifacts = _run_discovery(runtime, tickets)
    if stop_after == "discover":
        return runtime.run_dir

    assignments = _run_assignment(runtime, artifacts)
    if stop_after == "assign":
        return runtime.run_dir

    _run_reporting(runtime, tickets, artifacts, assignments)
    return runtime.run_dir


@app.command()
def ingest(
    dataset: str = typer.Option(..., "--dataset"),
    profile: str = typer.Option("cpu", "--profile"),
    run_id: str | None = typer.Option(None, "--run-id"),
) -> None:
    """Run ingest only."""

    run_dir = _execute_pipeline(dataset, profile, run_id, stop_after="ingest")
    console.print(f"[green]Ingest completed[/green]: {run_dir}")


@app.command()
def discover(
    dataset: str = typer.Option(..., "--dataset"),
    profile: str = typer.Option("cpu", "--profile"),
    run_id: str | None = typer.Option(None, "--run-id"),
) -> None:
    """Run through issue discovery."""

    run_dir = _execute_pipeline(dataset, profile, run_id, stop_after="discover")
    console.print(f"[green]Discovery completed[/green]: {run_dir}")


@app.command()
def assign(
    dataset: str = typer.Option(..., "--dataset"),
    profile: str = typer.Option("cpu", "--profile"),
    run_id: str | None = typer.Option(None, "--run-id"),
) -> None:
    """Run through issue assignment."""

    run_dir = _execute_pipeline(dataset, profile, run_id, stop_after="assign")
    console.print(f"[green]Assignment completed[/green]: {run_dir}")


@app.command(name="full-run")
def full_run(
    dataset: str = typer.Option(..., "--dataset"),
    profile: str = typer.Option("cpu", "--profile"),
    run_id: str | None = typer.Option(None, "--run-id"),
) -> None:
    """Run the complete pipeline."""

    run_dir = _execute_pipeline(dataset, profile, run_id, stop_after="report")
    console.print(f"[green]Full pipeline completed[/green]: {run_dir}")


@app.command()
def report(
    dataset: str = typer.Option(..., "--dataset"),
    profile: str = typer.Option("cpu", "--profile"),
    run_id: str | None = typer.Option(None, "--run-id"),
) -> None:
    """Alias for a full run that produces reports."""

    run_dir = _execute_pipeline(dataset, profile, run_id, stop_after="report")
    console.print(f"[green]Reports created[/green]: {run_dir}")


@app.command()
def promote(
    dataset: str = typer.Option(..., "--dataset"),
    mapping_file: Path = typer.Option(..., "--mapping-file"),
) -> None:
    """Promote reviewed working types into canonical types."""

    _ = dataset
    canonical = promote_working_types(get_project_root(), mapping_file)
    console.print(f"[green]Canonical types updated[/green]: {len(canonical)} rows")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
