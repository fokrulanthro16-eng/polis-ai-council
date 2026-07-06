import { DEMO_SCENARIOS } from "@/lib/scenarios";

interface ScenarioPickerProps {
  selectedId: string | null;
  onSelect: (problem: string, id: string) => void;
  disabled?: boolean;
}

export default function ScenarioPicker({ selectedId, onSelect, disabled }: ScenarioPickerProps) {
  return (
    <div className="scenario-picker">
      <div className="scenario-picker-head">
        <h2>Try a demo scenario</h2>
        <span className="hint">Or describe your own decision below</span>
      </div>
      <div className="scenario-grid">
        {DEMO_SCENARIOS.map((scenario) => (
          <button
            key={scenario.id}
            type="button"
            className={`scenario-card ${selectedId === scenario.id ? "is-selected" : ""}`}
            onClick={() => onSelect(scenario.problem, scenario.id)}
            disabled={disabled}
          >
            <span className="scenario-title">{scenario.title}</span>
            <span className="scenario-tagline">{scenario.tagline}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
