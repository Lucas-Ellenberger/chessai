"""
The core actions that agents are allowed to take.
Default actions are provided, but custom actions can be easily created.
"""

import abc
import json
import re
import typing

import edq.util.json

import chessai.core.coordinate
import chessai.core.piece
import chessai.core.types

ACTION_PATTERN: re.Pattern = re.compile(r'^([a-z]+\d+)([a-z]+\d+)([a-zA-Z]?)$')
ACTION_KEY: str = 'actions'

UCI_ACCEPT_DRAW_ACTION: str = 'Accept Draw'
UCI_FORFEIT_ACTION: str = 'Forfeit'
UCI_NULL_ACTION: str = '0000'
UCI_PROPOSE_DRAW_ACTION: str = 'Propose Draw'
UCI_REJECT_DRAW_ACTION: str = 'Reject Draw'

class Action(abc.ABC, edq.util.json.DictConverter):
    """
    The base for all actions that an agent is allowed to take.

    Actions are an immutable class, so do not change attributes after construction.

    Actions are strings in the Chess UCI format
    (https://en.wikipedia.org/wiki/Universal_Chess_Interface).
    """

    @abc.abstractmethod
    def uci(self) -> str:
        """ Represent the agent action as a chess move in UCI format. """

    def __lt__(self, other: object) -> bool:
        if (not isinstance(other, Action)):
            raise TypeError(f"Cannot compare an action with an object of type '{type(other)}'.")

        return self._type_order() < other._type_order()

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, Action)):
            return False

        return type(self) == type(other)

    def __str__(self) -> str:
        return self.uci()

    def __repr__(self) -> str:
        return self.uci()

    def _type_order(self) -> int:
        """ Returns the ordering of the type. """

        return _ACTION_TYPE_ORDER[type(self)]

class NoneAction(Action):
    """ An action that signifies nothing happened. """

    def uci(self) -> str:
        return UCI_NULL_ACTION

class MoveAction(Action):
    """ Actions that move a piece from one coordinate to another. """

    def __init__(self,
                 start_coordinate: chessai.core.coordinate.Coordinate,
                 end_coordinate: chessai.core.coordinate.Coordinate,
                 ) -> None:
        super().__init__()

        self.start_coordinate: chessai.core.coordinate.Coordinate = start_coordinate
        """ The starting coordinate for the action. """

        self.end_coordinate: chessai.core.coordinate.Coordinate = end_coordinate
        """ The ending coordinate for the action. """

    def uci(self) -> str:
        start = self.start_coordinate.uci()
        end = self.end_coordinate.uci()

        return f"{start}{end}"

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, MoveAction)):
            return False

        return ((self.start_coordinate == other.start_coordinate) and (self.end_coordinate == other.end_coordinate))

    def __lt__(self, other: object) -> bool:
        if (not isinstance(other, Action)):
            raise TypeError(f"Cannot compare an action with an object of type '{type(other)}'.")

        if isinstance(other, MoveAction):
            if (self.start_coordinate < other.start_coordinate):
                return True

            if ((self.start_coordinate == other.start_coordinate) and (self.end_coordinate < other.end_coordinate)):
                return True

            return False

        return self._type_order() < other._type_order()

class PromotionAction(MoveAction):
    """ Actions that move a piece and promote it to another piece type. """

    def __init__(self,
                 start_coordinate: chessai.core.coordinate.Coordinate,
                 end_coordinate: chessai.core.coordinate.Coordinate,
                 promotion: chessai.core.piece.Piece,
                 ) -> None:
        super().__init__(start_coordinate, end_coordinate)

        self.promotion: chessai.core.piece.Piece = promotion
        """ The piece to promote to, or None if this is not a promotion move. """

    def uci(self) -> str:
        movement_uci = super().uci()
        promotion = self.promotion.symbol()

        return f"{movement_uci}{promotion}"

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, PromotionAction)):
            return False

        return (self.start_coordinate, self.end_coordinate, self.promotion) == (other.start_coordinate, other.end_coordinate, other.promotion)

    def __lt__(self, other: object) -> bool:
        if (not isinstance(other, Action)):
            raise TypeError(f"Cannot compare an action with an object of type '{type(other)}'.")

        if isinstance(other, PromotionAction):
            return (self.start_coordinate, self.end_coordinate, self.promotion) < (other.start_coordinate, other.end_coordinate, other.promotion)

        return self._type_order() < other._type_order()

class MetaAction(Action):
    """
    Meta actions for inter-agent communication regarding non-standard actions.

    Meta actions include handling draws and forfeits.
    """

class ProposeDrawAction(MetaAction):
    """ A meta action signaling the agent is offering a draw. """

    def uci(self) -> str:
        return UCI_PROPOSE_DRAW_ACTION

class AcceptDrawAction(MetaAction):
    """ A meta action responding to a draw proposal with an acceptance. """

    def uci(self) -> str:
        return UCI_ACCEPT_DRAW_ACTION

class RejectDrawAction(MetaAction):
    """ A meta action responding to a draw proposal with a rejection. """

    def uci(self) -> str:
        return UCI_REJECT_DRAW_ACTION

class ForfeitAction(MetaAction):
    """ A meta action signaling the agent is forfeiting the game. """

    def uci(self) -> str:
        return UCI_FORFEIT_ACTION

def from_uci(uci: str) -> Action:
    """
    Parse a UCI string into the appropriate Action.
    """

    if (uci == UCI_NULL_ACTION):
        return NoneAction()

    if (uci == UCI_PROPOSE_DRAW_ACTION):
        return ProposeDrawAction()

    if (uci == UCI_ACCEPT_DRAW_ACTION):
        return AcceptDrawAction()

    if (uci == UCI_REJECT_DRAW_ACTION):
        return RejectDrawAction()

    if (uci == UCI_FORFEIT_ACTION):
        return ForfeitAction()

    match = ACTION_PATTERN.fullmatch(uci)
    if (match is None):
        raise ValueError("An action must be a pair of coordinates with an optional promotion piece:"
                        + f" '{ACTION_PATTERN.pattern}', got: '{uci}'.")

    start_coordinate = chessai.core.coordinate.Coordinate.from_uci(match.group(1))
    end_coordinate = chessai.core.coordinate.Coordinate.from_uci(match.group(2))

    tail = match.group(3)
    if (len(tail) == 1):
        if (tail not in chessai.core.piece.get_registered_piece_symbols()):
            raise ValueError(f"Unknown promotion piece symbol '{tail}' in UCI string: '{uci}'.")

        promotion = chessai.core.piece.get_registered_piece(tail)
        return PromotionAction(start_coordinate, end_coordinate, promotion)

    return MoveAction(start_coordinate, end_coordinate)

def actions_list_from_dict(data: dict[str, typing.Any]) -> list[list[Action]]:
    """
    Get a list of a list of actions from a dictionary.
    The 'actions' key will be checked.
    """

    raw_actions = data.get(ACTION_KEY, None)
    if (raw_actions is None):
        return []

    str_actions_lists: list[list[str]] = json.loads(raw_actions)

    clean_actions: list[list[Action]] = []
    for str_action_list in str_actions_lists:
        clean_action_list = []
        for str_action in str_action_list:
            clean_action_list.append(from_uci(str_action))

        clean_actions.append(clean_action_list)

    return clean_actions

_ACTION_TYPE_ORDER: dict[typing.Type[Action], int] = {
    NoneAction: 0,
    MoveAction: 1,
    PromotionAction: 2,
    ProposeDrawAction: 3,
    AcceptDrawAction: 4,
    RejectDrawAction: 5,
    ForfeitAction: 6,
}
