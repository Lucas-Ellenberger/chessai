import os
import re
import typing

import edq.util.json

import chessai.core.action
import chessai.core.board
import chessai.core.castling
import chessai.core.coordinate
import chessai.core.piece
import chessai.core.types

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))
BOARDS_DIR: str = os.path.join(THIS_DIR, '..', 'resources', 'boards')

FEN_FILE_EXTENSION = '.fen'

# FEN parsing patterns.
DIMENSIONS_PATTERN: re.Pattern = re.compile(r'^#(\d+)x(\d+)$')

class ParsedGameState:
    """
    The parsed information that can be used to create a GameState.

    By default, the gamestate is parsed from a FEN or a filepath that only contains a FEN.

    FEN format:
    [#<files>x<ranks>] <pieces> <turn> <castling> <en-passant> <halfmove-clock> <fullmove-number>

    dimensions   -- optional '#<files>x<ranks>' (e.g. '#8x8'); defaults to 8x8 if omitted
    pieces       -- ranks 8..1, files a..h; '/' separates ranks; digits = empty coordinates
    turn         -- 'w' or 'b'
    castling     -- 'KQkq' subset or '-'
    en-passant   -- target coordinate in algebraic notation or '-'
    halfmove     -- integer
    fullmove     -- integer (starts at 1, increments after Black's move)

    The dimensions field is a chessai extension and is not part of the standard FEN spec.
    Standard FEN strings (6 fields) are accepted without modification.

    See: https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation .
    """

    __slots__ = (
        'pieces',
        'turn',
        'castling_rights',
        'en_passant_coordinate',
        'halfmove_clock',
        'fullmove_number',
        'num_files',
        'num_ranks',
        'options',
    )

    def __init__(self,
            pieces: dict[chessai.core.coordinate.Coordinate, chessai.core.piece.Piece],
            turn: chessai.core.types.Color,
            castling_rights: chessai.core.castling.CastlingRights,
            en_passant_coordinate: chessai.core.coordinate.Coordinate | None,
            halfmove_clock: int,
            fullmove_number: int,
            num_files: int = chessai.core.board.DEFAULT_BOARD_FILES,
            num_ranks: int = chessai.core.board.DEFAULT_BOARD_RANKS,
            options: dict[str, typing.Any] | None = None,
            ) -> None:
        self.pieces: dict[chessai.core.coordinate.Coordinate, chessai.core.piece.Piece] = pieces
        """ The position of the pieces on the board. """

        self.turn: chessai.core.types.Color = turn
        """ The current turn of the game. """

        self.castling_rights: chessai.core.castling.CastlingRights = castling_rights
        """ The available castling rights in the game. """

        self.en_passant_coordinate: chessai.core.coordinate.Coordinate | None = en_passant_coordinate
        """ The game's en-passant coordinate. """

        self.halfmove_clock: int = halfmove_clock
        """ The game's halfmove clock. """

        self.fullmove_number: int = fullmove_number
        """ The game's fullmove number. """

        self.num_files: int = num_files
        """ The number of files in the FEN. """

        self.num_ranks: int = num_ranks
        """ The number of ranks found in the FEN. """

        if (options is None):
            options = {}

        self.options: dict[str, typing.Any] = options
        """ Any additional options found in the FEN. """

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ParsedGameState):
            raise ValueError(f"Cannot compare equality of a ParsedGameState with an object of another type: '{type(other)}'.")

        return (
            self.pieces == other.pieces and
            self.turn == other.turn and
            self.castling_rights == other.castling_rights and
            self.en_passant_coordinate == other.en_passant_coordinate and
            self.halfmove_clock == other.halfmove_clock and
            self.fullmove_number == other.fullmove_number and
            self.num_files == other.num_files and
            self.num_ranks == other.num_ranks
        )

@typing.runtime_checkable
class GameStateStringParser(typing.Protocol):
    """
    A function that parses a filepath into the necessary information for a GameState to be constructed.

    Not every game type will neeed a custom GameStateParser,
    unless they do not conform to the defualt parser.
    """

    def __call__(self,
                 text: str,
                 **kwargs: typing.Any) -> ParsedGameState:
        ...

@typing.runtime_checkable
class GameStateParser(typing.Protocol):
    """
    A function that parses a filepath into the necessary information for a GameState to be constructed.

    Not every game type will neeed a custom GameStateParser,
    unless they do not conform to the defualt parser.
    """

    def __call__(self,
                 data: str,
                 default_dir: str,
                 default_extension: str,
                 string_parser: GameStateStringParser,
                 accepts_raw_string: bool = False,
                 options: dict[str, typing.Any] | None = None,
                 **kwargs: typing.Any) -> ParsedGameState:
        ...

