from pydantic import BaseModel, Field
from typing import List, Dict, Union


class ActionResponse(BaseModel):
    """
    A Response to a prompt that requires selecting a player and providing an explanation
    """

    player_name: str = Field(..., description="The name of the player")
    message: str = Field(
        ..., description="Your explanation behind your choice of player"
    )


class ConversationalResponse(BaseModel):
    """
    A Response to a prompt that requires just a message
    """

    message: str = Field(..., description="The response to the prompt")


# NOTE: not working as expected, will circle back to this
class LLMResponse(BaseModel):
    output: Union[
        ConversationalResponse,
        ActionResponse,
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
    potential_mafia_targets: List[str] = []
    investigation_history: List[InvestigateAction] = []
    protections: List[str] = []
