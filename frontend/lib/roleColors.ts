// Consistent color coding and initials for each agent role, used across
// cards and the timeline.
export const ROLE_COLORS: Record<string, string> = {
  "Research Agent": "#6ea8fe",
  "Planner Agent": "#c084fc",
  "Critic Agent": "#fb923c",
  "Risk Agent": "#f87171",
  "Ethics Agent": "#4ade80",
  "Consensus Agent": "#facc15",
};

const ROLE_INITIALS: Record<string, string> = {
  "Research Agent": "RE",
  "Planner Agent": "PL",
  "Critic Agent": "CR",
  "Risk Agent": "RI",
  "Ethics Agent": "ET",
  "Consensus Agent": "CO",
};

export function roleColor(role: string): string {
  return ROLE_COLORS[role] ?? "#6ea8fe";
}

export function roleInitials(role: string): string {
  return ROLE_INITIALS[role] ?? role.slice(0, 2).toUpperCase();
}
