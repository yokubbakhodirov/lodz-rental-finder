"use client";

import { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import type { ScoredListing } from "../lib/types";
import { TIER_HEX, TIER_LABEL, TIER_ORDER } from "../lib/tiers";

interface Props {
  results: ScoredListing[];
}

const PRICE_BUCKET_SIZE = 250;

export default function AnalyticsDashboard({ results }: Props) {
  const priceHistogram = useMemo(() => {
    const buckets = new Map<number, number>();
    for (const r of results) {
      const total = r.priceMonthlyPln + r.rentExtraPln;
      const bucket = Math.floor(total / PRICE_BUCKET_SIZE) * PRICE_BUCKET_SIZE;
      buckets.set(bucket, (buckets.get(bucket) ?? 0) + 1);
    }
    return Array.from(buckets.entries())
      .sort((a, b) => a[0] - b[0])
      .map(([bucket, count]) => ({
        label: `${bucket}-${bucket + PRICE_BUCKET_SIZE}`,
        count,
      }));
  }, [results]);

  const scatterByTier = useMemo(() => {
    const groups: Record<ScoredListing["tier"], { price: number; score: number }[]> = {
      premium: [],
      good: [],
      average: [],
      poor: [],
    };
    for (const r of results) {
      groups[r.tier].push({ price: r.priceMonthlyPln + r.rentExtraPln, score: r.score });
    }
    return groups;
  }, [results]);

  const districtCounts = useMemo(() => {
    const counts = new Map<string, number>();
    for (const r of results) {
      counts.set(r.district, (counts.get(r.district) ?? 0) + 1);
    }
    return Array.from(counts.entries())
      .sort((a, b) => b[1] - a[1])
      .map(([district, count]) => ({ district, count }));
  }, [results]);

  const tierCounts = useMemo(() => {
    const counts: Record<ScoredListing["tier"], number> = { premium: 0, good: 0, average: 0, poor: 0 };
    for (const r of results) counts[r.tier] += 1;
    return (["premium", "good", "average", "poor"] as const)
      .map((tier) => ({ tier, count: counts[tier] }))
      .filter((entry) => entry.count > 0);
  }, [results]);

  if (results.length === 0) {
    return (
      <div className="text-center text-sm text-neutral-400 py-16">
        No listings to analyze yet.
      </div>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">
      <ChartCard title="Price distribution (total monthly, PLN)">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={priceHistogram}>
            <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
            <XAxis dataKey="label" tick={{ fontSize: 11 }} interval={0} angle={-35} textAnchor="end" height={60} />
            <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" fill="#f97316" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Score vs. price by tier">
        <ResponsiveContainer width="100%" height={260}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
            <XAxis
              dataKey="price"
              name="Price"
              unit=" PLN"
              type="number"
              tick={{ fontSize: 11 }}
            />
            <YAxis dataKey="score" name="Score" type="number" domain={[0, 10]} tick={{ fontSize: 11 }} />
            <ZAxis range={[60, 60]} />
            <Tooltip cursor={{ strokeDasharray: "3 3" }} />
            <Legend />
            {TIER_ORDER.map((tier) => (
              <Scatter key={tier} name={TIER_LABEL[tier]} data={scatterByTier[tier]} fill={TIER_HEX[tier]} />
            ))}
          </ScatterChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Listings per district">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={districtCounts} layout="vertical" margin={{ left: 16 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
            <XAxis type="number" tick={{ fontSize: 11 }} allowDecimals={false} />
            <YAxis dataKey="district" type="category" tick={{ fontSize: 11 }} width={90} />
            <Tooltip />
            <Bar dataKey="count" fill="#0ea5e9" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Match quality breakdown">
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie
              data={tierCounts}
              dataKey="count"
              nameKey="tier"
              cx="50%"
              cy="50%"
              outerRadius={90}
              label={(props: any) => `${TIER_LABEL[props.tier as ScoredListing["tier"]]} (${props.count})`}
            >
              {tierCounts.map((entry) => (
                <Cell key={entry.tier} fill={TIER_HEX[entry.tier]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-neutral-200 p-4">
      <h3 className="text-sm font-medium text-neutral-700 mb-2">{title}</h3>
      {children}
    </div>
  );
}
