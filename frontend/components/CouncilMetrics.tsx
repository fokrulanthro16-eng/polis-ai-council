import type { CouncilMetrics as CouncilMetricsData, MetricLevel } from "@/lib/types";

// Risk and evidence quality read in opposite directions — "High" risk is
// bad, "High" evidence quality is good — so each gets its own semantic
// color mapping rather than sharing one generic low/medium/high scale.
const RISK_TONE: Record<MetricLevel, string> = { Low: "good", Medium: "warn", High: "danger" };
const QUALITY_TONE: Record<MetricLevel, string> = { Low: "danger", Medium: "warn", High: "good" };

export default function CouncilMetrics({ metrics }: { metrics: CouncilMetricsData }) {
  return (
    <div className="metrics-grid">
      <div className="metric-tile">
        <span className="field-label">Council Confidence</span>
        <span className="metric-value">{Math.round(metrics.council_confidence * 100)}%</span>
      </div>
      <div className="metric-tile">
        <span className="field-label">Agreement Score</span>
        <span className="metric-value">{Math.round(metrics.agreement_score * 100)}%</span>
      </div>
      <div className="metric-tile">
        <span className="field-label">Risk Level</span>
        <span className={`metric-badge ${RISK_TONE[metrics.risk_level]}`}>{metrics.risk_level}</span>
      </div>
      <div className="metric-tile">
        <span className="field-label">Evidence Quality</span>
        <span className={`metric-badge ${QUALITY_TONE[metrics.evidence_quality]}`}>
          {metrics.evidence_quality}
        </span>
      </div>
    </div>
  );
}
