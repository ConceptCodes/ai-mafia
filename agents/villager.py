from agents.base_agent import BaseAgent
from lib.constants import VILLAGER_ROLE
from lib.llm import get_llm


class VillagerAgent(BaseAgent):
    def __init__(self, name, game_state):
        super().__init__(
            name=name, role=VILLAGER_ROLE, game_state=game_state, llm=get_llm()
        )

    def act(self, phase, goal=None):
        task_description = "discuss and share your suspicion about who might be Mafia. "
        (player_name, _) = super().act(task_description, phase)
        return player_name
