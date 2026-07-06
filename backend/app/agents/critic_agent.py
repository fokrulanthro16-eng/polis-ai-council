from app.agents.base import BaseAgent


class CriticAgent(BaseAgent):
    """Stress-tests the plan so far, surfacing weak assumptions and gaps."""

    role = "Critic Agent"
