import chess

import chessai.core.agent
import chessai.core.gamestate

class RandomAgent(chessai.core.agent.Agent):
    """ An agent that just takes random (legal) action. """

    def get_action(self,
            state: chessai.core.gamestate.GameState) -> chess.Move:
        """
        Returns a random legal move based on the game state.
        """

        board = state.get_board()
        if (board is None):
            raise ValueError("Trying to get an action from an agent without a board.")

        legal_moves = list(board.get_legal_moves())
        return self.rng.choice(legal_moves)
