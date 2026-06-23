"use client";

import type { ScanLogEntry } from "../lib/types";

interface Props {
  log: ScanLogEntry[];
}

export default function ScanProgress({ log }: Props) {
  return (
    <div className="w-full max-w-5xl mx-auto">
      <div className="bg-neutral-900 rounded-2xl p-4 h-80 overflow-y-auto font-mono text-xs text-green-300">
        {log.length === 0 && <div className="text-neutral-500">Connecting to OLX.pl…</div>}
        {log.map((entry, i) => (
          <div key={i} className="flex gap-3 py-0.5">
            <span className="text-neutral-500 shrink-0">
              {new Date(entry.ts).toLocaleTimeString()}
            </span>
            <span className="text-orange-400 shrink-0 w-20">{entry.source}</span>
            <span>{entry.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
