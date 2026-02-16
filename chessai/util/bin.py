import argparse
import logging
import typing

import chess

import chessai.core.agentaction
import chessai.core.agentinfo
import chessai.core.game
import chessai.core.log
import chessai.util.alias

SCORE_LIST_MAX_INFO_LENGTH: int = 50
""" If a score list is less than this, log it to info. """

@typing.runtime_checkable
class SetCLIArgs(typing.Protocol):
    """
    A function that can be used to modify a CLI parser before use.
    """

    def __call__(self,
            parser: argparse.ArgumentParser,
            ) -> argparse.ArgumentParser:
        """
        Modify the CLI parser before use.
        Any changes may be made, including adding arguments.
        The modified (or new) parser should be returned.
        """

@typing.runtime_checkable
class GetAdditionalOptions(typing.Protocol):
    """
    A function that can be used to get additional initialization options.
    """

    def __call__(self,
            args: argparse.Namespace,
            ) -> dict[str, typing.Any]:
        """
        Get additional/custom initialization options.
        """

@typing.runtime_checkable
class InitFromArgs(typing.Protocol):
    """
    A function that can be used to initialize components from CLI args.
    """

    def __call__(self,
            args: argparse.Namespace,
            ) -> tuple[dict[bool, chessai.core.agentinfo.AgentInfo], list[bool], dict[str, typing.Any]]:
        """
        Initialize components from arguments and return
        the base agent infos, a list of agents to remove from the board, as well as any board options.
        See base_init_from_args() for the default implementation.
        """

@typing.runtime_checkable
class LogResults(typing.Protocol):
    """
    A function that can be used to log game results.
    """

    def __call__(self,
            results: list[chessai.core.game.GameResult],
            winning_agent_indexes: set[bool],
            prefix: str = '',
            ) -> None:
        """
        Log the result of running several games.
        """

def base_init_from_args(args: argparse.Namespace) -> tuple[dict[bool, chessai.core.agentinfo.AgentInfo], list[bool], dict[str, typing.Any]]:
    """
    Take in args from a parser that was passed to set_cli_args(),
    and initialize the proper components.
    """

    # Create base arguments for all possible agents.
    base_agent_infos: dict[bool, chessai.core.agentinfo.AgentInfo] = {
        chess.WHITE: chessai.core.agentinfo.AgentInfo(name = chessai.util.alias.AGENT_RANDOM.long),
        chess.BLACK: chessai.core.agentinfo.AgentInfo(name = chessai.util.alias.AGENT_RANDOM.long),
    }

    return base_agent_infos, [], {}

def base_log_results(results: list[chessai.core.game.GameResult], winning_agent_teams: set[bool], prefix: str = '') -> None:
    """
    Log the result of running several games.
    """

    # TODO(Lucas): How should we log the outcomes in a reasonable scoring method?
    outcomes = [result.outcome for result in results]
    wins = [('Tie' if ((outcome is None) or (outcome.winner is None)) else ('Win' if (outcome.winner) else 'Loss')) for outcome in outcomes]
    turn_counts = [len(result.history) for result in results]

    num_white_wins = 0
    num_black_wins = 0
    num_ties = 0
    for outcome in outcomes:
        if ((outcome is None) or (outcome.winner is None)):
            num_ties += 1
        elif (outcome.winner == chess.WHITE):
            num_white_wins += 1
        else:
            num_black_wins += 1

    # Avoid logging long lists (which can be a bit slow in Python's logging module).
    log_lists_to_info = (len(results) < SCORE_LIST_MAX_INFO_LENGTH)
    log_lists_to_debug = (logging.getLogger().getEffectiveLevel() <= logging.DEBUG)

    # joined_scores = ''
    joined_record = ''
    joined_turn_counts = ''

    if (log_lists_to_info or log_lists_to_debug):
        # joined_scores = ', '.join([str(score) for score in scores])
        joined_record = ', '.join(wins)
        joined_turn_counts = ', '.join([str(turn_count) for turn_count in turn_counts])

    # logging.info('%sAverage Score: %s', prefix, sum(scores) / float(len(results)))

    # if (log_lists_to_info):
    #     logging.info('%sScores:        %s', prefix, joined_scores)
    # elif (log_lists_to_debug):
    #     logging.debug('%sScores:        %s', prefix, joined_scores)

    logging.info('%sWin Rate:      %d / %d (%0.2f)', prefix, wins.count('Win'), len(wins), (num_white_wins / len(wins)))

    if (log_lists_to_info):
        logging.info('%sRecord:        %s', prefix, joined_record)
    elif (log_lists_to_debug):
        logging.debug('%sRecord:        %s', prefix, joined_record)

    logging.info('%sAverage Turns: %s', prefix, sum(turn_counts) / float(len(results)))

    if (log_lists_to_info):
        logging.info('%sTurn Counts:   %s', prefix, joined_turn_counts)
    elif (log_lists_to_debug):
        logging.debug('%sTurn Counts:   %s', prefix, joined_turn_counts)

