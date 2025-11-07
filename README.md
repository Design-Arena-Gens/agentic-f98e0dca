# InsightAgent Platform

InsightAgent couples a Python LangGraph engine with a Next.js control surface to deliver turnkey marketing intelligence. The Python package can run headless as an embeddable library or inside a Dockerized FastAPI microservice, while the web UI showcases the workflow for analysts.

## Structure

```
.
├── insight_agent/        # Python package (LangGraph orchestration + FastAPI)
├── web/                  # Next.js playground deployable to Vercel
└── README.md             # You are here
```

## Python engine

```bash
cd insight_agent
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
uvicorn insight_agent.server.api:app --reload
```

Send ad-level rows to `POST /analyze` with the schema defined in `insight_agent/schemas.py`. The engine resolves column semantics, runs formula-based heuristics, and returns structured JSON insights.

## Next.js playground

```bash
cd web
npm install
npm run dev
# open http://localhost:3000
```

Deploy straight to Vercel once validated locally:

```bash
vercel deploy --prod --yes --token $VERCEL_TOKEN --name agentic-f98e0dca
curl https://agentic-f98e0dca.vercel.app
```

## Docker

```bash
cd insight_agent
docker build -t insight-agent-engine .
docker run -p 8000:8000 insight-agent-engine
```

The container exposes the FastAPI service at `http://localhost:8000/analyze`.
