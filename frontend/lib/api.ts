import type { DeliberateResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function deliberate(problem: string): Promise<DeliberateResponse> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}/api/council/deliberate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ problem }),
    });
  } catch {
    throw new Error(
      `Can't reach the POLIS backend at ${API_BASE_URL}. Make sure it's running (see README.md#installation).`
    );
  }

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Council request failed (${res.status}): ${detail}`);
  }

  return res.json();
}
