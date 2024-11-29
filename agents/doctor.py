from agents.base_agent import BaseAgent
from lib.constants import DOCTOR_ROLE
from lib.llm import get_llm


class DoctorAgent(BaseAgent):
    def __init__(self, name, game_state):
        super().__init__(
            name=name, role=DOCTOR_ROLE, game_state=game_state, llm=get_llm()
        )

    def act(self, phase: str, goal=None):
        if phase == "night":
            task_description = (
                "Choose one player to protect from elimination. "
                "You cannot protect the same player two nights in a row. "
                "You can also choose to protect yourself from elimination. "
                "Remember that you are talking to the narrator, not the other players."
            )
        else:
            task_description = (
                "Discuss and share your suspicion about who might be Mafia."
            )

        (player_name, _) = super().act(task_description, phase)
        return player_name
