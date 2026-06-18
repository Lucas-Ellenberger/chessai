import sys
import typing

import chessai.core.gamestate
import chessai.core.piece
import chessai.core.ui

DEFAULT_PADDING_SIZE: int = 1
""" The default number of padding spaces between each piece and the square border. """

class TextUI(chessai.core.ui.UI):
    """
    A simple UI that renders the game to a text stream.
    This UI will be simple and generally meant for debugging.
    """

    SYMBOL_SIZE: int = 2
    """
    The space reserved to display the symbols.
    Pieces represent themselves as unicode symbols, which often take two spaces.
    """

    def __init__(self,
            output_stream: typing.TextIO,
            padding_size: int = DEFAULT_PADDING_SIZE,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        self._output_stream: typing.TextIO = output_stream
        """ The stream output will be sent to. """

        self._padding_size: int = padding_size
        """ The number of padding spaces between each piece and the square border. """

        self._cell_width: int = self.SYMBOL_SIZE
        """ The width of an individual cell, including the padding and symbol sizes. """

        self._file_labels: str | None = None
        """ The file labels to be displayed at the bottom of the board. """

        self._horizontal_border: str | None = None
        """ The horizontal border to be displayed between each rank. """

    def draw(self, state: chessai.core.gamestate.GameState, check_game_over: bool = False, **kwargs: typing.Any) -> None:
        if (state.get_previous_action() == chessai.core.action.NoneAction()):
            return

        # Draw the top border.
        self._output_stream.write(self._get_horizontal_border(state))

        prefix_padding_size = self._get_prefix_padding_size(state)

        for rank in range((state.board.num_ranks - 1), -1, -1):
            rank_str = str(rank + 1)
            rank_padding_size = prefix_padding_size - len(rank_str)
            rank_padding = ' ' * rank_padding_size

            line = f"{rank_str}{rank_padding}{self._get_padding()}|"

            for file in range(state.board.num_files):
                piece_symbol = self._translate_piece(state.board.get(file, rank))
                line += f"{piece_symbol}|"

            self._output_stream.write(line + "\n")
            self._output_stream.write(self._get_horizontal_border(state))

        self._output_stream.write(self._get_file_labels(state))

        # Display the most recent action.
        action = state.get_previous_action()
        if (action is not None):
            self._output_stream.write(f"Previous action: '{action}'.\n")

        if ((state.game_over) or (check_game_over and (state.is_game_over()))):
            self._output_stream.write('Game Over!\n')
            self._output_stream.write(f"Termination Reason: '{state.get_termination_reason()}'.\n")

        self._output_stream.write('\n')
        self._output_stream.flush()

    def _get_padding(self) -> str:
        """ Get the padding for this UI. """

        return " " * self._padding_size

    def _get_prefix_padding(self, state: chessai.core.gamestate.GameState) -> str:
        """
        Get the initial padding for rows without a column numbering,
        such as the horizontal border and the file labels.
        """

        prefix_padding_size = self._get_prefix_padding_size(state)

        prefix_padding = ' ' * prefix_padding_size

        return f"{prefix_padding}{self._get_padding()}"


    def _get_prefix_padding_size(self, state: chessai.core.gamestate.GameState) -> int:
        """ Get the size of the prefix padding to account for the rank labels. """

        prefix_padding_size = 1
        num_ranks = state.board.num_ranks

        while (num_ranks >= 10):
            prefix_padding_size += 1
            num_ranks = num_ranks // 10

        return prefix_padding_size

    def _get_horizontal_border(self, state: chessai.core.gamestate.GameState) -> str:
        """ Get the horizontal border for the UI. """

        if (self._horizontal_border is not None):
            return self._horizontal_border

        dash_segment = '-' * self._cell_width + '+'

        horizontal_border = f"{self._get_prefix_padding(state)}+" + (dash_segment * state.board.num_files) + '\n'

        # Cache the horizontal border for subsequent calls.
        self._horizontal_border = horizontal_border

        return self._horizontal_border

    def _get_file_labels(self, state: chessai.core.gamestate.GameState) -> str:
        """ Get the labels of the files for the bottom of the board. """

        if (self._file_labels is not None):
            return self._file_labels

        file_labels = self._get_prefix_padding(state)
        for file in range(state.board.num_files):
            # Use a coordinate to get the file name.
            coordinate = chessai.core.coordinate.Coordinate(file, 0)

            file_str = coordinate.uci(only_file = True)
            file_labels += f"{self._get_padding()}{file_str}{self._get_padding()}"

        file_labels += '\n'

        # Cache the file labels for subsequent calls to the UI.
        self._file_labels = file_labels

        return file_labels

    def _translate_piece(self, piece: chessai.core.piece.Piece | None) -> str:
        """
        Convert a piece to a string.
        This can be trivial (since a piece knows how to represent itself as a string),
        but this allows children to implement special conversions.
        """

        if (piece is None):
            return ' ' * self.SYMBOL_SIZE

        return piece.unicode_symbol().center(self.SYMBOL_SIZE)

class StdioUI(TextUI):
    """
    A convenience class for a TextUI using stdout.
    """

    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(sys.stdout, **kwargs)
