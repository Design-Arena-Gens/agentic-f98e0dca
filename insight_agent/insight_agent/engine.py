from __future__ import annotations

from typing import Any, Dict, Optional

from .graph import WorkflowState, build_graph
from .schemas import InsightAgentConfig, InsightAgentRequest, InsightAgentResponse


class InsightAgentEngine:
    """High-level façade orchestrating the InsightAgent workflow."""

    def __init__(self, config: Optional[InsightAgentConfig] = None) -> None:
        self.config = config or InsightAgentConfig()
        self._graph: Any = self._compile_graph()

    def _compile_graph(self):
        workflow = build_graph()
        return workflow.compile()

    def analyze(
        self, request: InsightAgentRequest, runtime_overrides: Optional[Dict[str, Any]] = None
    ) -> InsightAgentResponse:
        config = self.config.model_copy(update=runtime_overrides or {})

        initial_state: WorkflowState = {
            "request": request,
            "config": config,
        }

        result_state = self._graph.invoke(initial_state)
        response = result_state["response"]
        return response
