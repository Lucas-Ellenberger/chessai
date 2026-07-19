import random
import typing

import chessai.core.search

def tour_base_search(
        problem: chessai.core.search.SearchProblem,
        heuristic: chessai.core.search.SearchHeuristic,
        rng: random.Random,
        **kwargs: typing.Any) -> chessai.core.search.SearchSolution:
    """
    Output a very specific set of actions meant for the `tour-base` board.
    This (fake) search will generally not work on other boards.
    """

    actions = [
        chessai.core.action.from_uci('a1b3'),
        chessai.core.action.from_uci('b3c5'),
        chessai.core.action.from_uci('c5e6'),
        chessai.core.action.from_uci('e6f4'),
        chessai.core.action.from_uci('f4g6'),
        chessai.core.action.from_uci('g6h8'),
    ]

    return chessai.core.search.SearchSolution(actions, 0.0)
