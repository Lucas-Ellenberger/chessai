import copy
import random
import typing

import edq.util.json

import chess

import chessai.core.agentaction
import chessai.core.board

class GameState(edq.util.json.DictConverter):
    """
    The base for all game states in chessai.
    A game state should contain all the information about the current state of the game.

    Game states should only be interacted with via their methods and not their member variables.
    """

    def __init__(self,
                 board: chessai.core.board.Board | None = None,
                 seed: int = -1,
                 game_over: bool = False,
                 **kwargs: typing.Any) -> None:
        if (board is None):
            raise ValueError("Cannot construct a game state without a board.")

        self.board: chessai.core.board.Board = board
        """ The current board. """

        self.seed: int = seed
        """ A utility seed that components using the game state may use to seed their own RNGs. """

        self.game_over: bool = game_over
        """ Indicates that this state represents a complete game. """

    def get_board(self) -> chessai.core.board.Board:
        """ Returns the chess board for the game state. """
        return self.board

    def get_player(self) -> bool:
        """ Returns the player with the next move. """
        return self.board.get_turn()

    def copy(self) -> 'GameState':
        """
        Get a deep copy of this state.

        Child classes are responsible for making any deep copies they need to.
        """

        new_state = copy.copy(self)

        new_state.board = self.board.copy()

        return new_state

    def game_start(self) -> None:
        """
        Indicate that the game is starting.
        This will initialize some state.
        """
        # TODO(Lucas): Necessary?

    def agents_game_start(self, agent_responses: dict[bool, chessai.core.agentaction.AgentActionRecord]) -> None:
        """ Indicate that agents have been started. """

    def game_complete(self) -> list[bool]:
        """
        Indicate that the game has ended.
        The state should take any final actions and return the indexes of the winning agents (if any).
        """

        return []

    def generate_successor(self,
            action: chess.Move,
            rng: random.Random | None = None,
            **kwargs: typing.Any) -> 'GameState':
        """
        Create a new deep copy of this state that represents the current agent taking the given action.
        To just apply an action to the current state, use process_turn().
        """

        successor = self.copy()
        successor.process_turn_full(action, rng, **kwargs)

        return successor


    def process_agent_timeout(self, agent_index: int) -> None:
        """
        Notify the state that the given agent has timed out.
        The state should make any updates and set the end of game information.
        """

        self.game_over = True

    def process_agent_crash(self, agent_index: int) -> None:
        """
        Notify the state that the given agent has crashed.
        The state should make any updates and set the end of game information.
        """

        self.game_over = True

    def process_game_timeout(self) -> None:
        """
        Notify the state that the game has reached the maximum number of turns without ending.
        The state should make any updates and set the end of game information.
        """

        self.game_over = True


    def process_turn(self,
            action: chess.Move,
            rng: random.Random | None = None,
            **kwargs: typing.Any) -> None:
        """
        Process the current agent's turn with the given action.
        This may modify the current state.
        To get a copy of a potential successor state, use generate_successor().
        """

    def process_turn_full(self,
            action: chess.Move,
            rng: random.Random | None = None,
            **kwargs: typing.Any) -> None:
        """
        Process the current agent's turn with the given action.
        This will modify the current state.
        First procecss_turn() will be called,
        then any bookkeeping will be performed.
        Child classes should prefer overriding the simpler process_turn().

        To get a copy of a potential successor state, use generate_successor().
        """

        # If the game is over, don't do anyhting.
        # This case can come up when planning agent actions and generating successors.
        if (self.game_over):
            return

        # TODO(Lucas): Do we need any additional bookkeeping outside of state.board?
        self.process_turn(action, rng, **kwargs)

    def to_dict(self) -> dict[str, typing.Any]:
        data = vars(self).copy()

        data['board'] = self.board.to_dict()

        return data

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        data = data.copy()
        data['board'] = chessai.core.board.Board.from_dict(data['board'])

        return cls(**data)

@typing.runtime_checkable
class AgentStateEvaluationFunction(typing.Protocol):
    """
    A function that can be used to score a game state.
    """

    def __call__(self,
            state: GameState,
            agent: typing.Any | None = None,
            **kwargs: typing.Any) -> int:
        """
        Compute a score for a state that the provided agent can use to decide actions.
        The current state is the only required argument, the others are optional.
        Passing the agent asking for this evaluation is a simple way to pass persistent state
        (like pre-computed heuristics) from the agent to this function.
        """

def base_eval(
        state: GameState,
        agent: typing.Any | None = None,
        **kwargs: typing.Any) -> int:
    """ The most basic evaluation function, which just uses the difference of the number of pieces. """

    board = state.get_board()

    piece_types: list[int] = [
        chess.PAWN,
        chess.KNIGHT,
        chess.BISHOP,
        chess.ROOK,
        chess.QUEEN,
        chess.KING,
    ]

    # The difference in pieces from white's perspective.
    piece_count = 0
    for piece_type in piece_types:
        piece_count += len(board.get_pieces(piece_type, chess.WHITE)) - len(board.get_pieces(piece_type, chess.BLACK))

    if (board.get_turn() == chess.WHITE):
        return piece_count

    # The piece difference is the opposite for black.
    return -1 * piece_count
