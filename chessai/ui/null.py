import typing

import chessai.core.board
import chessai.core.gamestate
import chessai.core.ui

class NullUI(chessai.core.ui.UI):
    """
    A UI that renders nothing.
    This is useful when are more interested in the output of the game
    (e.g., the log or gif) than seeing the actual game.
    """

    def draw(self, state: chessai.core.gamestate.GameState, **kwargs: typing.Any) -> None:
        pass
