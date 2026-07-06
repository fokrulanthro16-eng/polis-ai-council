from app.agents.base import BaseAgent


class ResearchAgent(BaseAgent):
    """Gathers and summarizes relevant background information on the problem."""

    role = "Research Agent"
