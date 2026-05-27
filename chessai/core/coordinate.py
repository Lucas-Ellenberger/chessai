import re
import typing

COORDINATES_KEY: str = 'coordinates'

COORDINATE_PATTERN: re.Pattern = re.compile(r'([a-z]+)(\d+)')

class Coordinate(typing.NamedTuple):
    """
    An immutable chess coordinate on a board.

    File increases left-to-right (a=0, h=7).
    Rank increases bottom-to-top (1=0, 8=7).
    """

    file: int
    """ The file of the coordinate. """

    rank: int
    """ The rank of the coordinate. """

    @classmethod
    def from_uci(cls, uci: str) -> 'Coordinate':
        """ Construct a Coordinate from standard algebraic coordinate name. """

        match = re.fullmatch(COORDINATE_PATTERN, uci.lower())
        if (match is None):
            raise ValueError(f"Improper Coordinate name: '{uci}', expected '[a-z]+\\d+'.")

        raw_file, raw_rank = match.groups()

        # Convert base-26 string into an integer.
        file = 0
        for char in raw_file:
            file = (file * 26) + (ord(char) - ord('a') + 1)

        # Adjust the file to be 0-indexed.
        file -= 1

        # Adjust the rank to be 0-indexed.
        rank = int(raw_rank) - 1

        return cls(file, rank)

    def uci(self, only_file: bool = False, only_rank: bool = False) -> str:
        """ The standard algebraic name of this coordinate. """

        # Convert the integer coordinate to a base-26 string, switching to the 1-indexed format.
        file_num = self.file + 1
        file_chars = []

        while file_num > 0:
            file_num -= 1
            file_chars.append(chr(file_num % 26 + ord('a')))
            file_num //= 26

        file_str = ''.join(reversed(file_chars))
        rank_str = str(self.rank + 1)

        if (only_file):
            return file_str

        if (only_rank):
            return rank_str

        return f"{file_str}{rank_str}"

    def offset(self, file_delta: int, rank_delta: int) -> 'Coordinate':
        """ Return the coordinate reached by moving (file_delta, rank_delta) from this coordinate. """

        new_file = self.file + file_delta
        new_rank = self.rank + rank_delta

        return Coordinate(new_file, new_rank)

    def file_distance(self, other: 'Coordinate') -> int:
        """ The absolute difference in file between this coordinate and another. """

        return abs(self.file - other.file)

    def rank_distance(self, other: 'Coordinate') -> int:
        """ The absolute difference in rank between this coordinate and another. """

        return abs(self.rank - other.rank)

    def chebyshev_distance(self, other: 'Coordinate') -> int:
        """
        The Chebyshev distance (chessboard distance) between two coordinates.
        This is the minimum number of king moves to travel between them.

        Useful as a building block for heuristics.
        """

        return max(self.file_distance(other), self.rank_distance(other))

    def manhattan_distance(self, other: 'Coordinate') -> int:
        """
        The Manhattan distance between two coordinates.
        Note: this is NOT an admissible heuristic for knight movement,
        since a knight does not move in cardinal directions.
        Students should think carefully before using this in their heuristic.
        """

        return self.file_distance(other) + self.rank_distance(other)

    def __str__(self) -> str:
        return f"({self.file}, {self.rank})"

    def __repr__(self) -> str:
        return str(self)

    def to_dict(self) -> dict[str, typing.Any]:
        """ Convert the coordinate into a dictionary. """

        return {
            'file': self.file,
            'rank': self.rank,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> 'Coordinate':
        """ Create a coordinate from a dictionary of data. """

        return Coordinate(file = data['file'], rank = data['rank'])

def coordinates_from_dict(data: dict[str, typing.Any]) -> list[Coordinate]:
    """
    Get a list of coordinates from a dict.
    The 'coordinates' key will be checked.
    """

    clean_coordinates: list[Coordinate] = []

    raw_coordinates = data.get(COORDINATES_KEY, [])
    if (isinstance(raw_coordinates, str)):
        raw_coordinates = raw_coordinates.split(',')

    for raw_coordinate in raw_coordinates:
        clean_coordinate = None

        if (isinstance(raw_coordinate, dict)):
            clean_coordinate = Coordinate.from_dict(raw_coordinate)
        elif (isinstance(raw_coordinate, str)):
            clean_coordinate = Coordinate.from_uci(raw_coordinate)

        if (clean_coordinate is None):
            continue

        clean_coordinates.append(clean_coordinate)

    return clean_coordinates

NULL_COORDINATE = Coordinate(-1, -1)
