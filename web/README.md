## InsightAgent Playground

This Next.js app surfaces the capabilities of the InsightAgent engine — a LangGraph + Python orchestrated marketing analysis pipeline — inside a browser-friendly experience.

### Local development

```bash
npm install
npm run dev
# open http://localhost:3000
```

The UI lets you paste CSV exports, inspects the headers that were detected by the Python column resolver, and mirrors the heuristics used by the backend recommendation agents. The UI reads from `public/sample-data.csv` by default so you can test the workflow immediately.

### Deploy

The app is ready for Vercel deployment:

```bash
vercel deploy --prod --yes --token $VERCEL_TOKEN --name agentic-f98e0dca
```

After deployment, verify the production URL with:

```bash
curl https://agentic-f98e0dca.vercel.app
```
