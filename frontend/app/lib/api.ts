import type { Job } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

export async function startScan(brief: string): Promise<string> {
  const res = await fetch(`${API_URL}/api/scan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ brief }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error ?? `Scan request failed (${res.status})`);
  }
  const data = await res.json();
  return data.jobId as string;
}

export async function getJob(jobId: string): Promise<Job> {
  const res = await fetch(`${API_URL}/api/scan/${jobId}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Job fetch failed (${res.status})`);
  }
  return res.json();
}
