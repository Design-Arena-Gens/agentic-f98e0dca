from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from insight_agent.engine import InsightAgentEngine
from insight_agent.schemas import InsightAgentRequest


def load_sample_records() -> list[dict[str, object]]:
    dataset = Path(__file__).resolve().parents[1] / "data" / "sample_paid_media.csv"
    frame = pd.read_csv(dataset)
    return frame.to_dict(orient="records")


def test_engine_generates_insights(tmp_path: Path) -> None:
    records = load_sample_records()
    request = InsightAgentRequest(dataset_name="sample", data_source="meta_ads", records=records)

    engine = InsightAgentEngine()
    response = engine.analyze(request)

    assert response.metrics_snapshot["spend"] > 0
    assert response.insights, "Expected at least one insight"

    serialized = json.loads(response.model_dump_json())
    output_path = tmp_path / "response.json"
    output_path.write_text(json.dumps(serialized, indent=2))

    assert output_path.exists()


def test_validation_requires_records() -> None:
    with pytest.raises(ValueError):
        InsightAgentRequest(dataset_name="empty", data_source="unknown", records=[])
