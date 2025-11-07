from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd

from ..schemas import ColumnMapping


@dataclass
class MetricsResult:
    summary: Dict[str, float]
    entity_metrics: pd.DataFrame


class MetricsAgent:
    """Derive key marketing metrics ready for downstream insight agents."""

    def __init__(self, mapping: ColumnMapping) -> None:
        self.mapping = mapping

    def run(self, frame: pd.DataFrame) -> MetricsResult:
        df = frame.copy()

        def safe_cast(column: Optional[str]) -> Optional[pd.Series]:
            if column is None:
                return None
            return pd.to_numeric(df[column], errors="coerce")

        spends = safe_cast(self.mapping.spend)
        impressions = safe_cast(self.mapping.impressions)
        clicks = safe_cast(self.mapping.clicks)

        df["__spend"] = spends if spends is not None else 0.0
        df["__impressions"] = impressions if impressions is not None else 0.0
        df["__clicks"] = clicks if clicks is not None else 0.0
        df["__ctr"] = df["__clicks"] / df["__impressions"].replace(0, pd.NA)

        purchases = safe_cast(self.mapping.purchases)
        purchase_value = safe_cast(self.mapping.purchase_value)
        adds_to_cart = safe_cast(self.mapping.adds_to_cart)

        df["__purchases"] = purchases if purchases is not None else 0.0
        df["__purchase_value"] = purchase_value if purchase_value is not None else 0.0
        df["__adds_to_cart"] = adds_to_cart if adds_to_cart is not None else 0.0

        df["__roas"] = df["__purchase_value"] / df["__spend"].replace(0, pd.NA)
        df["__atc_to_purchase"] = df["__purchases"] / df["__adds_to_cart"].replace(
            0, pd.NA
        )
        df["__ctr_7d"] = (
            pd.to_numeric(df[self.mapping.ctr_7d], errors="coerce")
            if self.mapping.ctr_7d
            else pd.NA
        )
        df["__ctr_prev_7d"] = (
            pd.to_numeric(df[self.mapping.ctr_prev_7d], errors="coerce")
            if self.mapping.ctr_prev_7d
            else pd.NA
        )

        agg = df[
            [
                "__spend",
                "__impressions",
                "__clicks",
                "__purchases",
                "__purchase_value",
                "__adds_to_cart",
            ]
        ].sum(numeric_only=True)

        summary: Dict[str, float] = {
            "spend": float(agg["__spend"]),
            "impressions": float(agg["__impressions"]),
            "clicks": float(agg["__clicks"]),
            "purchases": float(agg["__purchases"]),
            "purchase_value": float(agg["__purchase_value"]),
            "adds_to_cart": float(agg["__adds_to_cart"]),
        }

        summary["ctr"] = (
            summary["clicks"] / summary["impressions"]
            if summary["impressions"]
            else 0.0
        )
        summary["roas"] = (
            summary["purchase_value"] / summary["spend"] if summary["spend"] else 0.0
        )
        summary["atc_to_purchase"] = (
            summary["purchases"] / summary["adds_to_cart"]
            if summary["adds_to_cart"]
            else 0.0
        )

        entity_columns: List[str] = [
            column
            for column in [
                self.mapping.campaign_name,
                self.mapping.adset_name,
                self.mapping.ad_name,
                self.mapping.ad_id,
            ]
            if column
        ]

        entity_frame = df[
            entity_columns
            + [
                "__spend",
                "__impressions",
                "__clicks",
                "__roas",
                "__purchases",
                "__purchase_value",
                "__adds_to_cart",
                "__atc_to_purchase",
                "__ctr",
                "__ctr_7d",
                "__ctr_prev_7d",
            ]
        ].copy()

        return MetricsResult(summary=summary, entity_metrics=entity_frame)

