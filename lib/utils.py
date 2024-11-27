import time
from typing import Dict, List
import faker
from langchain_core.output_parsers import JsonOutputParser


from lib import constants
from lib.constants import (
    Fore,
    Style,
    DETECTIVE_ROLE,
    DOCTOR_ROLE,
    MAFIA_ROLE,
    NARRATOR_ROLE,
    VILLAGER_ROLE,
    CHAT_LOG_PUBLIC,
    CHAT_LOG_MAFIA,
    CHAT_LOG_DETECTIVE_NARRATOR,
    CHAT_LOG_DOCTOR_NARRATOR,
    ROLE_COLORS,
    LOG_FORMAT,
)
from lib.models import (
    ActionResponse,
    ChatLogEntry,
    ConversationalResponse,
    InvestigateAction,
    PlayerInfo,
    GameState,
)

fake = faker.Faker()


def initialize_chat_logs(game_state):
    chat_logs = {
        CHAT_LOG_PUBLIC: [],
        CHAT_LOG_MAFIA: [],
        CHAT_LOG_DETECTIVE_NARRATOR: [],
        CHAT_LOG_DOCTOR_NARRATOR: [],
    }
    game_state.chat_logs = chat_logs


def initialize_players(game_state):
    NUM_MAFIA = 2
    NUM_VILLAGERS = NUM_MAFIA + 2
    players = {}

    players["Narrator"] = PlayerInfo(role=NARRATOR_ROLE, status="alive", agent=None)
    players[fake.first_name()] = PlayerInfo(
        role=DETECTIVE_ROLE, status="alive", agent=None
    )
    players[fake.first_name()] = PlayerInfo(
        role=DOCTOR_ROLE, status="alive", agent=None
    )

    for _ in range(NUM_MAFIA):
        players[fake.first_name()] = PlayerInfo(
            role=MAFIA_ROLE, status="alive", agent=None
        )

    for _ in range(NUM_VILLAGERS):
        players[fake.first_name()] = PlayerInfo(
            role=VILLAGER_ROLE, status="alive", agent=None
        )

    game_state.players = players


def post_message(game_state, chat_log_key, player_name=None, message=""):
    if player_name is None:
        player_name = "Narrator"

    player_role = get_player_role(game_state, player_name)

    formatted_message = build_log_message(
        chat_log_key, player_role, player_name, message
    )

    print(formatted_message)


def build_log_message(chat_log_key, role, player_name, message):
    return LOG_FORMAT.format(
        color=ROLE_COLORS.get(role, Fore.WHITE),
        asctime=time.asctime(),
        chat_log_key=chat_log_key,
        player_name=player_name,
        message=message,
        reset=Style.RESET_ALL,
    )


def is_alive(game_state: GameState, player_name: str) -> bool:
    if player_name == "Narrator":
        return True
    return game_state.players[player_name].status == "alive"


def get_player_role(game_state: GameState, player_name: str) -> str:
    return game_state.players[player_name].role


def get_players(game_state: GameState) -> Dict[str, PlayerInfo]:
    return dict(sorted(game_state.players.items(), key=lambda x: fake.random_int()))


def get_chat_log(
    game_state: GameState, chat_log_key: str
) -> Dict[str, List[ChatLogEntry]]:
    return game_state.chat_logs[chat_log_key]


def add_to_chat_log(game_state: GameState, chat_log_key: str, message: str) -> None:
    game_state.chat_logs[chat_log_key].append(
        ChatLogEntry(message=message, timestamp=time.time())
    )


def get_role_specific_chat_log(
    game_state: GameState, role: str, should_reverse: bool = False
) -> List[str]:
    logs = []
    if role == MAFIA_ROLE:
        logs += get_chat_log(game_state, constants.CHAT_LOG_MAFIA)
    elif role == DETECTIVE_ROLE:
        logs += get_chat_log(game_state, constants.CHAT_LOG_DETECTIVE_NARRATOR)
    elif role == DOCTOR_ROLE:
        logs += get_chat_log(game_state, constants.CHAT_LOG_DOCTOR_NARRATOR)

    logs += get_chat_log(game_state, constants.CHAT_LOG_PUBLIC)

    sorted_chat_logs = sorted(logs, key=lambda x: x.timestamp, reverse=should_reverse)
    return [chat_log.message for chat_log in sorted_chat_logs]


def get_role_specific_game_state(game_state: GameState, name: str, role: str):
    formatted_game_state = {
        "players": [
            player_name
            for player_name, player_info in game_state.players.items()
            if player_info.status == "alive"
            and player_name != name
            and player_info.role != NARRATOR_ROLE
        ],
        "phase": game_state.phase,
        # "day_number": game_state.day,
        # "identity": name,
        "eliminations": game_state.eliminations,
        "most_recent_elimination": (
            game_state.eliminations[-1] if game_state.eliminations else None
        ),
    }

    if role == MAFIA_ROLE:
        formatted_game_state["mafia_members"] = [
            player_name
            for player_name, player_info in game_state.players.items()
            if player_info.role == MAFIA_ROLE
            and player_info.status == "alive"
            and player_name != name
        ]
        formatted_game_state["mafia_target"] = game_state.mafia_target
        formatted_game_state["potential_mafia_targets"] = (
            game_state.potential_mafia_targets
        )
    elif role == DETECTIVE_ROLE:
        formatted_game_state["investigations"] = game_state.investigation_history
    elif role == DOCTOR_ROLE:
        formatted_game_state["protections"] = game_state.protections

    return formatted_game_state


def update_investigation_history(
    game_state: GameState, target: str, result: str
) -> None:
    game_state.investigation_history.append(
        InvestigateAction(target=target, result=result)
    )


def update_protections(game_state: GameState, player_name: str) -> None:
    game_state.protections.append(player_name)


def update_mafia_target(game_state: GameState, target_name: str) -> None:
    game_state.mafia_target = target_name


def update_eliminations(game_state: GameState, role: str, player_name: str) -> None:
    game_state.eliminations.append(player_name)
    game_state.players[player_name].status = "eliminated"


def get_last_investigation(game_state: GameState) -> InvestigateAction:
    return game_state.investigation_history[-1]


def get_last_protection(game_state: GameState) -> str:
    return game_state.protections[-1]


def reset_mafia_target(game_state: GameState) -> None:
    game_state.mafia_target = ""


def get_current_phase(game_state: GameState) -> str:
    return game_state.phase


def set_current_phase(game_state: GameState, phase) -> None:
    game_state.phase = phase


def get_current_day(game_state: GameState) -> int:
    return game_state.day


def update_phase(game_state: GameState, phase) -> None:
    game_state.phase = phase


def update_day(game_state: GameState) -> None:
    game_state.day += 1


def get_mafia_target(game_state: GameState) -> str:
    return game_state.mafia_target


def set_potential_mafia_targets(
    game_state: GameState, potential_mafia_targets: List[str]
) -> None:
    game_state.potential_mafia_targets = potential_mafia_targets


def get_llm_output_parser(base_model):
    return JsonOutputParser(pydantic_object=base_model)


def reset_potential_mafia_targets(game_state: GameState) -> None:
    game_state.potential_mafia_targets = []

narrator_parser = get_llm_output_parser(ConversationalResponse)
common_parser = get_llm_output_parser(ActionResponse)
