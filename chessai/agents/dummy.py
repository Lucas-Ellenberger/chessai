import chess

import chessai.core.agent
import chessai.core.gamestate

class DummyAgent(chessai.core.agent.Agent):
    """
    An agent that only takes the NULL action.
    At first this may seem useless, but dummy agents can serve several purposes.
    Like being a stand-in for a future agent, fallback for a failing agent, or a placeholder when running a replay.
    """

    def get_action(self, state: chessai.core.gamestate.GameState) -> chess.Move:
        return chess.Move.null()
