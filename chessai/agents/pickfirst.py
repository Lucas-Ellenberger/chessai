import chessai.core.action
import chessai.core.agent
import chessai.core.gamestate

class PickFirstAgent(chessai.core.agent.Agent):
    """ An agent that takes the first available action. """

    def get_action(self, state: chessai.core.gamestate.GameState) -> chessai.core.action.Action:
        legal_actions = state.get_legal_actions()

        return legal_actions[0]
