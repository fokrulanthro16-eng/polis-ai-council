const PLACEHOLDER_COUNT = 6;

export default function LoadingSkeleton() {
  return (
    <div className="agent-grid" aria-hidden="true">
      {Array.from({ length: PLACEHOLDER_COUNT }).map((_, i) => (
        <div className="agent-card skeleton-card" key={i}>
          <div className="agent-card-head">
            <span className="skeleton-block skeleton-avatar" />
            <div className="agent-card-heading">
              <span className="skeleton-block skeleton-line" style={{ width: "60%" }} />
              <span className="skeleton-block skeleton-line" style={{ width: "40%", marginTop: 8 }} />
            </div>
          </div>
          <span className="skeleton-block skeleton-line" style={{ width: "100%" }} />
          <span className="skeleton-block skeleton-line" style={{ width: "90%" }} />
          <span className="skeleton-block skeleton-line" style={{ width: "70%" }} />
        </div>
      ))}
    </div>
  );
}
