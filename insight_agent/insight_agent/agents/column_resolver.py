from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Tuple

import numpy as np

from ..schemas import ColumnMapping


CANONICAL_FIELDS: Dict[str, Tuple[str, ...]] = {
    "spend": ("spend", "amount_spent", "total_spent", "cost"),
    "impressions": ("impressions", "impr"),
    "clicks": ("clicks", "link_clicks", "click_count"),
    "ctr": ("ctr", "click_through_rate"),
    "frequency": ("frequency",),
    "roas": ("roas", "return_on_ad_spend"),
    "purchases": ("purchases", "purchase", "conversions", "results"),
    "purchase_value": ("purchase_value", "purchasevalue", "value", "revenue"),
    "adds_to_cart": ("adds_to_cart", "atc", "addtocart"),
    "ctr_7d": ("ctr_7d", "ctr_7_day", "ctr_7day"),
    "ctr_prev_7d": (
        "ctr_prev_7d",
        "ctr_prior_7d",
        "ctr_previous_7days",
        "ctr_prev_week",
    ),
    "status": ("status", "delivery", "state"),
    "ad_name": ("ad", "ad_name", "creative_name"),
    "ad_id": ("ad_id", "adid", "adset_ad_id"),
    "campaign_name": ("campaign_name", "campaign"),
    "adset_name": ("ad_set_name", "adset_name", "adset"),
}


def _tokenize(value: str) -> List[str]:
    value = value.replace("%", "percent")
    return re.findall(r"[a-z0-9]+", value.lower())


def _similarity_score(candidate: Iterable[str], options: Iterable[str]) -> float:
    candidate_tokens = set()
    for option in candidate:
        candidate_tokens.update(_tokenize(option))

    max_score = 0.0
    for option in options:
        option_tokens = set(_tokenize(option))
        if not option_tokens:
            continue
        overlap = len(candidate_tokens & option_tokens)
        union = len(candidate_tokens | option_tokens)
        score = overlap / union if union else 0.0
        max_score = max(max_score, score)
    return max_score


@dataclass
class ColumnResolutionResult:
    mapping: ColumnMapping
    failed: List[str]


class ColumnResolver:
    """Resolve canonical metrics to dataset columns using fuzzy matching."""

    def __init__(
        self,
        semantic_threshold: float = 0.6,
        manual_overrides: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.semantic_threshold = semantic_threshold
        self.manual_overrides = manual_overrides or {}

    def resolve(self, dataset_columns: Iterable[str]) -> ColumnResolutionResult:
        dataset_columns = list(dataset_columns)
        canonical_to_column: Dict[str, str] = {}
        failed: List[str] = []

        for canonical_key, synonyms in CANONICAL_FIELDS.items():
            if canonical_key in self.manual_overrides:
                canonical_to_column[canonical_key] = self.manual_overrides[canonical_key]
                continue

            scores = np.array(
                [
                    _similarity_score([column], synonyms)
                    for column in dataset_columns
                ]
            )
            if len(scores) == 0:
                failed.append(canonical_key)
                continue

            best_idx = int(np.argmax(scores))
            best_score = float(scores[best_idx])
            if best_score >= self.semantic_threshold:
                canonical_to_column[canonical_key] = dataset_columns[best_idx]
            else:
                failed.append(canonical_key)

        mapping = ColumnMapping(**canonical_to_column)
        return ColumnResolutionResult(mapping=mapping, failed=failed)

