import random
import typing

import chessai.core.action
import chessai.core.board
import chessai.core.gamestate
import chessai.core.parser
import chessai.tour.parser

TIME_PENALTY: int = 1
""" Number of points lost each round. """

POSITION_POINTS: int = 10
""" Points for reaching a search position. """

BOARD_CLEAR_POINTS: int = 500
""" Points for reaching all search positions on the board. """

LOSE_POINTS: int = -500
""" Points for not finding a solution. """

CRASH_POINTS = -1000000
""" Points for crashing the game. """

class GameState(chessai.core.gamestate.GameState):
    """ A game state specific to a Tour game. """

    def __init__(self,
                 board: chessai.core.board.Board,
                 turn: chessai.core.types.Color,
                 castling_rights: chessai.core.castling.CastlingRights,
                 en_passant_coordinate: chessai.core.coordinate.Coordinate | None = None,
                 halfmove_clock: int = 0,
                 fullmove_number: int = 1,
                 previous_action: chessai.core.action.Action | None = None,
                 seed: int = -1,
                 game_over: bool = False,
                 search_targets: list[chessai.core.coordinate.Coordinate] | dict[str, typing.Any] | None = None,
                 _validate_search_targets: bool = True,
                 **kwargs: typing.Any) -> None:
        super().__init__(board, turn, castling_rights, en_passant_coordinate,
                         halfmove_clock, fullmove_number, previous_action,
                         seed, game_over, **kwargs)

        self.score: int = 0
        """ The score for the Tour. """

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
        """ The targets of the piece tour search. """

        # A Tour problem must have at least one search target.
        if (_validate_search_targets and (len(self.search_targets) == 0)):
            raise ValueError("Cannot create a Tour game state without at least one search target.")

    def is_game_over(self) -> bool:
        if (self.game_over):
            return True

        return (len(self.search_targets) == 0)

    def get_legal_actions(self) -> list[chessai.core.action.Action]:
        legal_actions = super().get_legal_actions()

        # Tour agents cannot propose a draw or forfeit the game.
        for action in [chessai.core.action.ProposeDrawAction(), chessai.core.action.ForfeitAction()]:
            if (action in legal_actions):
                legal_actions.remove(action)

        return legal_actions

    def remove_search_target(self, coordinate: chessai.core.coordinate.Coordinate) -> None:
        """
        Remove a search target from the gamestate.
        If the coordinate is not a search target, the state is unchanged.
        """

        if (coordinate not in self.search_targets):
            return

        self.search_targets.remove(coordinate)

    def process_turn(self,
            action: chessai.core.action.Action,
            rng: random.Random | None = None,
            **kwargs: typing.Any) -> None:
        """
        Process the current agent's turn with the given action.
        This may modify the current state.
        To get a copy of a potential successor state, use generate_successor().
        """

        # Simply progress the turn with the null action.
        if (self.turn == chessai.core.types.Color.BLACK):
            self._progress_state(action, False)
            return

        self.push(action)

        if isinstance(action, chessai.core.action.MoveAction):
            destination_coordinate = action.end_coordinate
            if (destination_coordinate in self.search_targets):
                # Get points for reaching a search target.
                self.remove_search_target(destination_coordinate)
                self.score += POSITION_POINTS

        # The agent always loses a point each turn.
        self.score -= TIME_PENALTY

    def process_agent_timeout(self, player: chessai.core.types.Color) -> None:
        # Treat timeouts like crashes.
        self.process_agent_crash(player)

    def process_agent_crash(self, player: chessai.core.types.Color) -> None:
        super().process_agent_crash(player)

        if (player == chessai.core.types.Color.WHITE):
            self.score += CRASH_POINTS

    def game_complete(self) -> tuple[list[chessai.core.types.Color], float]:
        # The agent wins if they reach all of the search targets.
        if (len(self.search_targets) == 0):
            self.score += BOARD_CLEAR_POINTS

            return ([chessai.core.types.Color.WHITE], self.score)

        self.score += LOSE_POINTS

        return ([chessai.core.types.Color.BLACK], self.score)

    def copy(self) -> 'GameState':
        new_state = GameState(board           = self.board.copy(),
                              turn            = self.turn,
                              castling_rights = self.castling_rights,
                              en_passant_coordinate = self.en_passant_coordinate,
                              halfmove_clock  = self.halfmove_clock,
                              fullmove_number = self.fullmove_number,
                              previous_action = self.previous_action,
                              seed            = self.seed,
                              game_over       = self.game_over,
                              search_targets  = self.search_targets.copy(),
                              _validate_search_targets = False)

        new_state.score = self.score

        return new_state

    @classmethod
    def get_gamestate_parser(cls) -> chessai.core.parser.GameStateParser:
        return chessai.tour.parser.parse_tour
