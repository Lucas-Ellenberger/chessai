import math

import chess

import chessai.core.agent
import chessai.core.gamestate

class ValueAgent(chessai.core.agent.Agent):
    """ An agent that takes an action that maximizes the value of the resulting board position. """

    def get_action(self,
            state: chessai.core.gamestate.GameState) -> chess.Move:
        """
        Returns the move the maximizes the expected value of the resulting board.
        """

        board: chessai.core.board.Board = state.get_board()

        # Start with a very bad value.
        best_score: float = -math.inf
        best_move: chess.Move | None = None

        legal_moves = list(board.get_legal_moves())
        self.rng.shuffle(legal_moves)
        for move in legal_moves:
            curr_state = state.generate_successor(move)
            opponents_score = self.evaluate_state(curr_state)

            # The move score is the inverse of the resulting score for the opponent.
            move_score = -1 * opponents_score

            # Check if we should accept the current move based on the expected value of the state.
            if (move_score > best_score):
                best_score = move_score
                best_move = move

        if (best_move is not None):
            return best_move

        # If we couldn't find a move, return a random move.
        if (len(legal_moves) > 0):
            return legal_moves[0]

        return chess.Move.null()
