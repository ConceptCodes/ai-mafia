from pydantic import BaseModel, Field
from typing import List, Dict, Union
from collections import Counter


class ConversationalResponse(BaseModel):
    """
    A Response that requires selecting a player and providing an explanation
    """

    player_name: str = Field(..., description="The name of the player your selecting")
    message: str = Field(
        ..., description="Your explanation behind your choice of player"
    )


class NarratorResponse(BaseModel):
    """
    A Response that requires just a message
    """

    message: str = Field(..., description="The response to the prompt")


# NOTE: not working as expected, will circle back to this
class LLMResponse(BaseModel):
    output: Union[
        ConversationalResponse,
        NarratorResponse,
    ]


class PlayerInfo(BaseModel):
    role: str
    status: str
    agent: object = None


class ChatLogEntry(BaseModel):
    message: str
    timestamp: float

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __repr__(self):
        return self.message

    __str__ = __repr__


class InvestigateAction(BaseModel):
    target: str
    result: str

    def __repr__(self):
        return self.result

    __str__ = __repr__


class GameState(BaseModel):
    day: int = 0
    phase: str = "night"
    players: Dict[str, PlayerInfo] = {}
    chat_logs: Dict[str, List[ChatLogEntry]] = {}
    eliminations: List[str] = []
    mafia_target: str = None
    investigation_history: List[InvestigateAction] = []
    protections: List[str] = []


class ConversationState:
    def __init__(self, agents):
        self.decisions = {agent.name: None for agent in agents}
        self.rounds = 0

    def update_decision(self, agent_name, decision):
        """Update the decision of an agent."""
        self.decisions[agent_name] = decision

    def check_consensus(self):
        """Check if all agents have selected the same user."""
        values = list(self.decisions.values())
        if None in values:
            return False, None  # Not all agents have made a decision
        counter = Counter(values)
        most_common = counter.most_common(1)[0]  # Get the most common decision
        if most_common[1] == len(self.decisions):
            return True, most_common[0]  # Consensus reached
        return False, None  # No consensus yet

    def print_state(self):
        print(f"Current Decisions: {self.decisions}")

    def clear(self):
        self.decisions = None
        self.rounds = 0
