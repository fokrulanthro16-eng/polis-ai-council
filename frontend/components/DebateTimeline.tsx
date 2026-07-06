import type { DebateTimelineEntry } from "@/lib/types";
import { roleColor, roleInitials } from "@/lib/roleColors";

export default function DebateTimeline({ timeline }: { timeline: DebateTimelineEntry[] }) {
  return (
    <ol className="timeline">
      {timeline.map((entry) => (
        <li key={entry.step} style={{ "--role-color": roleColor(entry.role) } as React.CSSProperties}>
          <span className="timeline-avatar">{roleInitials(entry.role)}</span>
          <div className="timeline-body">
            <div className="timeline-role">
              <span className="timeline-step">Step {entry.step}</span>
              {entry.role}
              {entry.responding_to && (
                <span className="timeline-responding-to">responding to {entry.responding_to}</span>
              )}
            </div>
            <div className="timeline-message">{entry.message}</div>
          </div>
        </li>
      ))}
    </ol>
  );
}
