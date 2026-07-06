export type CouncilStage = "idle" | "loading" | "done";

const STEPS = ["Problem", "Agents", "Debate", "Consensus", "Decision"];

// Which step index is "active" (pulsing) for a given stage, and how many
// preceding steps count as already complete.
const STAGE_PROGRESS: Record<CouncilStage, { complete: number; active: number[] }> = {
  idle: { complete: 0, active: [0] },
  loading: { complete: 1, active: [1, 2] },
  done: { complete: 5, active: [] },
};

export default function CouncilProcess({ stage }: { stage: CouncilStage }) {
  const { complete, active } = STAGE_PROGRESS[stage];

  return (
    <ol className="process-stepper" aria-label="Council deliberation process">
      {STEPS.map((label, i) => {
        const isComplete = i < complete;
        const isActive = active.includes(i);
        const className = ["process-step", isComplete && "is-complete", isActive && "is-active"]
          .filter(Boolean)
          .join(" ");
        return (
          <li key={label} className={className}>
            <span className="process-dot" />
            <span className="process-label">{label}</span>
          </li>
        );
      })}
    </ol>
  );
}
