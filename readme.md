# Mafia Game Simulation

Welcome to the Mafia Game Simulation! This project simulates the popular social deduction game *Mafia* using AI agents. Each player in the game is controlled by an AI agent that makes decisions based on their role and the current game state.

## Game Roles

- **Narrator**: Guides the players through the game with vivid, engaging narration.
- **Detective**: Investigates players each night to uncover their allegiance.
- **Doctor**: Protects one player each night from being eliminated.
- **Mafia**: Collaborates with other Mafia members to eliminate non-Mafia players.
- **Villager**: Works to identify and vote out the Mafia members during the day phase.

[Here](https://en.wikipedia.org/wiki/Mafia_(party_game)) is a detailed description of the game rules.

## AI Agents
This is a v1 of this simulation. We have a *BaseAgent* class that all agents inherit from. 
Every Agent is given a task to perform in the game. The task is to be implemented in the `act` method.
We will give the agent a simple prompt, role specific chat_log & game_state to make decisions.

## Setup Instructions

1. **Clone the repository**:
    ```sh
    git clone https://github.com/conceptcodes/ai-mafia.git
    cd ai-mafia
    ```

2. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

## Running the Game

To start the game, run the following command:
```sh
python main.py
```

