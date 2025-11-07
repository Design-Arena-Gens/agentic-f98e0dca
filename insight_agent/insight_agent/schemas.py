from __future__ import annotations

from typing import Dict, List, Literal, Optional, Sequence

from pydantic import BaseModel, Field, model_validator


class InsightAgentConfig(BaseModel):
    """Runtime configuration options for the engine."""

    llm_provider: Literal["openai", "azure_openai", "mock"] = "mock"
    llm_model: str = "gpt-4o-mini"
    temperature: float = 0.0
    top_p: float = 1.0
    max_tokens: int = 1024
    semantic_column_threshold: float = 0.6


class InsightAgentRequest(BaseModel):
    """Input payload containing the marketing performance dataset."""

    dataset_name: str = Field(..., description="Human-friendly label for the dataset.")
    data_source: Literal["meta_ads", "tiktok_ads", "google_ads", "unknown"] = "unknown"
    records: Sequence[Dict[str, object]] = Field(
        ..., description="Flat list of ad-level performance rows."
    )
    manual_column_overrides: Optional[Dict[str, str]] = Field(
        None,
        description="Optional mapping of canonical column names to dataset column names.",
    )

    @model_validator(mode="after")
    def _ensure_records(self):
        if not self.records:
            msg = "InsightAgentRequest.records must contain at least one row."
            raise ValueError(msg)
        return self


class ColumnMapping(BaseModel):
    """Resolved column mapping from canonical field to dataset field."""

    spend: str
    impressions: str
    clicks: str
    ctr: Optional[str] = None
    frequency: Optional[str] = None
    roas: Optional[str] = None
    purchases: Optional[str] = None
    purchase_value: Optional[str] = None
    adds_to_cart: Optional[str] = None
    ctr_7d: Optional[str] = None
    ctr_prev_7d: Optional[str] = None
    status: Optional[str] = None
    ad_name: Optional[str] = None
    ad_id: Optional[str] = None
    campaign_name: Optional[str] = None
    adset_name: Optional[str] = None


class ResolvedContext(BaseModel):
    column_mapping: ColumnMapping
    normalized_rows: List[Dict[str, object]]
    failed_columns: List[str] = Field(default_factory=list)


class InsightAgentInsight(BaseModel):
    topic: Literal[
        "roas",
        "ctr",
        "conversion",
        "fatigue",
        "status",
        "anomaly",
        "meta",
    ]
    severity: Literal["info", "warning", "critical"]
    summary: str
    recommendation: str
    impacted_entities: List[str] = Field(
        default_factory=list, description="Human-friendly identifiers (ads, ad sets...)."
    )
    supporting_data: Dict[str, object] = Field(default_factory=dict)


class InsightAgentResponse(BaseModel):
    request: InsightAgentRequest
    config: InsightAgentConfig
    resolved_context: ResolvedContext
    insights: List[InsightAgentInsight]
    metrics_snapshot: Dict[str, object]

