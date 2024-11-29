from agents.base_agent import BaseAgent
from lib.constants import CHAT_LOG_DETECTIVE_NARRATOR, DETECTIVE_ROLE, MAFIA_ROLE
from lib.llm import get_llm
from lib.utils import get_players, update_investigation_history


class DetectiveAgent(BaseAgent):
    def __init__(self, name, game_state):
        super().__init__(
            name=name, role=DETECTIVE_ROLE, game_state=game_state, llm=get_llm()
        )

    def act(self, phase, goal=None):
        if phase == "night":
            task_description = (
                "Select a player whose recent actions have aroused your suspicion."
            )
            (player_name, _) = super().act(task_description, phase)
            result = self.ask_narrator(player_name)
            update_investigation_history(
                game_state=self.game_state, target=player_name, result=result
            )
            return result
        else:
            task_description = (
                "Reflect on the previous events and the behaviors exhibited by other players to inform your decisions. "
                "Be prepared to adjust your strategies based on new information and the evolving dynamics of the game."
                "Discuss and share your suspicion about who might be Mafia."
                "Consider the complete conversation history, the additional context, your current situation, emotional state, and goals when writing a response. "
            )
            (player_name, _) = super().act(task_description, phase)
            return player_name

    def ask_narrator(self, target):
        """Simulate a back-and-forth conversation with the narrator."""
        players = get_players(self.game_state)
        if target not in players.keys():
            raise KeyError(f"Invalid player name: {target}")

        # Initial question from the Detective
        question = f"Is {target} a member of the Mafia?"
        self.send_message(question, CHAT_LOG_DETECTIVE_NARRATOR)

        # Narrator's response
        player_info = players[target]
        if player_info.role == MAFIA_ROLE:
            response = f"{target} is indeed a member of the Mafia."
        else:
            response = f"{target} is not a member of the Mafia."
        self.send_message(response, CHAT_LOG_DETECTIVE_NARRATOR)

        # Follow-up question from the Detective
        follow_up_question = (
            f"Can you provide any additional information about {target}?"
        )
        self.send_message(follow_up_question, CHAT_LOG_DETECTIVE_NARRATOR)

        # Narrator's follow-up response
        if player_info.role == MAFIA_ROLE:
            follow_up_response = (
                f"{target} has been seen conspiring with other Mafia members."
            )
        else:
            follow_up_response = f"{target} appears to be an innocent villager."
        self.send_message(follow_up_response, CHAT_LOG_DETECTIVE_NARRATOR)

        # Final confirmation from the Detective
        final_confirmation = f"Thank you for the information about {target}."
        self.send_message(final_confirmation, CHAT_LOG_DETECTIVE_NARRATOR)

        return response
