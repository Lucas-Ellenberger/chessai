import chessai.core.action
import chessai.core.agent
import chessai.core.gamestate

class UserInputAgent(chessai.core.agent.Agent):
    """ An agent that takes actions from the user. """

    def get_action(self,
            state: chessai.core.gamestate.GameState) -> chessai.core.action.Action:
        """
        Returns the chosen legal action from the user.
        """

        legal_actions = state.get_legal_actions()

        for (i, legal_action) in enumerate(legal_actions):
            print(f"{i}: '{legal_action}'")

        while (True):
            raw_index = input('Input the number corresponding to your chosen action: ')

            try:
                index = int(raw_index)
            except Exception:
                print(f"Please input a number, got: '{raw_index}'.")
                continue

            if ((index < 0) or (index >= len(legal_actions))):
                print(f"Input a number in the range [0, {len(legal_actions) - 1}], got: '{index}'.")
                continue

            return legal_actions[index]