def load_fen_from_string(text: str, **kwargs: typing.Any) -> ParsedGameState:
    """ Load a FEN string from a string. """

    fields = text.strip().split()
    if (len(fields) not in (6, 7)):
        raise ValueError(f"FEN must have 6 or 7 fields, found '{len(fields)}': '{text}'.")

    num_files = chessai.core.board.DEFAULT_BOARD_FILES
    num_ranks = chessai.core.board.DEFAULT_BOARD_RANKS

    if (len(fields) == 7):
        (num_files, num_ranks) = _parse_fen_dimensions(fields.pop(0))

    pieces          = _parse_fen_pieces(fields[0], num_files, num_ranks)
    turn            = _parse_fen_turn(fields[1])
    castling_rights = chessai.core.castling.CastlingRights.from_fen_string(fields[2])
    en_passant      = _parse_fen_en_passant(fields[3])
    halfmove_clock  = _parse_int_field(fields[4], 'halfmove clock', min_value = 0)
    fullmove_number = _parse_int_field(fields[5], 'fullmove number', min_value = 1)

    return ParsedGameState(
        pieces                = pieces,
        turn                  = turn,
        castling_rights       = castling_rights,
        en_passant_coordinate = en_passant,
        halfmove_clock        = halfmove_clock,
        fullmove_number       = fullmove_number,
        num_files             = num_files,
        num_ranks             = num_ranks,
        options               = kwargs,
    )

def parse_fen(data: str,
              default_dir: str = BOARDS_DIR,
              default_extension: str = FEN_FILE_EXTENSION,
              string_parser: GameStateStringParser = load_fen_from_string,
              accepts_raw_string: bool = True,
              options: dict[str, typing.Any] | None = None,
              **kwargs: typing.Any) -> ParsedGameState:
    """
    Parse a FEN string into a ParsedGameState.

    Accepts standard 6-field FEN strings as well as the chessai extended
    7-field format with an optional '#<files>x<ranks>' dimensions field.

    Raises ValueError if the FEN is malformed.

    See https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation .
    """

    # Check if this might be directly parseable.
    if (accepts_raw_string and (' ' in data.strip())):
        # Parse the data directly.
        return string_parser(data, options = options, **kwargs)

    # Otherwise, load from a path.
    return load_from_path(
        data,
        default_dir       = default_dir,
        default_extension = default_extension,
        string_parser     = string_parser,
        **kwargs,
    )

def load_from_path(path: str,
                   default_dir: str = BOARDS_DIR,
                   default_extension: str = FEN_FILE_EXTENSION,
                   string_parser: GameStateStringParser = load_fen_from_string,
                   **kwargs: typing.Any) -> ParsedGameState:
    """
    Load a FEN string from a file.

    If the given path does not exist,
    try to prefix the path with the standard board directory and suffix with the standard extension.
    """

    raw_path = path

    # If the path does not exist, try the boards directory.
    if (not os.path.exists(path)):
        path = os.path.join(default_dir, path)

        # If this path does not have a good extension, add one.
        if (os.path.splitext(path)[-1] != default_extension):
            path = path + default_extension

    if (not os.path.exists(path)):
        raise ValueError(f"Could not find {default_extension} file, path does not exist: '{raw_path}'.")

    text = edq.util.dirent.read_file(path, strip = False)
    return string_parser(text, **kwargs)

def serialize_fen(
        board: chessai.core.board.Board,
        turn: chessai.core.types.Color,
        castling_rights: chessai.core.castling.CastlingRights,
        en_passant_coordinate: chessai.core.coordinate.Coordinate | None,
        halfmove_clock: int,
        fullmove_number: int,
        partial: bool = False,
        ) -> str:
    """
    Serialize game state fields back into a FEN string.

    For standard 8x8 boards the dimensions field is omitted,
    producing a standard FEN string.
    For non-standard board sizes the chessai dimensions extension is prepended.

    Partial serializations exclude the clock and move number.
    """

    piece_field = board.to_fen_piece_field()

    if (turn == chessai.core.types.Color.WHITE):
        turn_field = 'w'
    else:
        turn_field = 'b'

    castling_field = castling_rights.to_fen_string()

    if (en_passant_coordinate is not None):
        ep_field = en_passant_coordinate.uci()
    else:
        ep_field = '-'

    if (partial):
        # Produce an augmented FEN, which is useful for comparing pseudo-unique gamestates.
        return f"{piece_field} {turn_field} {castling_field} {ep_field}"

    is_standard_size = (
        (board.num_files == chessai.core.board.DEFAULT_BOARD_FILES)
        and (board.num_ranks == chessai.core.board.DEFAULT_BOARD_RANKS)
    )

    if (not is_standard_size):
        board_field = f"#{board.num_files}x{board.num_ranks} "
    else:
        board_field = ''

    # Produce a standard FEN.
    return f"{board_field}{piece_field} {turn_field} {castling_field} {ep_field} {halfmove_clock} {fullmove_number}"

