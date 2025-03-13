from collections import deque

from agents.detective import DetectiveAgent
from agents.doctor import DoctorAgent
from agents.mafia import MafiaAgent
from agents.narrator import NarratorAgent
from agents.villager import VillagerAgent
from lib.constants import (
    CHAT_LOG_MAFIA,
    DETECTIVE_ROLE,
    DOCTOR_ROLE,
    MAFIA_ROLE,
    NARRATOR_ROLE,
    VILLAGER_ROLE,
    Fore,
    Style,
    CHAT_LOG_DOCTOR_NARRATOR,
)
from lib.utils import (
    display_players,
    get_current_day,
    get_current_phase,
    get_last_protection,
    get_mafia_target,
    get_players,
    initialize_chat_logs,
    initialize_players,
    post_message,
    is_alive,
    reset_mafia_target,
    set_current_phase,
    update_day,
    update_eliminations,
    update_mafia_target,
    update_protections,
)
from lib.models import (
    ConversationState,
    GameState,
)


class GameManager:
    def __init__(self):
        self.game_state = self.initialize_game_state()
        self.initialize_agents()

    def initialize_game_state(self) -> GameState:
        game_state = GameState(
            day=1,
            phase="night",
            players={},
            chat_logs={},
            eliminations=[],
            mafia_target="",
            investigation_history=[],
            protections=[],
        )

        initialize_chat_logs(game_state)
        initialize_players(game_state)

        return game_state

    def initialize_agents(self):
        players = get_players(self.game_state)
        for player_name, info in players.items():
            if info.role == NARRATOR_ROLE:
                info.agent = NarratorAgent(self.game_state)
            elif info.role == DETECTIVE_ROLE:
                info.agent = DetectiveAgent(player_name, self.game_state)
            elif info.role == DOCTOR_ROLE:
                info.agent = DoctorAgent(player_name, self.game_state)
            elif info.role == MAFIA_ROLE:
                info.agent = MafiaAgent(
                    player_name, self.game_state, self.get_mafia_team_names(player_name)
                )
            elif info.role == VILLAGER_ROLE:
                info.agent = VillagerAgent(player_name, self.game_state)

    def get_mafia_agents(self) -> list:
        players = get_players(self.game_state)
        mafia_players = [
            player_info
            for player_name, player_info in players.items()
            if player_info.role == MAFIA_ROLE and is_alive(self.game_state, player_name)
        ]
        return [player.agent for player in mafia_players]

    def get_mafia_team_names(self, current_player_name) -> list:
        players = get_players(self.game_state)
        return [
            player_name
            for player_name, info in players.items()
            if info.role == MAFIA_ROLE and player_name != current_player_name
        ]

    def run_game(self):
        display_players(self.game_state)
        while not self.check_win_condition():
            current_phase = get_current_phase(self.game_state)
            if current_phase == "night":
                self.night_phase()
                set_current_phase(self.game_state, "day")
            elif current_phase == "day":
                self.day_phase()
                set_current_phase(self.game_state, "night")
                update_day(self.game_state)

    def night_phase(self):
        print(
            f"\n============ {Fore.CYAN}Night {get_current_day(self.game_state)} begins.{Style.RESET_ALL} ============"
        )

        if self.game_state.day == 1 and self.game_state.phase == "night":
            players = get_players(self.game_state)
            narrator = players.get("Narrator")
            narrator.agent.act("night", goal="introduce")

        self.mafia_discussion_and_target_selection()
        self.doctor_protection()
        self.detective_investigation()
        self.resolve_night_actions()

    def mafia_choose_target(self, mafia_target):
        post_message(
            game_state=self.game_state,
            chat_log_key=CHAT_LOG_MAFIA,
            player_name=None,
            message=f"Selected target: {mafia_target}",
        )
        update_mafia_target(game_state=self.game_state, target_name=mafia_target)
        return

    def discuss_and_choose_target(self, agents: list, phase: str):
        max_rounds = 5
        agent_queue = deque(agents)
        state_manager = ConversationState(agents)

        for _ in range(max_rounds):
            print(f"\n--- Round {state_manager.rounds + 1} ---")
            while agent_queue:
                agent = agent_queue.popleft()
                response = agent.act(phase=phase, goal="suggest")
                print(response)
                state_manager.update_decision(agent.name, response.player_name)

                # Check for consensus
                consensus_reached, selected_user = state_manager.check_consensus()
                if consensus_reached:
                    print(f"\n✅ Consensus Reached! Selected User: {selected_user}")
                    return selected_user

            state_manager.rounds += 1
            agent_queue.extend(agents)

        print("\n❌ Consensus not reached.")
        state_manager.clear()

    def mafia_discussion_and_target_selection(self):
        print(f"\n{Fore.RED}[ Mafia Discussion and Target Selection ]{Style.RESET_ALL}")

        mafia_agents = self.get_mafia_agents()
        mafia_target = self.discuss_and_choose_target(mafia_agents, "night")

        self.mafia_choose_target(mafia_target)

    def doctor_protection(self):
        print(f"\n{Fore.BLUE}Doctor Protection{Style.RESET_ALL}")
        protection_target = None
        players = get_players(game_state=self.game_state)
        doctor = players.get("Doctor")

        if is_alive(game_state=self.game_state, player_name=doctor.name) is False:
            print("Doctor is not alive.")
            return

        protection_target = doctor.agent.act(phase="night")
        post_message(
            game_state=self.game_state,
            chat_log_key=CHAT_LOG_DOCTOR_NARRATOR,
            player_name=doctor.name,
            message=f"Protected {protection_target}",
        )
        update_protections(game_state=self.game_state, player_name=protection_target)

    def detective_investigation(self):
        print(f"\n{Fore.BLACK + Style.BRIGHT}Detective Investigation{Style.RESET_ALL}")
        players = get_players(self.game_state)
        detective = players.get("Detective")
        if is_alive(self.game_state, detective.name) is False:
            return
        detective.agent.act(phase="night")

    def resolve_night_actions(self):
        print(f"\n{Fore.MAGENTA}Resolve Night Actions{Style.RESET_ALL}")
        mafia_target = get_mafia_target(self.game_state)
        protection_target = get_last_protection(self.game_state)

        if mafia_target and mafia_target != protection_target:
            update_eliminations(game_state=self.game_state, player_name=mafia_target)
            print(
                f"{Fore.RED}{mafia_target} was eliminated during the night.{Style.RESET_ALL}"
            )
        else:
            print(
                f"{Fore.BLUE}The Doctor protected {protection_target}, preventing their elimination!{Style.RESET_ALL}"
            )

        reset_mafia_target(self.game_state)

    def day_phase(self):
        print(
            f"\n============ {Fore.CYAN}Day {get_current_day(self.game_state)} begins.{Style.RESET_ALL} ============"
        )

        players = get_players(self.game_state)
        narrator = players.get("Narrator")
        narrator.agent.act(phase="day")

        narrator_excluded = {
            player_name: info
            for player_name, info in players.items()
            if player_name != "Narrator"
        }

        target = self.discuss_and_choose_target(narrator_excluded, "day")

        print(f"\n{Fore.MAGENTA}Resolve Day Actions{Style.RESET_ALL}")

        if target:
            update_eliminations(self.game_state, target)
            print(
                f"{Fore.MAGENTA}{target} was eliminated by a majority decision.{Style.RESET_ALL}"
            )

    def check_win_condition(self):
        players = get_players(self.game_state)
        mafia_count = sum(
            1 for p in players.values() if p.role == MAFIA_ROLE and p.status == "alive"
        )
        villager_count = sum(
            1 for p in players.values() if p.role != MAFIA_ROLE and p.status == "alive"
        )

        if mafia_count == 0:
            print(f"{Fore.GREEN}Villagers win!{Style.RESET_ALL}")
            return True
        elif mafia_count >= villager_count:
            print(f"{Fore.RED}Mafia wins!{Style.RESET_ALL}")
            return True
        return False
