import chessai.core.action
import chessai.core.agent
import chessai.core.gamestate

class RandomAgent(chessai.core.agent.Agent):
    """ An agent that just takes random (legal) action. """

    def get_action(self,
            state: chessai.core.gamestate.GameState) -> chessai.core.action.Action:
        """
        Returns a random legal action based on the game state while prioritizing movement actions.
        """

        # Prioritize movement actions.
        legal_actions = state.get_legal_move_actions()

        # Fall back to all legal actions if there are no legal movement actions.
        if (len(legal_actions) == 0):
            legal_actions = state.get_legal_actions()

        return self.rng.choice(legal_actions)
