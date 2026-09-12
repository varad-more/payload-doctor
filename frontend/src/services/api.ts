import type { AnalyzeRequest, AnalyzeResult } from "../types/api";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "");

export async function analyzePayload(request: AnalyzeRequest): Promise<AnalyzeResult> {
  if (!API_BASE_URL) {
    throw new Error("API URL is not configured. Set VITE_API_BASE_URL and restart the frontend.");
  }

  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 12_000);
  try {
    let response: Response;
    try {
      response = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(request),
        signal: controller.signal,
      });
    } catch (error) {
      if (error instanceof DOMException && error.name === "AbortError") {
        throw new Error("Analysis timed out. Try again with a smaller payload.");
      }
      throw new Error("Unable to analyze payload. Please try again.");
    }

    let result: AnalyzeResult;
    try {
      result = (await response.json()) as AnalyzeResult;
    } catch {
      throw new Error("The analysis service returned an unexpected response. Please try again.");
    }
    if (!result || typeof result.success !== "boolean") {
      throw new Error("The analysis service returned an unexpected response. Please try again.");
    }
    return result;
  } finally {
    window.clearTimeout(timeout);
  }
}
