from app.agents.base import BaseAgent


class RiskAgent(BaseAgent):
    """Assesses downside exposure and proposes contingencies."""

    role = "Risk Agent"
