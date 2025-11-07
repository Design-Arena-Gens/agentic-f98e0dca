import Papa from "papaparse";
import { z } from "zod";

export const canonicalColumns = [
  "Spend",
  "Impressions",
  "Clicks",
  "CTR %",
  "Frequency",
  "ROAS",
  "Purchases",
  "Purchase value",
  "Adds to cart",
  "CTR 7d %",
  "CTR prev7 %",
] as const;

const Numeric = z
  .string()
  .or(z.number())
  .transform((value) => {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : 0;
  });

const RowSchema = z.object({
  "Campaign name": z.string().optional(),
  "Ad set name": z.string().optional(),
  "Ad name": z.string().optional(),
  "Ad ID": z.string().optional(),
  Spend: Numeric,
  Impressions: Numeric,
  Clicks: Numeric,
  "CTR %": Numeric.optional(),
  Frequency: Numeric.optional(),
  ROAS: Numeric.optional(),
  Purchases: Numeric.optional(),
  "Purchase value": Numeric.optional(),
  "Adds to cart": Numeric.optional(),
  "CTR 7d %": Numeric.optional(),
  "CTR prev7 %": Numeric.optional(),
  Status: z.string().optional(),
});

export type Insight = {
  topic: "roas" | "ctr" | "conversion" | "fatigue" | "status" | "meta";
  severity: "info" | "warning" | "critical";
  summary: string;
  recommendation: string;
  impactedEntities: string[];
  supportingData: Record<string, number>;
};

export type MetricsSnapshot = {
  spend: number;
  impressions: number;
  clicks: number;
  ctr: number;
  roas: number;
  purchases: number;
  purchaseValue: number;
  addsToCart: number;
  atcToPurchase: number;
};

export type ParsedDataset = {
  headers: string[];
  rows: z.infer<typeof RowSchema>[];
};

export function parseCsv(text: string): ParsedDataset {
  const parsed = Papa.parse<Record<string, string>>(text.trim(), {
    header: true,
    skipEmptyLines: true,
  });

  if (parsed.errors.length) {
    throw new Error(parsed.errors[0].message);
  }

  const rows = parsed.data.map((row) => RowSchema.parse(row));
  const headers = (parsed.meta.fields ?? []).filter(Boolean) as string[];

  return { headers, rows };
}

const joinEntities = (row: z.infer<typeof RowSchema>) => {
  const pieces = (
    [
      row["Campaign name"],
      row["Ad set name"],
      row["Ad name"],
      row["Ad ID"],
    ] as (string | undefined)[]
  ).filter((value): value is string => Boolean(value));
  if (!pieces.length) return [];
  if (pieces.length === 1) return pieces;
  return [pieces.slice(0, -1).join(", ") + ` & ${pieces.at(-1)}`];
};

const sum = (values: number[]) => values.reduce((acc, val) => acc + val, 0);

export function generateInsights(rows: z.infer<typeof RowSchema>[]) {
  const totalSpend = sum(rows.map((row) => row.Spend));
  const totalImpressions = sum(rows.map((row) => row.Impressions));
  const totalClicks = sum(rows.map((row) => row.Clicks));
  const totalPurchases = sum(rows.map((row) => row.Purchases ?? 0));
  const totalPurchaseValue = sum(rows.map((row) => row["Purchase value"] ?? 0));
  const totalAtc = sum(rows.map((row) => row["Adds to cart"] ?? 0));

  const metrics: MetricsSnapshot = {
    spend: totalSpend,
    impressions: totalImpressions,
    clicks: totalClicks,
    ctr: totalImpressions ? totalClicks / totalImpressions : 0,
    roas: totalSpend ? totalPurchaseValue / totalSpend : 0,
    purchases: totalPurchases,
    purchaseValue: totalPurchaseValue,
    addsToCart: totalAtc,
    atcToPurchase: totalAtc ? totalPurchases / totalAtc : 0,
  };

  const insights: Insight[] = [];

  rows.forEach((row) => {
    if (row.Spend < 50) {
      return;
    }

    const impactedEntities = joinEntities(row);
    const roas = Number(row.ROAS ?? (row["Purchase value"] ?? 0) / row.Spend);
    const ctr = Number(row["CTR %"] ?? row.Clicks / Math.max(row.Impressions, 1));
    const atcToPurchase = Number(
      (row.Purchases ?? 0) / Math.max(row["Adds to cart"] ?? 0, 1),
    );

    if (Number.isFinite(roas) && roas < 1.5) {
      insights.push({
        topic: "roas",
        severity: roas > 1 ? "warning" : "critical",
        summary: `ROAS is below efficiency guardrail at ${roas.toFixed(2)}.`,
        recommendation:
          "Test 2–3 new hooks/thumbnails, rotate in new ad creative, and cap frequency.",
        impactedEntities,
        supportingData: { spend: row.Spend, roas },
      });
    }

    if (ctr >= 0.015 && atcToPurchase < 0.2) {
      insights.push({
        topic: "conversion",
        severity: "warning",
        summary:
          "CTR is healthy but conversion from adds-to-cart to purchase is under 20%.",
        recommendation:
          "Audit landing/checkout, review tracking, and consider CRO experimentation.",
        impactedEntities,
        supportingData: { ctr, atcToPurchase },
      });
    }

    const ctr7d = row["CTR 7d %"];
    const ctrPrev7 = row["CTR prev7 %"];
    if (ctr7d && ctrPrev7 && ctrPrev7 > 0) {
      const drop = (ctrPrev7 - ctr7d) / ctrPrev7;
      if (drop > 0.25) {
        insights.push({
          topic: "fatigue",
          severity: "info",
          summary: "CTR dropped >25% vs previous 7 days.",
          recommendation:
            "Rotate fatigued creatives, refresh best hooks, and rebuild warm audiences.",
          impactedEntities,
          supportingData: { ctr7d, ctrPrev7, drop },
        });
      }
    }
  });

  if (!insights.length) {
    insights.push({
      topic: "meta",
      severity: "info",
      summary: "No critical anomalies detected across paid media rows.",
      recommendation: "Maintain pacing, continue monitoring ROAS and funnel KPIs.",
      impactedEntities: [],
      supportingData: {},
    });
  }

  return { insights, metrics };
}
