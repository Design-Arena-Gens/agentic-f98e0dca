FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY insight_agent /app/insight_agent

RUN pip install --upgrade pip && \
    pip install -e .[dev]

EXPOSE 8000

CMD ["uvicorn", "insight_agent.server.api:app", "--host", "0.0.0.0", "--port", "8000"]
