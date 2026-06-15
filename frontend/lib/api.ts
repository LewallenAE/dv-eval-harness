import { DVCase, IngestResponse, Trajectory } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error ${response.status}: ${errorText || response.statusText}`);
  }
  return response.json();
}

export async function fetchCases(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/cases`);
  return handleResponse<string[]>(response);
}

export async function runCase(caseId: string): Promise<Trajectory> {
  const response = await fetch(`${API_BASE_URL}/run-case/${caseId}`, {
    method: "POST",
  });
  return handleResponse<Trajectory>(response);
}

export async function runCaseJson(caseData: DVCase): Promise<Trajectory> {
  const response = await fetch(`${API_BASE_URL}/run-case-json`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(caseData),
  });
  return handleResponse<Trajectory>(response);
}

export async function ingestCase(raw: Record<string, unknown>): Promise<IngestResponse> {
  const response = await fetch(`${API_BASE_URL}/ingest-case`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(raw),
  });
  return handleResponse<IngestResponse>(response);
}

export async function fetchTraces(): Promise<Trajectory[]> {
  const response = await fetch(`${API_BASE_URL}/traces`);
  return handleResponse<Trajectory[]>(response);
}

export async function fetchHealth(): Promise<{ status: string; service: string }> {
  const response = await fetch(`${API_BASE_URL}/`);
  return handleResponse<{ status: string; service: string }>(response);
}
