import random
import typing

import chess

import chessai.core.gamestate

class GameState(chessai.core.gamestate.GameState):
    """ A game state specific to a standard Pacman game. """

    def process_turn(self,
            action: chess.Move,
            rng: random.Random | None = None,
            **kwargs: typing.Any) -> None:
        """
        Process the current agent's turn with the given action.
        This may modify the current state.
        To get a copy of a potential successor state, use generate_successor().
        """

        board = self.get_board()
        board._push(action)
