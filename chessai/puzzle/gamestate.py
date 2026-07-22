import copy
import typing

import edq.util.serial

import chessai.chess.piece
import chessai.chess.gamestate
import chessai.core.action
import chessai.core.board
import chessai.core.gamestate
import chessai.core.parser
import chessai.core.types
import chessai.puzzle.parser

class GameState(chessai.chess.gamestate.GameState):
    """ A game state specific to a Puzzle game. """

    def __init__(self,
                 board: chessai.core.board.Board,
                 turn: chessai.core.types.Color,
                 castling_rights: chessai.core.castling.CastlingRights,
                 en_passant_coordinate: chessai.core.coordinate.Coordinate | None = None,
                 halfmove_clock: int = 0,
                 fullmove_number: int = 1,
                 previous_action: chessai.core.action.Action | None = None,
                 seed: int = -1,
                 game_over: bool = False,
                 puzzle_solved: bool = False,
                 _capture_move_lines: bool = False,
                 **kwargs: typing.Any) -> None:
        super().__init__(board, turn, castling_rights, en_passant_coordinate,
                         halfmove_clock, fullmove_number, previous_action,
                         seed, game_over, **kwargs)

        self.puzzle_solved: bool = puzzle_solved
        """ Set to True when the agent has successfully completed one of the move lines. """

        self.dummy_player: chessai.core.types.Color = self.turn.opposite()
        """ The dummy player for the current game, which is the opponent to the puzzle's starting player. """

        if _capture_move_lines:
            move_lines = kwargs.get(chessai.puzzle.parser.MOVE_LINES_KEY, [])
        else:
            move_lines = []

        self._move_lines: list[list[chessai.core.action.Action]] = move_lines
        """ The move lines for the puzzle. """

    def game_complete(self) -> tuple[list[chessai.core.types.Color], float]:
        """
        Determine the outcome of the puzzle.

        The puzzle agent wins with score 1.0 if they fully completed one of the valid move lines.
        Otherwise the agent loses with score 0.0.
        """

        agent = self.dummy_player.opposite()

        if self.puzzle_solved:
            return ([agent], 1.0)

        return ([self.dummy_player], 0.0)

    def copy(self,
            context: typing.Union[edq.util.serial.SerializationContext, None] = None,
            ) -> 'GameState':
        new_state = super().copy()
        new_state = typing.cast(GameState, new_state)

        new_state.puzzle_solved = self.puzzle_solved
        new_state._move_lines = copy.deepcopy(self._move_lines)

        return new_state

    @classmethod
    def get_gamestate_parser(cls) -> chessai.core.parser.GameStateParser:
        return chessai.puzzle.parser.parse_puzzle
