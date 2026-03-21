"""Pattern-based extraction rules."""

from __future__ import annotations

import regex as re


MONEY_RE = re.compile(r"\d+(?:,\d{3})*(?:\.\d+)?元")
PERCENT_RE = re.compile(r"\d+(?:\.\d+)?%")
CARD_LIKE_RE = re.compile(r"[\p{Han}A-Za-z0-9]+卡")
CONTRACT_RE = re.compile(r"(贷款合同|合同|协议|面签)")
ACTIVITY_RE = re.compile(r"[\p{Han}A-Za-z0-9]+(?:活动|权益|礼包|消费季|Plus)")


def extract_money_mentions(text: str) -> list[str]:
    return MONEY_RE.findall(text)


def extract_rate_mentions(text: str) -> list[str]:
    return PERCENT_RE.findall(text)


def extract_card_mentions(text: str) -> list[str]:
    return CARD_LIKE_RE.findall(text)


def extract_contract_mentions(text: str) -> list[str]:
    return CONTRACT_RE.findall(text)


def extract_activity_mentions(text: str) -> list[str]:
    return ACTIVITY_RE.findall(text)

