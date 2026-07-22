"""
This module handles containers for passing information from agents back to the game (via isolators).
"""

import typing

import edq.util.serial
import edq.util.time

import chessai.core.action

class AgentAction(edq.util.serial.DictConverter):
    """
    The full response by an agent when an action is requested.
    Agent's usually just provide actions, but more information can be supplied if necessary.
    """

    def __init__(self,
            action: chessai.core.action.Action | None = None,
            other_info: dict[str, typing.Any] | None = None,
            ) -> None:
        if (action is None):
            action = chessai.core.action.NoneAction()

        self.action: chessai.core.action.Action = action
        """ The action returned by the agent (or chessai.core.action.NoneAction() on a crash). """

        if (other_info is None):
            other_info = {}

        self.other_info: dict[str, typing.Any] = other_info
        """
        Additional information that the agent wishes to pass to the game.
        Specific games may use or ignore this information.

        All information put here must be trivially JSON serializable.
        """

class AgentActionRecord(edq.util.serial.DictConverter):
    """
    The full representation of requesting an action from an agent.
    In addition to the data supplied by the agent,
    this class contains administrative fields used to keep track of the agent.
    """

    def __init__(self,
            player: chessai.core.types.Color,
            agent_action: AgentAction | None,
            duration: edq.util.time.Duration,
            crashed: bool = False,
            timeout: bool = False,
            ) -> None:
        self.player: chessai.core.types.Color = player
        """ The player for the agent making this action. """

        self.agent_action: AgentAction | None = agent_action
        """ The information returned by the agent or None on a crash or timeout. """

        self.duration: edq.util.time.Duration = duration
        """ The duration (in MS) the agent took to compute this action. """

        self.crashed: bool = crashed
        """ Whether or not the agent crashed (e.g., raised an exception) when computing this action. """

        self.timeout: bool = timeout
        """ Whether or not the agent timed out when computing this action. """

    def get_action(self) -> chessai.core.action.Action:
        """ Get the agent's action. """

        if (self.agent_action is None):
            return chessai.core.action.NoneAction()

        return self.agent_action.action
