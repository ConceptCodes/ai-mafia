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
    reset_potential_mafia_targets,
    set_current_phase,
    set_potential_mafia_targets,
    update_day,
    update_eliminations,
    update_mafia_target,
    update_protections,
)
from lib.models import GameState


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
            narrator = next(
                player for player in players.values() if player.role == NARRATOR_ROLE
            )
            narrator.agent.act("night", goal="introduce")

        self.mafia_discussion_and_target_selection()
        self.doctor_protection()
        self.detective_investigation()
        self.resolve_night_actions()

    def mafia_discussion_and_target_selection(self):
        print(f"\n{Fore.RED}[ Mafia Discussion ]{Style.RESET_ALL}")
        mafia_agents = self.get_mafia_agents()

        # Step 1: Collect Suggestions
        suggestions = set()
        for player in mafia_agents:
            try:
                suggestion = player.act(phase="night", goal="suggest")
                suggestions.add(suggestion)
            except ValueError as e:
                pass  # TODO: retry mechanism needed!

        set_potential_mafia_targets(self.game_state, list(suggestions))

        print("\nMafia Suggestions:")
        for target in suggestions:
            print(target)

        # Step 2: Vote on Targets
        print(f"\n{Fore.RED}[ Mafia Voting ]{Style.RESET_ALL}")
        votes = {}
        for agent in mafia_agents:
            try:
                player_name = agent.act(phase="night", goal="vote")
                votes[player_name] = votes.get(player_name, 0) + 1
            except ValueError as e:
                pass  # TODO: retry mechanism needed!

        # Log the votes
        print("\nMafia Votes:")
        for target, count in votes.items():
            print(f"{target}: {count} votes")

        # Step 3: Select Target
        if votes:
            mafia_target = max(votes, key=votes.get)
            post_message(
                game_state=self.game_state,
                chat_log_key=CHAT_LOG_MAFIA,
                player_name=None,
                message=f"Selected target: {mafia_target}",
            )
        else:
            mafia_target = None
        update_mafia_target(game_state=self.game_state, target_name=mafia_target)

    def doctor_protection(self):
        print(f"\n{Fore.BLUE}Doctor Protection{Style.RESET_ALL}")
        protection_target = None
        players = get_players(game_state=self.game_state)
        doctor = next(
            (
                (player_name, player_info)
                for player_name, player_info in players.items()
                if player_info.role == DOCTOR_ROLE
                and is_alive(game_state=self.game_state, player_name=player_name)
            ),
            None,
        )

        if doctor is None:
            print("Doctor is not alive.")
            return

        player_name, player_info = doctor

        protection_target = player_info.agent.act(phase="night")
        post_message(
            game_state=self.game_state,
            chat_log_key=CHAT_LOG_DOCTOR_NARRATOR,
            player_name=player_name,
            message=f"Protected {protection_target}",
        )
        update_protections(game_state=self.game_state, player_name=protection_target)

    def detective_investigation(self):
        print(f"\n{Fore.BLACK + Style.BRIGHT}Detective Investigation{Style.RESET_ALL}")
        players = get_players(self.game_state)
        detective = next(
            (player_name, player_info)
            for player_name, player_info in players.items()
            if player_info.role == DETECTIVE_ROLE
            and is_alive(game_state=self.game_state, player_name=player_name)
        )
        if detective is None:
            return
        _, _detective = detective
        _detective.agent.act(phase="night")

    def resolve_night_actions(self):
        print(f"\n{Fore.MAGENTA}Resolve Night Actions{Style.RESET_ALL}")
        mafia_target = get_mafia_target(self.game_state)
        protection_target = get_last_protection(self.game_state)

        if mafia_target and mafia_target != protection_target:
            update_eliminations(
                game_state=self.game_state, role=MAFIA_ROLE, player_name=mafia_target
            )
            print(
                f"{Fore.RED}{mafia_target} was eliminated during the night.{Style.RESET_ALL}"
            )
        else:
            print(
                f"{Fore.BLUE}The Doctor protected {protection_target}, preventing their elimination!{Style.RESET_ALL}"
            )

        reset_mafia_target(self.game_state)
        reset_potential_mafia_targets(self.game_state)

    def day_phase(self):
        print(
            f"\n============ {Fore.CYAN}Day {get_current_day(self.game_state)} begins.{Style.RESET_ALL} ============"
        )

        # Narrator announces night events
        players = get_players(self.game_state)
        narrator = next(
            (player_name, player_info)
            for player_name, player_info in players.items()
            if player_info.role == NARRATOR_ROLE
        )
        _, _narrator = narrator
        _narrator.agent.act(phase="day")

        # Players communicate
        for player_name, player_info in players.items():
            if (
                is_alive(game_state=self.game_state, player_name=player_name)
                and player_info.role != NARRATOR_ROLE
            ):
                player_info.agent.act(phase="day", goal="communicate")

        self.resolve_day_actions()

    def resolve_day_actions(self):
        print(f"\n{Fore.MAGENTA}Resolve Day Actions{Style.RESET_ALL}")

        # Voting logic
        votes = {}
        players = get_players(self.game_state)

        for player_name, player_info in players.items():
            if player_info.role != NARRATOR_ROLE and is_alive(
                game_state=self.game_state, player_name=player_name
            ):
                chosen = player_info.agent.act(phase="day", goal="vote")
                votes[chosen] = votes.get(chosen, 0) + 1

        # Determine player to eliminate
        if votes:
            eliminated_player = max(votes, key=votes.get)
            update_eliminations(self.game_state, "public", eliminated_player)

            print(
                f"{Fore.MAGENTA}{eliminated_player} was eliminated by a majority vote.{Style.RESET_ALL}"
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
