import os
import pyfiglet

from game_manager import GameManager

VERSION = "1.0"


def main():
    os.system("cls" if os.name == "nt" else "clear")

    ascii_banner = pyfiglet.figlet_format(f"Mafia v{VERSION}")
    print(ascii_banner)

    manager = GameManager()

    try:
        manager.run_game()
    except KeyboardInterrupt:
        print("\nGame interrupted. Exiting...")

    if manager.check_win_condition():
        print("The game has ended.")


if __name__ == "__main__":
    main()
