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
                task_description = "Suggest a non-Mafia player for elimination. "
                (player_name, _) = super().act(task_description, phase)
                if player_name in self.mafia_team:
                    raise ValueError("Mafia cannot target themselves.")
                return player_name
            elif goal == "vote":
                task_description = (
                    "Cast your vote for elimination from the pool of potential targets. "
                    "Ensure alignment with your team's objectives."
                )
                (player_name, _) = super().act(task_description, phase)
                return player_name
        else:
            task_description = (
                "Engage in discussions to identify potential Mafia members. "
                "Share your suspicions and observations, aiming to mislead non-Mafia players while protecting your teams true identity. "
                "Remember you are talking in a public chat, so be careful with your words. "
                "If you are the target of suspicion, respond with tact and discretion, carefully balancing your insights without revealing your role or identity."
            )
            (player_name, _) = super().act(task_description, phase)
            return player_name
