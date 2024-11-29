from agents.base_agent import BaseAgent
from lib.constants import CHAT_LOG_PUBLIC, NARRATOR_ROLE
from lib.llm import get_llm


class NarratorAgent(BaseAgent):
    def __init__(self, game_state):
        super().__init__(
            name="Narrator",
            role=NARRATOR_ROLE,
            game_state=game_state,
            llm=get_llm(),
        )

    def act(self, phase, goal=None):
        if goal == "introduce":
            task_description = "Introduce the game to the players. Dont create any suspense yet, just set the scene."
        else:
            task_description = (
                "Provide a summary of the events that have occurred so far. "
                "Dont forget to mention any eliminations that have occurred."
            )
        response = super().act(task_description, phase)
        return response
