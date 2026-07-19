import typing

import chessai.core.action
import chessai.core.gamestate
import chessai.core.search
import chessai.core.coordinate
import chessai.core.types
import chessai.search.common
import chessai.tour.gamestate
import chessai.util.alias

class PositionSearchNode(chessai.core.search.SearchNode):
    """
    A search node for the position search problem.
    The state for this problem is simple,
    it is just the current position being searched.
    """

    def __init__(self, position: chessai.core.coordinate.Coordinate, state: chessai.core.gamestate.GameState) -> None:
        self.position: chessai.core.coordinate.Coordinate = position
        """ The current position being searched. """

        self.state: chessai.core.gamestate.GameState = state
        """ The gamestate of the search node. """

    def __lt__(self, other: object) -> bool:
        if (not isinstance(other, PositionSearchNode)):
            return False

        return (self.position < other.position)

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, PositionSearchNode)):
            return False

        return (self.position == other.position)

    def __hash__(self) -> int:
        return hash(self.position)

class PositionSearchProblem(chessai.core.search.SearchProblem[PositionSearchNode]):
    """
    A search problem for finding a specific position on the board.
    """

    def __init__(self,
            game_state: chessai.core.gamestate.GameState,
            goal_positions: list[chessai.core.coordinate.Coordinate] | None = None,
            start_position: chessai.core.coordinate.Coordinate | None = None,
            cost_function: chessai.core.search.CostFunction | str = chessai.util.alias.COST_FUNC_UNIT.long,
            **kwargs: typing.Any) -> None:
        """
        Create a positional search problem.

        If no goal position is provided, the board's search target will be used,
            if that does not exist, then DEFAULT_GOAL_POSITION will be used.
        If no start position is provided, the current agent's position will be used.
        If no cost function is provided, chessai.util.alias.COST_FUNC_UNIT will be used.
        """

        super().__init__()

        self.state: chessai.tour.gamestate.GameState = typing.cast(chessai.tour.gamestate.GameState, game_state)
        """ Keep track of the gamestate so we can navigate. """

        if (goal_positions is None):
            if (len(self.state.search_targets) == 0):
                raise ValueError("Cannot create a position search problem without at least one goal position.")

            goal_positions = self.state.search_targets

        self.goal_positions: list[chessai.core.coordinate.Coordinate] = goal_positions
        """ The positions to search for. """

        if (start_position is None):
            all_coordinates = self.state.get_coordinate_map(self.state.search_agent)
            for (coordinate, piece) in all_coordinates.items():
                if isinstance(piece, chessai.tour.piece.Rock):
                    continue

                start_position = coordinate
                break

        if (start_position is None):
            raise ValueError("Could not find starting position.")

        self.start_position: chessai.core.coordinate.Coordinate = start_position
        """ The position to start from. """

        self.start_state: chessai.core.gamestate.GameState = self.state.copy()
        """ The board the problem started from. """

        if (isinstance(cost_function, str)):
            cost_function = typing.cast(chessai.core.search.CostFunction, chessai.util.reflection.fetch(cost_function))

        self._cost_function: chessai.core.search.CostFunction = cost_function
        """ The function used to score search nodes. """

    def get_starting_node(self) -> PositionSearchNode:
        return PositionSearchNode(self.start_position, self.start_state)

    def is_goal_node(self, node: PositionSearchNode) -> bool:
        return (node.position in self.goal_positions)

    def complete(self, goal_node: PositionSearchNode) -> None:
        # Mark the final node in the history.
        self.position_history.append(goal_node.position)

    def get_successor_nodes(self, node: PositionSearchNode) -> list[chessai.core.search.SuccessorInfo]:
        successors = []

        # Check all the neighbors.
        for (action, position) in node.state.get_neighbors(node.position):
            next_state = node.state.copy()
            next_state.push(action)

            # Push a null move for black.
            next_state._progress_state(chessai.core.action.NoneAction(), False)

            next_node = PositionSearchNode(position, next_state)
            cost = self._cost_function(next_node)

            successors.append(chessai.core.search.SuccessorInfo(next_node, action, cost))

        # Do bookkeeping on the states/positions we visited.
        self.expanded_node_count += 1
        if (node not in self.visited_nodes):
            self.position_history.append(node.position)

        return successors
