"use client";

import { useState } from "react";
import DemoModeBadge from "@/components/DemoModeBadge";
import Hero from "@/components/Hero";
import CouncilProcess from "@/components/CouncilProcess";
import ScenarioPicker from "@/components/ScenarioPicker";
import ProblemInput from "@/components/ProblemInput";
import AgentCard from "@/components/AgentCard";
import DebateTimeline from "@/components/DebateTimeline";
import ConsensusPanel from "@/components/ConsensusPanel";
import CouncilMetrics from "@/components/CouncilMetrics";
import SessionActions from "@/components/SessionActions";
import LoadingSkeleton from "@/components/LoadingSkeleton";
import { deliberate } from "@/lib/api";
import { DEFAULT_PROBLEM } from "@/lib/scenarios";
import type { DeliberateResponse } from "@/lib/types";
import type { CouncilStage } from "@/components/CouncilProcess";

export default function Home() {
  const [problem, setProblem] = useState(DEFAULT_PROBLEM);
  const [scenarioId, setScenarioId] = useState<string | null>(null);
  const [result, setResult] = useState<DeliberateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const stage: CouncilStage = loading ? "loading" : result ? "done" : "idle";

  function handleSelectScenario(scenarioProblem: string, id: string) {
    setProblem(scenarioProblem);
    setScenarioId(id);
    setResult(null);
    setError(null);
    document.getElementById("problem-input")?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function handleChangeProblem(value: string) {
    setProblem(value);
    setScenarioId(null);
  }

  async function handleRunCouncil() {
    const trimmed = problem.trim();
    if (trimmed.length < 3 || loading) return;
    setLoading(true);
    setError(null);
    try {
      const response = await deliberate(trimmed);
      setResult(response);
    } catch (err) {
      setResult(null);
      setError(err instanceof Error ? err.message : "Something went wrong talking to the council.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <DemoModeBadge />

      <Hero />

      <CouncilProcess stage={stage} />

      <ScenarioPicker selectedId={scenarioId} onSelect={handleSelectScenario} disabled={loading} />

      <ProblemInput value={problem} onChange={handleChangeProblem} onSubmit={handleRunCouncil} loading={loading} />

      {error && (
        <div className="error-banner">
          <strong>Council unavailable.</strong> {error}
        </div>
      )}

      {!result && !loading && !error && (
        <p className="empty-state">
          A sample decision is already loaded above — pick a scenario, edit it, or write your own, then run the
          council to see agents debate and reach consensus.
        </p>
      )}

      {loading && (
        <section className="block">
          <h2>Agent Perspectives</h2>
          <LoadingSkeleton />
        </section>
      )}

      {result && !loading && (
        <>
          <section className="block">
            <h2>Agent Perspectives</h2>
            <div className="agent-grid">
              {result.agents.map((agent) => (
                <AgentCard key={agent.role} agent={agent} />
              ))}
            </div>
          </section>

          <section className="block">
            <h2>Debate Timeline</h2>
            <DebateTimeline timeline={result.timeline} />
          </section>

          <section className="block">
            <h2>Council Metrics</h2>
            <CouncilMetrics metrics={result.metrics} />
          </section>

          <section className="block">
            <h2>Consensus</h2>
            <ConsensusPanel consensus={result.consensus} />
            <SessionActions result={result} />
          </section>
        </>
      )}
    </main>
  );
}
