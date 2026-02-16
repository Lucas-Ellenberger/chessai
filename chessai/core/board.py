import io
import typing

import edq.util.json

import chess
import chess.pgn

# TODO(Lucas): Continue adding the necessary methods for students to interact with the board.
class Board(edq.util.json.DictConverter):
    """
    The board for all chess games in chessai.
    A board holds the current state and history of the game.

    Boards should only be interacted with via their methods and not their member variables.
    """

    def __init__(self,
                 start_fen: str = chess.STARTING_FEN) -> None:
        self._board = chess.Board(start_fen)
        """ The current board which stores the current state and the history. """

    def get_turn(self) -> bool:
        """ The side to move (chess.WHITE or chess.BLACK). """
        return self._board.turn

    def get_fullmove_number(self) -> int:
        """ Counts move pairs. Starts at 1 and is incremented after every move of the black side. """
        return self._board.fullmove_number

    def get_legal_moves(self) -> chess.LegalMoveGenerator:
        """ Returns a dynamic list of the legal moves. """
        return self._board.legal_moves

    def get_fen(self) -> str:
        """ Gets a FEN representation of the current board position. """
        return self._board.fen()

    def get_pieces(self,
                   piece_type: chess.PieceType,
                   color: chess.Color) -> chess.SquareSet:
        """ Gets the pieces of the given type and color. """
        return self._board.pieces(piece_type, color)

    def get_outcome(self) -> chess.Outcome | None:
        """ Gets the outcome of the game if it is over. """
        return self._board.outcome()

    def is_game_over(self) -> bool:
        """ Returns if the game is over. """
        return self._board.is_game_over()

    def is_capture(self, move: chess.Move) -> bool:
        """ Returns if the move captures a piece. """
        return self._board.is_capture(move)

    def _push(self, move: chess.Move) -> None:
        """ Updates the position with the given move and puts it onto the move stack. """
        return self._board.push(move)

    def copy(self) -> 'Board':
        """ Create a deep copy of the board. """
        instance = self.__class__.__new__(self.__class__)
        instance._board = self._board.copy()
        return instance

    def to_pgn(self) -> str:
        """Serialize the board's game history to a PGN string."""
        game = chess.pgn.Game.from_board(self._board)
        exporter = chess.pgn.StringExporter()
        return game.accept(exporter)

    @classmethod
    def from_pgn(cls, pgn_string: str) -> 'Board':
        """ Reconstruct a Board from a PGN string, restoring the full move history. """
        instance = cls.__new__(cls)

        game = chess.pgn.read_game(io.StringIO(pgn_string))
        if (game is None):
            raise ValueError(f"Unable to read PGN of board: '{pgn_string}'.")

        # Replay the move history to get the current position.
        board = game.board()
        for move in game.mainline_moves():
            board.push(move)

        instance._board = board
        return instance

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'pgn': self.to_pgn(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return cls.from_pgn(data.get('pgn', ''))
