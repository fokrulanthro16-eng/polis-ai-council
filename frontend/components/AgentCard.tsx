import type { AgentResult } from "@/lib/types";
import { roleColor, roleInitials } from "@/lib/roleColors";

export default function AgentCard({ agent }: { agent: AgentResult }) {
  return (
    <div className="agent-card" style={{ "--role-color": roleColor(agent.role) } as React.CSSProperties}>
      <div className="agent-card-head">
        <span className="agent-avatar">{roleInitials(agent.role)}</span>
        <div className="agent-card-heading">
          <h3>{agent.role}</h3>
          <div className="confidence-row-mini">
            <div className="confidence-bar-track">
              <div className="confidence-bar-fill" style={{ width: `${Math.round(agent.confidence * 100)}%` }} />
            </div>
            <span className="confidence-badge">{Math.round(agent.confidence * 100)}%</span>
          </div>
        </div>
      </div>

      <p className="analysis">{agent.analysis}</p>

      <div className="agent-card-section">
        <span className="field-label">Key recommendation</span>
        <p className="recommendation">{agent.recommendation}</p>
      </div>

      {agent.objections.length > 0 && (
        <div className="agent-card-section">
          <span className="field-label">Objections</span>
          <ul className="objections">
            {agent.objections.map((objection, i) => (
              <li key={i}>{objection}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
