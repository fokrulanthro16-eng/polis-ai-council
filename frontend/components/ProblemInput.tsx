import { DEFAULT_PROBLEM } from "@/lib/scenarios";

interface ProblemInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  loading: boolean;
}

export default function ProblemInput({ value, onChange, onSubmit, loading }: ProblemInputProps) {
  const canSubmit = value.trim().length >= 3 && !loading;

  return (
    <div className="input-card" id="problem-input">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={`Describe a decision or problem for the council to debate…\ne.g. "${DEFAULT_PROBLEM}"`}
        disabled={loading}
        onKeyDown={(e) => {
          if (e.key === "Enter" && (e.metaKey || e.ctrlKey) && canSubmit) onSubmit();
        }}
      />
      <div className="input-row">
        <span className="hint">Tip: Cmd/Ctrl + Enter to run</span>
        <button className="run-btn" onClick={onSubmit} disabled={!canSubmit}>
          {loading ? (
            <>
              <span className="btn-spinner" /> Deliberating…
            </>
          ) : (
            "Run Council"
          )}
        </button>
      </div>
    </div>
  );
}
