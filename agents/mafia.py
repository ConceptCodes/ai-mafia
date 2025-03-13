from agents.base_agent import BaseAgent
from lib.constants import MAFIA_ROLE
from lib.llm import get_llm


class MafiaAgent(BaseAgent):
    def __init__(self, name, game_state, mafia_team):
        super().__init__(
            name=name, role=MAFIA_ROLE, game_state=game_state, llm=get_llm()
        )
        self.mafia_team = mafia_team

    def act(self, phase, goal):
        if phase == "night":
            if goal == "suggest":
                task_description = "Engage in discussions with your Mafia teammates to select a target for elimination. "
                response = super().act(task_description, phase)
                if response.player_name in self.mafia_team:
                    self.act(phase, goal)
        else:
            task_description = (
                "Engage in discussions to identify potential Mafia members. "
                "Remember you are talking in a public chat, so be careful with your words. "
                "If you are the target of suspicion, respond with tact and discretion, carefully balancing your insights without revealing your role or identity. "
            )
            response = super().act(task_description, phase)

            if response.player_name in self.mafia_team:
                self.act(phase, goal)

            return response.player_name
