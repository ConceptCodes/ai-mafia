import stamina
from halo import Halo
from langchain_core.language_models.llms import LLM
from typing import Union


from lib.models import ConversationalResponse, GameState, NarratorResponse
import lib.prompts as prompts
from lib.utils import (
    add_to_chat_log,
    get_role_specific_chat_log,
    get_role_specific_game_state,
    post_message,
    narrator_parser,
    common_parser,
)
from lib.constants import (
    CHAT_LOG_DETECTIVE_NARRATOR,
    CHAT_LOG_DOCTOR_NARRATOR,
    CHAT_LOG_MAFIA,
    CHAT_LOG_PUBLIC,
    DETECTIVE_ROLE,
    DOCTOR_ROLE,
    MAFIA_ROLE,
    NARRATOR_ROLE,
    VILLAGER_ROLE,
)


class BaseAgent:
    def __init__(self, name: str, role: str, game_state: GameState, llm: LLM):
        self.role = role
        self.game_state = game_state
        self.name = name

        self.prompt_template = self.get_prompt_template()

        if self.role == NARRATOR_ROLE:
            parser = narrator_parser
        else:
            parser = common_parser

        self.llm_chain = self.prompt_template | llm | parser

    def send_message(self, message, chat_log_key):
        post_message(
            game_state=self.game_state,
            chat_log_key=chat_log_key,
            player_name=self.name,
            message=message,
        )
        add_to_chat_log(
            game_state=self.game_state, chat_log_key=chat_log_key, message=message
        )

    def get_prompt_template(self):
        role_mapping = {
            NARRATOR_ROLE: prompts.narrator_template,
            DETECTIVE_ROLE: prompts.detective_template,
            DOCTOR_ROLE: prompts.doctor_template,
            MAFIA_ROLE: prompts.mafia_template,
            VILLAGER_ROLE: prompts.villager_template,
        }

        return role_mapping[self.role]

    @stamina.retry(on=Exception, attempts=2)
    def act(self, task_description: str, phase: str, goal=None):
        response = None

        chat_logs = get_role_specific_chat_log(
            game_state=self.game_state, role=self.role, should_reverse=False
        )
        game_state = get_role_specific_game_state(
            game_state=self.game_state, name=self.name, role=self.role
        )

        spinner = Halo(text=f"\n{self.name}: {task_description}", spinner="dots")
        spinner.start()

        response = self.llm_chain.invoke(
            {
                "game_state": game_state,
                "chat_history": chat_logs,
                "task_description": task_description,
                "player_name": self.name,
            }
        )

        if response is None:
            raise Exception(" response is None")

        if self.role == NARRATOR_ROLE:
            if response["message"] == None:
                raise Exception("Narrator response is None")
            response = NarratorResponse(message=response["message"])
        else:
            if response["message"] == None or response["player_name"] == None:
                raise Exception("Player response is None")
            response = ConversationalResponse(
                player_name=response["player_name"],
                message=response["message"],
            )

        spinner.stop()
        if phase == "night":
            if self.role == MAFIA_ROLE:
                self.send_message(message=response.message, chat_log_key=CHAT_LOG_MAFIA)
            elif self.role == DOCTOR_ROLE:
                self.send_message(
                    message=response.message, chat_log_key=CHAT_LOG_DOCTOR_NARRATOR
                )
            elif self.role == DETECTIVE_ROLE:
                self.send_message(
                    message=response.message, chat_log_key=CHAT_LOG_DETECTIVE_NARRATOR
                )
            else:
                self.send_message(
                    message=response.message, chat_log_key=CHAT_LOG_PUBLIC
                )
        else:
            self.send_message(message=response.message, chat_log_key=CHAT_LOG_PUBLIC)

        return response
