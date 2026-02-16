import chess

import chessai.core.agent
import chessai.core.gamestate

class AggressiveAgent(chessai.core.agent.Agent):
    """ An agent that just takes random (legal) action. """

    def get_action(self,
            state: chessai.core.gamestate.GameState) -> chess.Move:
        """
        Returns a random legal move based on the game state.
        """

        board: chessai.core.board.Board = state.get_board()

        legal_moves = list(board.get_legal_moves())
        self.rng.shuffle(legal_moves)
        for move in legal_moves:
            if (board.is_capture(move)):
                return move

        # If we couldn't find a move that is a capture, return a random move.
        if (len(legal_moves) > 0):
            return legal_moves[0]
        else:
            return chess.Move.null()
