import typing

import chessai.core.action
import chessai.core.agent
import chessai.core.gamestate

class MultiScriptedAgent(chessai.core.agent.Agent):
    """
    An agent that tries to follow one of the predetermined action sets, or "move lines".
    Once the actions are exhausted, they will just stop.
    If there are multiple actions available, one of the scripts will be chosen at random.
    This agent will take a scripted action even if it is illegal.
    """

    def __init__(self,
                 move_lines: list[list[chessai.core.action.Action]] | str | dict[str, typing.Any] | None = None,
                 **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        if (isinstance(move_lines, (str, dict))):
            move_lines = chessai.core.action.process_raw_action_list(move_lines)

        if (move_lines is None):
            move_lines = []

        self._move_lines: list[list[chessai.core.action.Action]] = move_lines
        """ The move lines this agent will follow, depending on the actions of the other player. """

    def get_action(self, state: chessai.core.gamestate.GameState) -> chessai.core.action.Action:
        # Update the move lines based on the previous action taken.
        previous_action = state.get_previous_action()
        if (previous_action is not None):
            self._update_move_lines(previous_action)

        # Choose an action out of the available move lines.
        possible_moves = self._next_move_options()
        if (len(possible_moves) == 0):
            return chessai.core.action.NoneAction()

        chosen_move_list = self.rng.sample(possible_moves, 1)
        chosen_move = chosen_move_list[0]

        # Update the possible move lines based on our current action.
        self._update_move_lines(chosen_move)

        return chosen_move

    def _next_move_options(self) -> list[chessai.core.action.Action]:
        """ Get the list of possible next moves from the multiple scripts. """

        move_options = []

        for move_line in self._move_lines:
            if (len(move_line) > 0):
                move_options.append(move_line[0])

        return move_options

    def _update_move_lines(self, action: chessai.core.action.Action) -> None:
        """ Update the possible move lines based on the action taken. """

        if (isinstance(action, chessai.core.action.NoneAction)):
            return

        new_move_lines = []

        for move_line in self._move_lines:
            if (len(move_line) == 0):
                continue

            # Skip if the action is not consistent with the move line.
            if (move_line[0] != action):
                continue

            new_move_line = move_line[1:]

            # If there is nothing left in the move line, skip it.
            if (len(new_move_line) == 0):
                continue

            new_move_lines.append(new_move_line)

        self._move_lines = new_move_lines
