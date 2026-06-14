import dataclasses
import enum
import typing

import edq.util.json

import chessai.core.coordinate
import chessai.core.types

class MoveKind(enum.Enum):
    """ An enum to encode the types of movement. """

    NORMAL  = 'Normal'
    """ Standard move, capable of capture and movement. """

    CAPTURE = 'Capture'
    """ Movement that can only be done if it captures a piece. """

    PUSH    = 'Push'
    """ Movement that can only be used to move, not capture. """

@dataclasses.dataclass(frozen = True)
class MoveVector:
    """
    A movement rule for a piece.
    If slides is True, then the vector can be repeated until the piece captures or the end of the board.
    """

    file_delta: int
    """ The direction of the movement on the file. """

    rank_delta: int
    """ The direction of the movement on the rank. """

    num_repetitions: int = 1
    """
    The number of times this movement can be repeated.
    Use -1 if this move can be repeated infinitely.
    """

    kind: MoveKind = MoveKind.NORMAL
    """ Determines if the movement is used for movement, capture, or both. """

class Piece(edq.util.json.DictConverter):
    """ A piece with a team color and movement rules. """

    def __init_subclass__(cls, symbols: tuple[str, ...] = (), **kwargs: typing.Any):
        """ Register piece subclasses so core functions can find them. """

        super().__init_subclass__(**kwargs)
        for symbol in symbols:
            register_piece(symbol, cls)

    def __init__(self,
                 color: chessai.core.types.Color) -> None:
        self.color: chessai.core.types.Color = color
        """ The team color that this piece belongs to. """

    def move_vectors(self) -> list[MoveVector]:
        """ Returns the movement vectors for this piece. """

        return []

    def symbol(self) -> str:
        """
        Gets the symbol for the piece.
        Upper-case symbols are white pieces and lower-case symbols are black pieces.
        """

        return ''

    def unicode_symbol(self) -> str:
        """ Gets the Unicode character for the piece. """

        return ''

    def __lt__(self, other: object) -> bool:
        if (not isinstance(other, Piece)):
            raise ValueError(f"Cannot compare a piece with an object of type '{type(other)}'.")

        return (self.symbol() < other.symbol())

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, Piece)):
            return False

        return (self.symbol() == other.symbol())

    def __hash__(self) -> int:
        return hash((self.symbol()))

    def __repr__(self) -> str:
        return f"Piece.from_symbol({self.symbol()!r})"

    def __str__(self) -> str:
        return self.symbol()

_PIECE_REGISTRY: dict[str, type['Piece']] = {}

def register_piece(symbol: str, piece_class: type['Piece']) -> None:
    """ Register a piece class with its symbol. """

    if symbol in _PIECE_REGISTRY:
        raise ValueError(f"Piece symbol '{symbol}' is already registered.")

    _PIECE_REGISTRY[symbol] = piece_class

def get_registered_piece_symbols() -> set[str]:
    """ Get all registered piece symbols. """

    return set(_PIECE_REGISTRY.keys())

def get_registered_piece(symbol: str) -> 'Piece':
    """ Create a piece instance from a symbol. """

    if symbol not in _PIECE_REGISTRY:
        raise ValueError(f"Unknown piece symbol: '{symbol}'")

    # Determine color from symbol case.
    if (symbol.isupper()):
        color = chessai.core.types.Color.WHITE
    else:
        color = chessai.core.types.Color.BLACK

    return _PIECE_REGISTRY[symbol](color = color)

def clear_registry() -> None:
    """ Clear the piece registry. """

    _PIECE_REGISTRY.clear()
