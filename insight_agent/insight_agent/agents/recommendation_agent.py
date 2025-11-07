from __future__ import annotations

from typing import Dict, List

import pandas as pd

from ..schemas import InsightAgentInsight
from ..utils.text import human_join


class RecommendationAgent:
    """Generate actionable optimization guidance from metrics."""

    def __init__(self, minimum_spend: float = 50.0) -> None:
        self.minimum_spend = minimum_spend

    def run(self, frame: pd.DataFrame) -> List[InsightAgentInsight]:
        insights: List[InsightAgentInsight] = []
        working = frame.copy()
        for column in working.columns:
            if column.startswith("__"):
                working[column] = pd.to_numeric(working[column], errors="coerce")
            else:
                working[column] = working[column].fillna("")

        for _, row in working.iterrows():
            spend = float(row["__spend"])
            if spend < self.minimum_spend:
                continue

            roas = float(row["__roas"]) if row["__roas"] == row["__roas"] else 0.0
            ctr = float(row["__ctr"]) if row["__ctr"] == row["__ctr"] else 0.0
            atc_to_purchase = (
                float(row["__atc_to_purchase"])
                if row["__atc_to_purchase"] == row["__atc_to_purchase"]
                else 0.0
            )
            ctr_7d = (
                float(row["__ctr_7d"]) if row["__ctr_7d"] == row["__ctr_7d"] else None
            )
            ctr_prev_7d = (
                float(row["__ctr_prev_7d"])
                if row["__ctr_prev_7d"] == row["__ctr_prev_7d"]
                else None
            )

            entity_parts = [
                str(value)
                for label, value in row.items()
                if label
                in {
                    "campaign",
                    "adset",
                    "ad",
                    "ad_name",
                    "ad_id",
                    "campaign_name",
                    "adset_name",
                }
                and value
            ]
            impacted_entities = [human_join(entity_parts)] if entity_parts else []

            if roas and roas < 1.5:
                recommendation = (
                    "Test 2–3 new hooks or thumbnails, rotate in fresh creative, and cap frequency if delivery is fatigued."
                )
                insights.append(
                    InsightAgentInsight(
                        topic="roas",
                        severity="warning" if roas > 1.0 else "critical",
                        summary=f"ROAS below efficiency guardrail at {roas:.2f}.",
                        recommendation=recommendation,
                        impacted_entities=impacted_entities,
                        supporting_data={"spend": spend, "roas": roas},
                    )
                )

            if ctr >= 0.015 and atc_to_purchase < 0.2:
                insights.append(
                    InsightAgentInsight(
                        topic="conversion",
                        severity="warning",
                        summary="CTR healthy but poor conversion from cart to purchase.",
                        recommendation="Audit landing and checkout flow, watch session recordings, validate funnel tracking.",
                        impacted_entities=impacted_entities,
                        supporting_data={
                            "ctr": ctr,
                            "atc_to_purchase": atc_to_purchase,
                        },
                    )
                )

            if ctr_7d is not None and ctr_prev_7d is not None:
                if ctr_prev_7d and (ctr_prev_7d - ctr_7d) / ctr_prev_7d > 0.25:
                    insights.append(
                        InsightAgentInsight(
                            topic="fatigue",
                            severity="info",
                            summary="CTR dropped >25% vs previous 7 days.",
                            recommendation="Refresh creative variants or rotate in best performers to arrest fatigue.",
                            impacted_entities=impacted_entities,
                            supporting_data={
                                "ctr_7d": ctr_7d,
                                "ctr_prev_7d": ctr_prev_7d,
                            },
                        )
                    )

        if not insights:
            insights.append(
                InsightAgentInsight(
                    topic="meta",
                    severity="info",
                    summary="No critical anomalies detected across evaluated entities.",
                    recommendation="Maintain current optimizations and continue monitoring daily pacing.",
                    supporting_data={},
                )
            )

        return insights
