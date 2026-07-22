"""
The core actions that agents are allowed to take.
Default actions are provided, but custom actions can be easily created.
"""

import re
import typing

import edq.util.json
import edq.util.serial

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

class Action(edq.util.serial.DictConverter):
    """
    The base for all actions that an agent is allowed to take.

    Actions are an immutable class, so do not change attributes after construction.

    Actions are strings in the Chess UCI format
    (https://en.wikipedia.org/wiki/Universal_Chess_Interface).
    """

    _type_order: typing.ClassVar[int]
    """
    The ordering of this action type.
    Child classes must choose a unique type number for their game.
    """

    # This function is meant to be an abc.abstractmethod,
    # but for performance reasons it raises an error.
    def uci(self) -> str:
        """ Represent the agent action as a chess move in UCI format. """

        raise NotImplementedError("Action.uci()")

    # Comparing actions with non-action objects raises an error.
    def __lt__(self, other: object) -> bool:
        return bool(self._type_order < other._type_order)  # type: ignore[attr-defined]  # pylint: disable=no-member

    # Comparing actions with non-action objects may raise an error.
    def __eq__(self, other: object) -> bool:
        return type(self) == type(other)

    def __str__(self) -> str:
        return self.uci()

    def __repr__(self) -> str:
        return self.uci()

class NoneAction(Action):
    """ An action that signifies nothing happened. """

    _type_order = 0

    def uci(self) -> str:
        return UCI_NULL_ACTION

class MoveAction(Action):
    """ Actions that move a piece from one coordinate to another. """

    _type_order = 1

    def __init__(self,
                 start_coordinate: chessai.core.coordinate.Coordinate,
                 end_coordinate: chessai.core.coordinate.Coordinate,
                 ) -> None:
        self.start_coordinate: chessai.core.coordinate.Coordinate = start_coordinate
        """ The starting coordinate for the action. """

        self.end_coordinate: chessai.core.coordinate.Coordinate = end_coordinate
        """ The ending coordinate for the action. """

    def uci(self) -> str:
        start = self.start_coordinate.uci()
        end = self.end_coordinate.uci()

        return f"{start}{end}"

    def __eq__(self, other: object) -> bool:
        if (type(self) != type(other)):
            return False

        return (self.start_coordinate, self.end_coordinate) == (other.start_coordinate, other.end_coordinate) # type: ignore[attr-defined]  # pylint: disable=no-member

    def __lt__(self, other: object) -> bool:
        if isinstance(other, MoveAction):
            return (self.start_coordinate, self.end_coordinate) < (other.start_coordinate, other.end_coordinate)

        return bool(self._type_order < other._type_order)  # type: ignore[attr-defined]  # pylint: disable=no-member

class PromotionAction(MoveAction):
    """ Actions that move a piece and promote it to another piece type. """

    _type_order = 2

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
        if isinstance(other, PromotionAction):
            return (self.start_coordinate, self.end_coordinate, self.promotion) < (other.start_coordinate, other.end_coordinate, other.promotion)

        return bool(self._type_order < other._type_order)  # type: ignore[attr-defined]  # pylint: disable=no-member

class MetaAction(Action):
    """
    Meta actions for inter-agent communication regarding non-standard actions.

    Meta actions include handling draws and forfeits.
    """

    def uci(self) -> str:
        raise NotImplementedError("MetaAction.uci()")

class ProposeDrawAction(MetaAction):
    """ A meta action signaling the agent is offering a draw. """

    _type_order = 3

    def uci(self) -> str:
        return UCI_PROPOSE_DRAW_ACTION

class AcceptDrawAction(MetaAction):
    """ A meta action responding to a draw proposal with an acceptance. """

    _type_order = 4

    def uci(self) -> str:
        return UCI_ACCEPT_DRAW_ACTION

class RejectDrawAction(MetaAction):
    """ A meta action responding to a draw proposal with a rejection. """

    _type_order = 5

    def uci(self) -> str:
        return UCI_REJECT_DRAW_ACTION

class ForfeitAction(MetaAction):
    """ A meta action signaling the agent is forfeiting the game. """

    _type_order = 6

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

def process_raw_action_list(raw_action_list: str | dict[str, typing.Any]) -> list[list[Action]]:
    """ Convert raw move lines, from the CLI, into cleaned move lines. """

    if (isinstance(raw_action_list, dict)):
        raw_action_list = str(raw_action_list.get(ACTION_KEY, None))

    parsed_move_lines = edq.util.json.loads(raw_action_list)

    clean_move_lines: list[list[Action]] = []

    for line in parsed_move_lines:
        move_line = []
        for uci in line:
            move_line.append(from_uci(uci))

        clean_move_lines.append(move_line)

    return clean_move_lines
