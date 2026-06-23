export interface ScoreBreakdown {
  budgetFit: number;
  roomFit: number;
  districtFit: number;
  renovationFit: number;
}

export type ListingSource = "olx" | "otodom" | "rentola";

export interface ScoredListing {
  source: ListingSource;
  id: number;
  title: string;
  description: string;
  priceMonthlyPln: number;
  rentExtraPln: number;
  areaM2: number | null;
  rooms: "one" | "two" | "three" | "four" | null;
  floor: string | null;
  furnished: boolean | null;
  district: string;
  lat: number | null;
  lon: number | null;
  photos: string[];
  url: string;
  createdTime: string;
  score: number;
  scoreBreakdown: ScoreBreakdown;
  tier: "premium" | "good" | "average" | "poor";
}

export interface FunnelStats {
  scanned: number;
  matched: number;
  deduped: number;
  shortlist: number;
}

export interface ScanLogEntry {
  ts: number;
  source: string;
  message: string;
}

export interface Brief {
  rawText: string;
  budgetPln: number | null;
  rooms: number | null;
  districts: string[];
  wantsRenovated: boolean;
}

export type JobStatus = "scanning" | "done" | "error";

export interface Job {
  id: string;
  status: JobStatus;
  brief: Brief;
  log: ScanLogEntry[];
  funnel: FunnelStats;
  results: ScoredListing[];
  error?: string;
}
