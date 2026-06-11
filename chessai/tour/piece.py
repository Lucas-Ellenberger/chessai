import chessai.core.coordinate
import chessai.core.piece
import chessai.core.types

UNICODE_PIECE_SYMBOLS: dict[str, str] = {
    "o": "⚫", "O": "⚪",
}

class Rock(chessai.core.piece.Piece, symbols = ('O', 'o')):
    """ The rock piece in tour, which cannot move or be captured. """

    _move_vectors: list[chessai.core.piece.MoveVector] = []

    def symbol(self) -> str:
        if (self.color == chessai.core.types.Color.WHITE):
            return 'O'

        return 'o'

    def unicode_symbol(self) -> str:
        return UNICODE_PIECE_SYMBOLS[self.symbol()]

    def move_vectors(self) -> list[chessai.core.piece.MoveVector]:
        return self._move_vectors
