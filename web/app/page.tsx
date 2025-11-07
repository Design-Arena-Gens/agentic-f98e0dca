"use client";

import { useEffect, useMemo, useState } from "react";
import { generateInsights, parseCsv } from "@/lib/insights";

type ViewState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "ready"; insights: ReturnType<typeof generateInsights>["insights"]; metrics: ReturnType<typeof generateInsights>["metrics"] }
  | { kind: "error"; message: string };

const loadSample = async () => {
  const res = await fetch("/sample-data.csv");
  if (!res.ok) {
    throw new Error("Failed to load sample dataset.");
  }
  return res.text();
};

const formatPercent = (value: number) => `${(value * 100).toFixed(1)}%`;

export default function Home() {
  const [rawCsv, setRawCsv] = useState("");
  const [state, setState] = useState<ViewState>({ kind: "idle" });

  const hasDataset = rawCsv.trim().length > 0;

  const parsedHeaders = useMemo(() => {
    if (!hasDataset) return [];
    try {
      return parseCsv(rawCsv).headers;
    } catch {
      return [];
    }
  }, [hasDataset, rawCsv]);

  const runAnalysis = async () => {
    setState({ kind: "loading" });
    try {
      const parsed = parseCsv(rawCsv);
      const { insights, metrics } = generateInsights(parsed.rows);
      setState({ kind: "ready", insights, metrics });
    } catch (error) {
      setState({
        kind: "error",
        message: error instanceof Error ? error.message : "Unexpected error",
      });
    }
  };

  useEffect(() => {
    loadSample()
      .then(setRawCsv)
      .catch(() => {
        setState({
          kind: "error",
          message: "Unable to bootstrap sample dataset.",
        });
      });
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <main className="mx-auto flex max-w-5xl flex-col gap-10 px-6 py-16">
        <section className="rounded-3xl bg-gradient-to-br from-purple-900/60 via-slate-900 to-slate-950 p-10 shadow-2xl ring-1 ring-purple-400/10">
          <div className="flex flex-col gap-4">
            <span className="w-fit rounded-full bg-purple-500/20 px-4 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-purple-200">
              InsightAgent Engine
            </span>
            <h1 className="text-4xl font-semibold tracking-tight md:text-5xl">
              Agentic marketing intelligence built with LangGraph + Python.
            </h1>
            <p className="max-w-2xl text-lg text-slate-200/80">
              Paste paid media exports to generate structured, formula-driven
              recommendations for ROAS lift, conversion repair, and fatigue
              mitigation. This UI wraps the headless engine that can also be
              embedded as a Dockerized FastAPI microservice.
            </p>
            <div className="flex flex-wrap gap-2 text-xs font-medium text-slate-200/70">
              <span className="rounded-full bg-slate-800/80 px-3 py-1">LangGraph orchestrator</span>
              <span className="rounded-full bg-slate-800/80 px-3 py-1">Pydantic v2 IO contracts</span>
              <span className="rounded-full bg-slate-800/80 px-3 py-1">Docker-ready FastAPI</span>
              <span className="rounded-full bg-slate-800/80 px-3 py-1">LLM-pluggable architecture</span>
            </div>
          </div>
        </section>

        <section className="grid gap-8 md:grid-cols-[2fr,1fr]">
          <div className="rounded-2xl bg-slate-900/70 p-6 ring-1 ring-slate-800/80">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Dataset</h2>
              <button
                onClick={runAnalysis}
                className="rounded-full bg-purple-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-purple-500/30 transition hover:bg-purple-400 disabled:cursor-not-allowed disabled:bg-purple-900/40"
                disabled={!hasDataset || state.kind === "loading"}
              >
                {state.kind === "loading" ? "Analyzing…" : "Run analysis"}
              </button>
            </div>
            <p className="mt-2 text-sm text-slate-300/70">
              Paste CSV exports with flexible column naming. The engine resolves
              semantic matches automatically.
            </p>
            <textarea
              className="mt-4 h-72 w-full resize-none rounded-xl border border-slate-800 bg-slate-950/60 p-4 font-mono text-xs text-slate-100 outline-none focus:ring-2 focus:ring-purple-400/60"
              value={rawCsv}
              onChange={(event) => setRawCsv(event.target.value)}
              placeholder="Campaign name,Ad set name,Ad name,Spend,Impressions,Clicks,..."
            />
            {parsedHeaders.length > 0 && (
              <div className="mt-4">
                <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-200/70">
                  Detected headers
                </h3>
                <div className="mt-2 flex flex-wrap gap-2 text-xs">
                  {parsedHeaders.map((header) => (
                    <span
                      key={header}
                      className="rounded-full bg-slate-800/80 px-3 py-1 text-slate-100/80"
                    >
                      {header}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {state.kind === "error" && (
              <p className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                {state.message}
              </p>
            )}
          </div>

          <aside className="flex flex-col gap-4">
            <div className="rounded-2xl bg-slate-900/70 p-6 ring-1 ring-slate-800/80">
              <h2 className="text-lg font-semibold text-slate-100">Quick start</h2>
              <ol className="mt-4 list-decimal space-y-3 pl-5 text-sm text-slate-200/80">
                <li>Clone the repo & install the Python package: <span className="font-mono text-purple-200">pip install -e .</span></li>
                <li>Boot the FastAPI microservice: <span className="font-mono text-purple-200">uvicorn insight_agent.server.api:app</span></li>
                <li>POST to <span className="font-mono text-purple-200">/analyze</span> with your ad-level export.</li>
              </ol>
            </div>

            <div className="rounded-2xl bg-slate-900/70 p-6 ring-1 ring-slate-800/80">
              <h2 className="text-lg font-semibold text-slate-100">Engine Specs</h2>
              <ul className="mt-3 space-y-2 text-sm text-slate-200/70">
                <li>Column resolver with semantic fuzzy matching</li>
                <li>Metrics agent generating ROAS / CTR / funnel ratios</li>
                <li>Heuristic insight layer mirroring production playbooks</li>
                <li>LLM adapter for OpenAI-compatible deployments</li>
              </ul>
            </div>
          </aside>
        </section>

        {state.kind === "ready" && (
          <section className="rounded-2xl bg-slate-900/70 p-8 ring-1 ring-slate-800/80">
            <h2 className="text-2xl font-semibold text-slate-100">Insights</h2>
            <div className="mt-6 grid gap-6 md:grid-cols-2">
              {state.insights.map((insight, index) => (
                <article
                  key={index}
                  className="flex h-full flex-col gap-3 rounded-xl border border-slate-800 bg-slate-950/60 p-5"
                >
                  <div className="flex items-center justify-between text-xs uppercase tracking-wide text-slate-300/60">
                    <span>{insight.topic}</span>
                    <span className="rounded-full bg-purple-500/20 px-3 py-1 text-purple-100">
                      {insight.severity}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-slate-100">
                    {insight.summary}
                  </h3>
                  <p className="text-sm text-slate-300/80">{insight.recommendation}</p>
                  {insight.impactedEntities.length > 0 && (
                    <p className="text-xs font-medium text-slate-400">
                      {insight.impactedEntities.join(", ")}
                    </p>
                  )}
                </article>
              ))}
            </div>

            <div className="mt-10 rounded-xl border border-slate-800 bg-slate-950/40 p-6">
              <h3 className="text-lg font-semibold text-slate-200">Metric snapshot</h3>
              <dl className="mt-4 grid gap-4 text-sm md:grid-cols-3">
                <div>
                  <dt className="text-slate-400">Spend</dt>
                  <dd className="text-slate-100">${state.metrics.spend.toFixed(0)}</dd>
                </div>
                <div>
                  <dt className="text-slate-400">Impressions</dt>
                  <dd className="text-slate-100">
                    {state.metrics.impressions.toLocaleString()}
                  </dd>
                </div>
                <div>
                  <dt className="text-slate-400">Clicks</dt>
                  <dd className="text-slate-100">{state.metrics.clicks.toLocaleString()}</dd>
                </div>
                <div>
                  <dt className="text-slate-400">CTR</dt>
                  <dd className="text-slate-100">{formatPercent(state.metrics.ctr)}</dd>
                </div>
                <div>
                  <dt className="text-slate-400">ROAS</dt>
                  <dd className="text-slate-100">{state.metrics.roas.toFixed(2)}x</dd>
                </div>
                <div>
                  <dt className="text-slate-400">ATC → Purchase</dt>
                  <dd className="text-slate-100">
                    {formatPercent(state.metrics.atcToPurchase)}
                  </dd>
                </div>
              </dl>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