def run_main(
        description: str,
        game_class: typing.Type[chessai.core.game.Game],
        default_board: str | None = None,
        custom_set_cli_args: SetCLIArgs | None = None,
        custom_init_from_args: InitFromArgs = base_init_from_args,
        winning_agent_indexes: set[bool] | None = None,
        log_results: LogResults | None = typing.cast(LogResults, base_log_results),
        argv: list[str] | None = None,
        ) -> list[chessai.core.game.GameResult]:
    """
    A full main function to prep and run games.

    Returns the results of the games.
    """

    # Create a CLI parser.
    parser = get_parser(description, default_board, custom_set_cli_args = custom_set_cli_args)

    # Parse the CLI args.
    args = parse_args(parser, game_class,
            custom_init_from_args = custom_init_from_args,
            argv = argv)

    return run_games(args, winning_agent_indexes = winning_agent_indexes)

def get_parser(
        description: str,
        default_board: str | None = None,
        custom_set_cli_args: SetCLIArgs | None = None,
        ) -> argparse.ArgumentParser:
    """ Get a parser with all the options. """

    parser = argparse.ArgumentParser(description = description)

    # Add logging arguments.
    parser = chessai.core.log.set_cli_args(parser)

    # Add game arguments.
    parser = chessai.core.game.set_cli_args(parser, default_board = default_board)

    # Add custom options.
    if (custom_set_cli_args is not None):
        parser = custom_set_cli_args(parser)

    return parser

def parse_args(
        parser: argparse.ArgumentParser,
        game_class: typing.Type[chessai.core.game.Game],
        custom_init_from_args: InitFromArgs = base_init_from_args,
        argv: list[str] | None = None,
        ) -> argparse.Namespace:
    """ Parse the args from the parser returned by get_parser(). """

    args = parser.parse_args(args = argv)

    # Parse logging arguments.
    args = chessai.core.log.init_from_args(parser, args)

    # Parse custom options.
    base_agent_infos, _, _ = custom_init_from_args(args)

    # Parse game arguments.

    args = chessai.core.game.init_from_args(args, game_class,
            base_agent_infos = base_agent_infos)

    return args

# TODO(Lucas): Add back logging once implemented.
def run_games(
        args: argparse.Namespace,
        winning_agent_indexes: set[bool] | None = None,
        log_results: LogResults | None = typing.cast(LogResults, base_log_results),
        ) -> list[chessai.core.game.GameResult]:
    """
    Run one or more standard games using pre-parsed arguments.
    The arguments are expected to have `_games` and `_uis`,
    as if `chessai.core.ui.init_from_args()` and `chessai.core.game.init_from_args()` have been called.

    Returns the results of the games.
    """

    if (winning_agent_indexes is None):
        winning_agent_indexes = set()

    results = []

    for i in range(args.num_games):
        game = args._games[i]

        result = game.run()
        results.append(result)

    if (len(results) > 0):
        if (log_results is not None):
            log_results(results, winning_agent_indexes)

    return results
