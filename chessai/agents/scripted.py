import typing

import chess

import chessai.core.agent
import chessai.core.gamestate

ACTION_DELIM: str = ','

class ScriptedAgent(chessai.core.agent.Agent):
    """
    An agent that has a specific set of actions that they will do in order.
    Once the actions are exhausted, they will just stop.
    This agent will take a scripted action even if it is illegal.

    This agent is particularly useful for things like replays.
    """

    def __init__(self,
            actions: list[chess.Move] | None = None,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        if (actions is None):
            actions = []

        self._actions: list[chess.Move] = actions
        """ The scripted actions this agent will take. """

    def get_action(self, state: chessai.core.gamestate.GameState) -> chess.Move:
        if (len(self._actions) > 0):
            return self._actions.pop(0)

        return chess.Move.null()
