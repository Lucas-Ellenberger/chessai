import argparse
import random
import typing

import chessai.chess.game
import chessai.core.agentinfo
import chessai.core.board
import chessai.core.game
import chessai.core.gamestate
import chessai.tour.gamestate
import chessai.tour.piece

class Game(chessai.chess.game.Game):
    """
    A tour game where the objective is to navigate a piece to the designated coordinates.
    """

    def __init__(self,
            game_info: chessai.core.game.GameInfo,
            save_path: str | None = None,
            is_replay: bool = False,
            search_targets: list[chessai.core.coordinate.Coordinate] | dict[str, typing.Any] | None = None,
            search_agent: chessai.core.types.Color = chessai.core.types.Color.WHITE) -> None:
        super().__init__(game_info, save_path, is_replay)

        if (search_targets is None):
            search_targets = []

        # Convert the string case into the dict case.
        if (isinstance(search_targets, str)):
            search_targets = {
                chessai.core.coordinate.COORDINATES_KEY: search_targets
            }

        if (isinstance(search_targets, dict)):
            search_targets = chessai.core.coordinate.coordinates_from_dict(search_targets)

        self.search_targets: list[chessai.core.coordinate.Coordinate] = search_targets
        """ The search targets of this game. """

        self.search_agent: chessai.core.types.Color = search_agent
        """ The agent completing the tour search, who is always the agent with the first move. """

    def process_args(self, args: argparse.Namespace) -> None:
        if (args.search_targets is not None):
            search_targets = {
                chessai.core.coordinate.COORDINATES_KEY: args.search_targets
            }

            self.search_targets = chessai.core.coordinate.coordinates_from_dict(search_targets)

    def get_initial_state(self,
            rng: random.Random,
            fen: str | None = None) -> chessai.core.gamestate.GameState:
        if (len(self.search_targets) == 0):
            # Let the gamestate parse the FEN so we can look for search targets from a file.
            initial_state = chessai.tour.gamestate.GameState.from_fen(fen = fen)
            self.search_targets = initial_state.search_targets
        else:
            initial_state = chessai.tour.gamestate.GameState.from_fen(fen = fen, search_targets = self.search_targets)

        # The search agent is always the agent with the first move.
        self.search_agent = initial_state.turn

        for search_target in self.search_targets:
            initial_state.board.set(chessai.tour.piece.Target(initial_state.turn.opposite()), search_target)

        return initial_state

    def process_turn(self,
            state: chessai.core.gamestate.GameState,
            action_record: chessai.core.agentaction.AgentActionRecord,
            result: chessai.core.game.GameResult,
            rng: random.Random,
            ) -> chessai.core.gamestate.GameState:
        """
        Process the given agent action and return an updated game state.
        The returned game state may be a copy or modified version of the passed in game state.
        """

        state = typing.cast(chessai.tour.gamestate.GameState, state)

        # The agent has timed out.
        if (action_record.timeout):
            result.timeout_agent_teams.append(action_record.player)
            state.process_agent_timeout(action_record.player)
            return state

        # The agent has crashed.
        if (action_record.crashed):
            result.crash_agent_teams.append(action_record.player)
            state.process_agent_crash(action_record.player)
            return state

        action = action_record.get_action()

        if (action not in state.get_legal_actions()):
            raise ValueError(f"Illegal action for agent {action_record.player}: '{action.uci()}' of type '{type(action)}'.")

        self._call_state_process_turn_full(state, action, rng, search_agent = self.search_agent)

        return state

    def check_end(self, state: chessai.core.gamestate.GameState) -> bool:
        """
        Check to see if the game is over.
        Return True if the game is now over, False otherwise.

        White wins by reaching all target squares.
        """

        state = typing.cast(chessai.tour.gamestate.GameState, state)

        if (state.game_over):
            return True

        return (len(state.search_targets) == 0)
