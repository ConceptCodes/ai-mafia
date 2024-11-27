from colorama import Fore, Style


ROLE_COLORS = {
    "mafia": Fore.RED,
    "doctor": Fore.BLUE,
    "villager": Fore.GREEN,
    "detective": Fore.BLACK + Style.BRIGHT,
    "narrator": Fore.YELLOW,
}

CHAT_LOG_PUBLIC = "public"
CHAT_LOG_MAFIA = "mafia"
CHAT_LOG_DOCTOR_NARRATOR = "doctor_narrator"
CHAT_LOG_DETECTIVE_NARRATOR = "detective_narrator"

LOG_FORMAT = "\n{color}[{asctime} - {chat_log_key} - {player_name}]{reset}: {message}"

MAFIA_ROLE = "mafia"
DOCTOR_ROLE = "doctor"
DETECTIVE_ROLE = "detective"
VILLAGER_ROLE = "villager"
NARRATOR_ROLE = "narrator"

PLAYER_NAME_REGEX = "<player:(?P<player_name>[^>]+)>"
