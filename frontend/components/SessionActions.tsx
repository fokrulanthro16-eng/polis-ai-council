"use client";

import { useState } from "react";
import type { DeliberateResponse } from "@/lib/types";

function downloadJson(data: unknown, filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export default function SessionActions({ result }: { result: DeliberateResponse }) {
  const [copied, setCopied] = useState(false);

  function handleExport() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    downloadJson(result, `polis-session-${timestamp}.json`);
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(result.consensus.final_recommendation);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      // Clipboard access can be denied by the browser; the button simply
      // won't show the "Copied" confirmation in that case.
    }
  }

  return (
    <div className="session-actions">
      <button type="button" className="secondary-btn" onClick={handleExport}>
        Export Session JSON
      </button>
      <button type="button" className="secondary-btn" onClick={handleCopy}>
        {copied ? "Copied!" : "Copy Final Decision"}
      </button>
    </div>
  );
}
