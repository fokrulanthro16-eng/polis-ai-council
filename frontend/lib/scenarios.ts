export interface DemoScenario {
  id: string;
  title: string;
  tagline: string;
  problem: string;
}

export const DEMO_SCENARIOS: DemoScenario[] = [
  {
    id: "healthcare",
    title: "Healthcare Resource Allocation",
    tagline: "How should a hospital system ration ICU capacity in a surge?",
    problem:
      "During a regional surge in patients, how should our hospital system allocate a limited budget for ICU beds, nursing staff, and equipment across three facilities, balancing patient safety, staff burnout risk, and the cost of emergency hiring?",
  },
  {
    id: "climate",
    title: "Climate-Resilient City Planning",
    tagline: "Should a coastal city spend $500M on flood defenses?",
    problem:
      "Our coastal city faces escalating flood risk from climate change. Should we commit a $500 million budget over the next decade to flood-resistant infrastructure, sea walls, and smart stormwater systems, even though it will raise costs for taxpayers, require hiring new engineering staff, and delay other capital projects?",
  },
  {
    id: "education",
    title: "AI Education Policy",
    tagline: "Should schools mandate AI literacy and AI tutoring tools?",
    problem:
      "Should our national education ministry mandate an AI literacy curriculum in every public school and allow AI tutoring software in classrooms, despite concerns about job security for teaching staff, student data privacy, and unequal technology access as the program scales nationwide?",
  },
];

// Pre-filled into the problem box on first load, so the app never opens
// on an empty, uninviting textarea — distinct from the one-click
// scenario cards above it, which replace this.
export const DEFAULT_PROBLEM =
  "Should our startup lay off 20% of staff to cut costs before the next funding round?";
