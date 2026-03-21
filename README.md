# 银行投诉审计问题识别工程

这是一个独立于数据清洗工程的 Python 机器学习项目，用于把清洗后的投诉工单自动拆解为 `issue`、自动发现问题簇、生成可下钻到具体工单的审计问题类别，并为后续跨年份、跨地区复用保留扩展接口。

## 项目目标

- 以清洗后的投诉工单为唯一输入，不和原始清洗逻辑耦合。
- 以 `issue` 为最小分析单位，支持一笔工单拆成多个问题单元。
- 自动发现问题簇，不预设固定类别数。
- 同时维护本次运行的 `WorkingType` 和可复用的 `CanonicalType`。
- 输出面向审计的汇总表和下钻表，确保每个分类都能回查具体工单和证据句。

## 目录结构

```text
bank-complaint-audit-issues/
  configs/                运行配置和数据集 manifest
  docs/                   架构、数据契约、运行档位和评审流程
  data/
    external/             正式问题类型库等外部静态数据
    cache/                向量、模型和中间缓存
    runs/                 每次运行的产物目录
  scripts/                便捷执行脚本
  src/audit_issue_engine/ 核心业务代码
  tests/                  smoke test 和模块级测试
```

## 输入数据契约

默认输入来自清洗工程产出的 CSV 或 Excel，必须至少包含以下字段：

- `ticket_id`
- `desc_clean`
- `resolution_cause_clean`
- `biz_type`
- `biz_subtype`

项目已经内置两个示例数据集配置：

- `sample_local`：本仓库内置的小样本，用于 smoke test
- `jl_2024`：指向吉林 2024 清洗结果快照的 GitHub raw 链接

## 安装

推荐使用独立虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

如果后续在更强的 GPU 机器上运行，再额外执行：

```powershell
python -m pip install -r requirements-gpu.txt
```

## CPU / GPU 运行档位

### CPU 基线模式

- 推荐机器：8 核以上 CPU，16GB 内存起步，32GB 更稳
- 默认句向量模型：`moka-ai/m3e-small`
- 允许在句向量、UMAP 或 HDBSCAN 不可用时自动回退到稀疏特征和 sklearn 聚类

### GPU 增强模式

- 推荐机器：12-16 核 CPU，32-64GB 内存，NVIDIA 12GB VRAM 起步
- 默认句向量模型：`BAAI/bge-m3`
- 优先启用本地 dense encoder、UMAP 和 HDBSCAN

## 常用命令

### 1. 只做数据接入

```powershell
audit-issues ingest --dataset jl_2024 --profile cpu
```

### 2. 运行到问题发现

```powershell
audit-issues discover --dataset sample_local --profile cpu
```

### 3. 运行到分类分配

```powershell
audit-issues assign --dataset sample_local --profile cpu
```

### 4. 运行完整流程

```powershell
audit-issues full-run --dataset sample_local --profile cpu
```

### 5. 从工作类提升正式类

```powershell
audit-issues promote --dataset sample_local --mapping-file reviewed_working_types.csv
```

## 输出文件

每次运行会在 `data/runs/{run_id}/` 下生成：

- `tickets.parquet`
- `issues.parquet`
- `term_catalog.parquet`
- `issue_facts.parquet`
- `working_types.parquet`
- `issue_assignments.parquet`
- `category_summary.xlsx`
- `category_drilldown.xlsx`
- `new_type_candidates.xlsx`
- `run_summary.md`
- `run_manifest.json`

## 工程特点

- `src` 目录下只放核心业务逻辑，脚本层只做装配
- 配置和数据集解耦，便于后续扩展到黑龙江或全国数据
- issue 级别分类，天然支持多标签和工单下钻
- 工作类自动发现，正式类逐步沉淀，不要求你先人工看完所有工单

## 常见问题

### 1. 当前机器没有 GPU，还能跑吗？

能。CPU 模式会优先用本地稀疏特征和轻量回退链路，确保工程可运行。

### 2. 为什么要单独建仓？

因为这个工程是独立的机器学习应用，不应该和数据清洗规则混在一个仓库里。这样后续可以独立演进、独立打版本、独立迁移到更强机器。

### 3. 没有正式问题类型库怎么办？

第一版允许 `CanonicalType` 为空，先跑出 `WorkingType`。后续只在问题簇层面做少量人工确认，再沉淀为正式类。

更多细节见：

- [架构文档](./docs/architecture.md)
- [数据契约](./docs/data_contract.md)
- [运行档位](./docs/runtime_profiles.md)
- [评审流程](./docs/review_workflow.md)

