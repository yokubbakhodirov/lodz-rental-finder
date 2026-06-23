"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import BriefForm, { EXAMPLE_BRIEF } from "./components/BriefForm";
import ScanProgress from "./components/ScanProgress";
import ResultsGrid from "./components/ResultsGrid";
import AnalyticsDashboard from "./components/AnalyticsDashboard";
import { getJob, startScan } from "./lib/api";
import type { Job } from "./lib/types";

type Screen = "brief" | "scanning" | "done" | "error";
type ResultsTab = "results" | "analytics";

export default function Home() {
  const [screen, setScreen] = useState<Screen>("brief");
  const [job, setJob] = useState<Job | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [resultsTab, setResultsTab] = useState<ResultsTab>("results");
  const [briefText, setBriefText] = useState(EXAMPLE_BRIEF);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  useEffect(() => stopPolling, [stopPolling]);

  const handleSubmit = async (brief: string) => {
    setErrorMessage(null);
    setScreen("scanning");
    try {
      const jobId = await startScan(brief);
      pollRef.current = setInterval(async () => {
        try {
          const latest = await getJob(jobId);
          setJob(latest);
          if (latest.status === "done") {
            stopPolling();
            setScreen("done");
          } else if (latest.status === "error") {
            stopPolling();
            setErrorMessage(latest.error ?? "Scan failed");
            setScreen("error");
          }
        } catch (err) {
          stopPolling();
          setErrorMessage(err instanceof Error ? err.message : "Connection lost");
          setScreen("error");
        }
      }, 1200);
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Failed to start scan");
      setScreen("error");
    }
  };

  const handleReset = () => {
    stopPolling();
    setJob(null);
    setErrorMessage(null);
    setResultsTab("results");
    setScreen("brief");
  };

  return (
    <main className="min-h-screen bg-[#fdf8f2] py-12 px-4">
      <header className="text-center mb-10">
        <h1 className="text-2xl font-semibold text-neutral-800">Łódź Rental Finder</h1>
        <p className="text-sm text-neutral-400">Łódź · v0.1 · live listings from OLX.pl, Otodom.pl &amp; Rentola.pl, scored for you</p>
      </header>

      {screen === "brief" && (
        <BriefForm
          text={briefText}
          onChange={setBriefText}
          onSubmit={handleSubmit}
          disabled={false}
        />
      )}

      {screen === "scanning" && (
        <div className="space-y-6">
          <div className="text-center text-sm text-neutral-500">
            Scanning OLX.pl, Otodom.pl &amp; Rentola.pl Łódź rentals — this takes about 10-20 seconds…
          </div>
          <ScanProgress log={job?.log ?? []} />
        </div>
      )}

      {screen === "error" && (
        <div className="max-w-xl mx-auto text-center">
          <p className="text-red-600 mb-4">{errorMessage}</p>
          <button onClick={handleReset} className="bg-orange-600 text-white px-5 py-2 rounded-xl">
            Try again
          </button>
        </div>
      )}

      {screen === "done" && job && (
        <div className="space-y-6">
          <div className="flex items-center justify-center gap-4">
            <button onClick={handleReset} className="text-sm text-orange-600 underline">
              ← New search
            </button>
            <div className="flex gap-1 bg-neutral-100 rounded-full p-1">
              <TabButton
                label="Results"
                active={resultsTab === "results"}
                onClick={() => setResultsTab("results")}
              />
              <TabButton
                label="Analytics"
                active={resultsTab === "analytics"}
                onClick={() => setResultsTab("analytics")}
              />
            </div>
          </div>
          {resultsTab === "results" && <ResultsGrid results={job.results} funnel={job.funnel} />}
          {resultsTab === "analytics" && <AnalyticsDashboard results={job.results} />}
        </div>
      )}
    </main>
  );
}

function TabButton({
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
      className={`px-4 py-1.5 rounded-full text-xs font-medium transition-colors ${
        active ? "bg-white text-neutral-800 shadow-sm" : "text-neutral-500 hover:text-neutral-700"
      }`}
    >
      {label}
    </button>
  );
}
