# InsightAgent Engine

InsightAgent is a headless Python engine that transforms raw paid media performance exports into actionable optimization guidance. The engine is designed for embedding inside other applications or deploying as a microservice.

## Highlights

- **Semantic column detection** – flexible resolution of differently named data exports (e.g. `ad_name` vs `Ad name`).
- **Agentic orchestration** – a LangGraph-powered workflow coordinates specialist analysis agents for ROAS, CTR, conversion funnels, and fatigue detection.
- **Schema-first contracts** – Pydantic v2 models enforce structured IO for deterministic downstream consumption.
- **LLM-pluggable** – use OpenAI-compatible chat models via a lightweight adapter layer or provide a mock model for deterministic testing.
- **Docker-ready** – packaged FastAPI app exposes the engine as a REST service.

## Quick Start

```bash
cd insight_agent
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
uvicorn insight_agent.server.api:app --reload
```

## License

MIT
