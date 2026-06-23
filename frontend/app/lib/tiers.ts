import type { ScoredListing } from "./types";

export const TIER_LABEL: Record<ScoredListing["tier"], string> = {
  premium: "Excellent",
  good: "Good",
  average: "Fair",
  poor: "Weak",
};

export const TIER_RANGE: Record<ScoredListing["tier"], string> = {
  premium: "score ≥ 8.5",
  good: "score 7–8.5",
  average: "score 5.5–7",
  poor: "score < 5.5",
};

export const TIER_BG_CLASS: Record<ScoredListing["tier"], string> = {
  premium: "bg-emerald-600",
  good: "bg-orange-500",
  average: "bg-amber-500",
  poor: "bg-neutral-400",
};

export const TIER_HEX: Record<ScoredListing["tier"], string> = {
  premium: "#059669",
  good: "#f97316",
  average: "#f59e0b",
  poor: "#a3a3a3",
};

export const TIER_ORDER: ScoredListing["tier"][] = ["premium", "good", "average", "poor"];