def _parse_fen_dimensions(dimensions_field: str) -> tuple[int, int]:
    """
    Parse the optional chessai dimensions field '#<files>x<ranks>'.

    Returns a (num_files, num_ranks) tuple.
    Raises ValueError if the field is malformed or contains non-positive values.
    """

    match = DIMENSIONS_PATTERN.fullmatch(dimensions_field)
    if (match is None):
        raise ValueError(
            "FEN dimensions field must be '#<files>x<ranks>' (e.g. '#8x8'),"
            + f" got: '{dimensions_field}'."
        )

    num_files = int(match.group(1))
    num_ranks = int(match.group(2))

    if (num_files < 1):
        raise ValueError(f"FEN dimensions num_files must be >= 1, got: {num_files}.")

    if (num_ranks < 1):
        raise ValueError(f"FEN dimensions num_ranks must be >= 1, got: {num_ranks}.")

    return (num_files, num_ranks)

def _parse_fen_pieces(
            piece_field: str,
            num_files: int = chessai.core.board.DEFAULT_BOARD_FILES,
            num_ranks: int = chessai.core.board.DEFAULT_BOARD_RANKS,
        ) -> dict[chessai.core.coordinate.Coordinate, chessai.core.piece.Piece]:
    """
    Parse the piece-placement field of a FEN string.

    FEN ranks are ordered 8..1 (rank 8 is first), files a..h left-to-right.
    """

    ranks = piece_field.split('/')
    if (len(ranks) != num_ranks):
        raise ValueError(
            f"FEN piece field must have {num_ranks} ranks"
            + f" separated by '/', found '{len(ranks)}': '{piece_field}'."
        )

    known_piece_symbols = chessai.core.piece.get_registered_piece_symbols()
    pieces: dict[chessai.core.coordinate.Coordinate, chessai.core.piece.Piece] = {}

    # A regular expression to find series of digits (empty squares) and pieces, which are each a single non-digit character.
    fen_token_re = re.compile(r'\d+|[^\d]')

    for (rank_index, rank_str) in enumerate(ranks):
        # FEN rank 8 is index 0 in the string, which is rank 7 in [0, 7].
        rank = (num_ranks - 1) - rank_index
        file = 0

        for fen_token in fen_token_re.findall(rank_str):
            if (fen_token.isdigit()):
                file += int(fen_token)
            elif (fen_token in known_piece_symbols):
                if (file >= num_files):
                    raise ValueError(f"Too many pieces on rank {rank + 1} in FEN: '{rank_str}'.")

                coordinate = chessai.core.coordinate.Coordinate(file, rank)
                pieces[coordinate] = chessai.core.piece.get_registered_piece(fen_token)
                file += 1
            else:
                raise ValueError(f"Unknown character '{fen_token}' in FEN piece field: '{rank_str}'.")

        if (file != num_files):
            raise ValueError(
                f"Rank {rank + 1} has {file} files, expected"
                + f" {num_files}: '{rank_str}'."
            )

    return pieces

def _parse_fen_turn(turn_field: str) -> chessai.core.types.Color:
    if (turn_field == 'w'):
        return chessai.core.types.Color.WHITE

    if (turn_field == 'b'):
        return chessai.core.types.Color.BLACK

    raise ValueError(f"FEN turn field must be 'w' or 'b', found: '{turn_field}'.")

def _parse_fen_en_passant(ep_field: str) -> chessai.core.coordinate.Coordinate | None:
    if (ep_field == '-'):
        return None

    try:
        return chessai.core.coordinate.Coordinate.from_uci(ep_field)
    except Exception as exc:
        raise ValueError(f"Invalid FEN en-passant field: '{ep_field}'.") from exc

def _parse_int_field(raw: str, label: str, min_value: int = 0) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"FEN {label} must be an integer, found: '{raw}'.") from exc

    if (value < min_value):
        raise ValueError(f"FEN {label} must be >= {min_value}, found: '{value}'.")

    return value
