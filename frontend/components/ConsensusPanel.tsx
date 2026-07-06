import type { AgreementLevel, ConsensusSummary } from "@/lib/types";

// CSS class per tier (see globals.css's .agreement.* rules) — mapped
// explicitly rather than slugifying the label, since "Strong Consensus"
// has a space and doesn't survive a naive .toLowerCase() the way the old
// single-word "High"/"Moderate"/"Low" values used to.
const AGREEMENT_CLASS: Record<AgreementLevel, string> = {
  "Strong Consensus": "strong",
  "Moderate Consensus": "moderate",
  "Weak Consensus": "weak",
  "Highly Contested": "contested",
};

export default function ConsensusPanel({ consensus }: { consensus: ConsensusSummary }) {
  const agreementClass = AGREEMENT_CLASS[consensus.agreement_level] ?? "moderate";

  return (
    <div className="consensus-panel">
      <span className={`agreement ${agreementClass}`}>{consensus.agreement_level}</span>

      <span className="field-label">Final decision</span>
      <p className="final-recommendation">{consensus.final_recommendation}</p>

      <div className="consensus-columns">
        <div>
          <h4>Confidence score</h4>
          <div className="confidence-row">
            <div className="confidence-bar-track">
              <div
                className="confidence-bar-fill"
                style={{ width: `${Math.round(consensus.overall_confidence * 100)}%` }}
              />
            </div>
            <span className="confidence-badge">{Math.round(consensus.overall_confidence * 100)}%</span>
          </div>
        </div>
      </div>

      <div className="consensus-columns">
        <div>
          <h4>Top risks</h4>
          {consensus.key_risks.length > 0 ? (
            <ul>
              {consensus.key_risks.map((risk) => (
                <li key={risk}>{risk}</li>
              ))}
            </ul>
          ) : (
            <p className="hint">No significant risks flagged.</p>
          )}
        </div>
        <div>
          <h4>Dissenting opinions</h4>
          {consensus.dissenting_roles.length > 0 ? (
            <ul>
              {consensus.dissenting_roles.map((role) => (
                <li key={role}>{role}</li>
              ))}
            </ul>
          ) : (
            <p className="hint">No strong dissent — the council is aligned.</p>
          )}
        </div>
      </div>

      <div className="consensus-explanation">
        <h4>Why this decision?</h4>
        <p className="explanation-reasoning">{consensus.explanation.reasoning}</p>
        <div className="consensus-columns">
          <div>
            <span className="field-label">Top supporting arguments</span>
            {consensus.explanation.supporting_arguments.length > 0 ? (
              <ul>
                {consensus.explanation.supporting_arguments.map((arg) => (
                  <li key={arg}>{arg}</li>
                ))}
              </ul>
            ) : (
              <p className="hint">No clear supporting argument stood out.</p>
            )}
          </div>
          <div>
            <span className="field-label">Main objections</span>
            {consensus.explanation.main_objections.length > 0 ? (
              <ul>
                {consensus.explanation.main_objections.map((objection) => (
                  <li key={objection}>{objection}</li>
                ))}
              </ul>
            ) : (
              <p className="hint">No major objections raised.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
