from __future__ import annotations

from typing import Any, Dict, TypedDict

import pandas as pd
from langgraph.graph import END, StateGraph

from .agents.column_resolver import ColumnResolver
from .agents.metrics_agent import MetricsAgent
from .agents.recommendation_agent import RecommendationAgent
from .schemas import (
    InsightAgentConfig,
    InsightAgentRequest,
    InsightAgentResponse,
    ResolvedContext,
)


class WorkflowState(TypedDict, total=False):
    request: InsightAgentRequest
    config: InsightAgentConfig
    frame: pd.DataFrame
    resolved_context: ResolvedContext
    metrics_snapshot: Dict[str, Any]
    insights: Any
    response: InsightAgentResponse


def build_graph() -> StateGraph[WorkflowState]:
    workflow = StateGraph(WorkflowState)

    def node_load_input(state: WorkflowState) -> WorkflowState:
        frame = pd.DataFrame(state["request"].records)
        state["frame"] = frame
        return state

    def node_resolve_columns(state: WorkflowState) -> WorkflowState:
        resolver = ColumnResolver(
            semantic_threshold=state["config"].semantic_column_threshold,
            manual_overrides=state["request"].manual_column_overrides,
        )

        result = resolver.resolve(state["frame"].columns)

        normalized_rows = state["frame"].to_dict(orient="records")
        state["resolved_context"] = ResolvedContext(
            column_mapping=result.mapping,
            normalized_rows=normalized_rows,
            failed_columns=result.failed,
        )
        return state

    def node_metrics(state: WorkflowState) -> WorkflowState:
        mapping = state["resolved_context"].column_mapping
        agent = MetricsAgent(mapping=mapping)
        metrics_result = agent.run(state["frame"])
        state["metrics_snapshot"] = metrics_result.summary

        entity_frame = metrics_result.entity_metrics.rename(
            columns={
                mapping.campaign_name or "": "campaign",
                mapping.adset_name or "": "adset",
                mapping.ad_name or "": "ad",
                mapping.ad_id or "": "ad_id",
            }
        )
        state["frame"] = entity_frame
        return state

    def node_recommendations(state: WorkflowState) -> WorkflowState:
        agent = RecommendationAgent()
        state["insights"] = agent.run(state["frame"])
        return state

    def node_finalize(state: WorkflowState) -> WorkflowState:
        response = InsightAgentResponse(
            request=state["request"],
            config=state["config"],
            resolved_context=state["resolved_context"],
            insights=state["insights"],
            metrics_snapshot=state["metrics_snapshot"],
        )
        next_state: WorkflowState = {
            **state,
            "response": response,
        }
        return next_state

    workflow.add_node("load_input", node_load_input)
    workflow.add_node("resolve_columns", node_resolve_columns)
    workflow.add_node("metrics", node_metrics)
    workflow.add_node("recommendations", node_recommendations)
    workflow.add_node("finalize", node_finalize)

    workflow.set_entry_point("load_input")
    workflow.add_edge("load_input", "resolve_columns")
    workflow.add_edge("resolve_columns", "metrics")
    workflow.add_edge("metrics", "recommendations")
    workflow.add_edge("recommendations", "finalize")
    workflow.add_edge("finalize", END)

    return workflow
