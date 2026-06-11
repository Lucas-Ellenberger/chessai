import dataclasses
import os
import typing

import edq.util.json

import chessai.core.coordinate
import chessai.core.parser

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))
TOURS_DIR: str = os.path.join(THIS_DIR, '..', 'resources', 'tours')

TOUR_FILE_EXTENSION: str = '.json'

SEARCH_TARGETS_KEY: str = 'search_targets'

@dataclasses.dataclass
class TourInfo:
    """ A simple dataclass to unpack tour data from JSON. """

    fen: str
    """ The starting FEN for the tour. """

    search_targets: list[str]
    """ The search targets to solve the tour. """

def parse_tour_from_string(text: str, **kwargs: typing.Any) -> chessai.core.parser.ParsedGameState:
    """ Load a tour from a string, which is expected to be JSON data. """

    # Extract the JSON data into the tour info.
    # print(text)
    data_dict = edq.util.json.loads(text)
    tour_info = TourInfo(**data_dict)

    # Use the default fen parsing.
    parsed_gamestate = chessai.core.parser.load_fen_from_string(text = tour_info.fen, **kwargs)

    search_targets: list[chessai.core.coordinate.Coordinate] = []
    for search_target in tour_info.search_targets:
        search_targets.append(chessai.core.coordinate.Coordinate.from_uci(search_target))

    # Add the search target information.
    parsed_gamestate.options[SEARCH_TARGETS_KEY] = search_targets

    return parsed_gamestate

def parse_tour(data: str,
               default_dir: str = TOURS_DIR,
               default_extension: str = TOUR_FILE_EXTENSION,
               string_parser: chessai.core.parser.GameStateStringParser = parse_tour_from_string,
               accepts_raw_string: bool = True,
               options: dict[str, typing.Any] | None = None,
               **kwargs: typing.Any) -> chessai.core.parser.ParsedGameState:
    """
    Parse a Tour GameState from a file path.

    If the filepath does not exist, the default directory and file extension are added.
    """

    return chessai.core.parser.parse_fen(data,
                                         default_dir = default_dir,
                                         default_extension = default_extension,
                                         string_parser = string_parser,
                                         accepts_raw_string = accepts_raw_string,
                                         **kwargs)
