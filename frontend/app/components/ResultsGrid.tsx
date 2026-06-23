"use client";

import { useMemo, useState } from "react";
import type { FunnelStats, ScoredListing } from "../lib/types";
import { TIER_BG_CLASS, TIER_LABEL, TIER_RANGE } from "../lib/tiers";

interface Props {
  results: ScoredListing[];
  funnel: FunnelStats;
}

const ROOM_LABEL: Record<string, string> = {
  one: "Studio",
  two: "2 rooms",
  three: "3 rooms",
  four: "4+ rooms",
};

const SOURCE_LABEL: Record<ScoredListing["source"], string> = {
  olx: "OLX",
  otodom: "Otodom",
  rentola: "Rentola",
};

const SOURCE_HOST: Record<ScoredListing["source"], string> = {
  olx: "OLX.pl",
  otodom: "Otodom.pl",
  rentola: "Rentola.pl",
};

type FilterKey = "all" | "premium" | "good";

export default function ResultsGrid({ results, funnel }: Props) {
  const [filter, setFilter] = useState<FilterKey>("all");

  const filtered = useMemo(() => {
    if (filter === "all") return results;
    if (filter === "premium") return results.filter((r) => r.tier === "premium");
    return results.filter((r) => r.tier === "premium" || r.tier === "good");
  }, [results, filter]);

  return (
    <div className="w-full max-w-6xl mx-auto">
      <div className="flex items-center gap-2 mb-2 text-sm flex-wrap">
        <FilterPill
          label={`All matches ${results.length}`}
          active={filter === "all"}
          onClick={() => setFilter("all")}
        />
        <FilterPill
          label={`${TIER_LABEL.premium} match ${results.filter((r) => r.tier === "premium").length}`}
          active={filter === "premium"}
          onClick={() => setFilter("premium")}
        />
        <FilterPill
          label={`${TIER_LABEL.premium} + ${TIER_LABEL.good} match ${
            results.filter((r) => r.tier === "premium" || r.tier === "good").length
          }`}
          active={filter === "good"}
          onClick={() => setFilter("good")}
        />
        <span className="ml-auto text-neutral-400 text-xs">
          Scanned {funnel.scanned} → Shortlist {funnel.shortlist}
        </span>
      </div>

      <p className="text-xs text-neutral-400 mb-5">
        Match score (0–10) combines budget fit, room-count fit, district fit, and condition fit. {" "}
        {(Object.keys(TIER_LABEL) as Array<keyof typeof TIER_LABEL>).map((tier, i) => (
          <span key={tier}>
            {i > 0 && " · "}
            <strong className="text-neutral-500">{TIER_LABEL[tier]}</strong> ({TIER_RANGE[tier]})
          </span>
        ))}
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((listing) => (
          <ListingCard key={listing.id} listing={listing} />
        ))}
      </div>
    </div>
  );
}

function FilterPill({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 rounded-full border text-xs font-medium transition-colors ${
        active
          ? "bg-orange-600 text-white border-orange-600"
          : "bg-white text-neutral-600 border-neutral-200 hover:border-orange-300"
      }`}
    >
      {label}
    </button>
  );
}

function ListingCard({ listing }: { listing: ScoredListing }) {
  const totalPrice = listing.priceMonthlyPln + listing.rentExtraPln;
  return (
    <a
      href={listing.url}
      target="_blank"
      rel="noopener noreferrer"
      className="bg-white rounded-xl border border-neutral-200 overflow-hidden hover:shadow-md transition-shadow flex flex-col"
    >
      <div className="relative h-40 bg-neutral-100">
        {listing.photos[0] ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={listing.photos[0]}
            alt={listing.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-neutral-300 text-xs">
            No photo
          </div>
        )}
        <span
          className={`absolute top-2 left-2 ${TIER_BG_CLASS[listing.tier]} text-white text-xs font-semibold px-2 py-0.5 rounded`}
        >
          {TIER_LABEL[listing.tier]} match · {listing.score.toFixed(1)}
        </span>
        <span className="absolute top-2 right-2 bg-white/90 text-neutral-600 text-[10px] font-medium px-2 py-0.5 rounded uppercase tracking-wide">
          {SOURCE_LABEL[listing.source]}
        </span>
      </div>
      <div className="p-3 flex flex-col gap-1 flex-1">
        <div className="font-medium text-sm text-neutral-800 line-clamp-2">{listing.title}</div>
        <div className="text-orange-600 font-semibold">
          {totalPrice.toLocaleString()} PLN/mo
        </div>
        <div className="text-xs text-neutral-500 flex gap-2 flex-wrap">
          <span>{listing.district}</span>
          {listing.rooms && <span>· {ROOM_LABEL[listing.rooms]}</span>}
          {listing.areaM2 && <span>· {listing.areaM2} m²</span>}
        </div>
        <div className="mt-auto pt-2 text-[11px] text-neutral-400">
          View on {SOURCE_HOST[listing.source]} →
        </div>
      </div>
    </a>
  );
}
