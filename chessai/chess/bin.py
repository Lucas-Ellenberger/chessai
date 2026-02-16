"""
The main executable for running a game of Chess.
"""

import argparse
import logging
import typing

import chess

import chessai.chess.game
import chessai.chess.team
import chessai.util.alias
import chessai.util.bin

def set_cli_args(parser: argparse.ArgumentParser, **kwargs: typing.Any) -> argparse.ArgumentParser:
    """
    Set Chess-specific CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    parser.add_argument('--white-team', dest = 'white_team_func', metavar = 'TEAM_CREATION_FUNC',
            action = 'store', type = str, default = chessai.util.alias.AGENT_RANDOM.short,
            help = ('Select the chess team that will play on the white team (default: %(default)s).'
                    + f' Builtin teams: {chessai.util.alias.AGENT_SHORT_NAMES}.'))

    parser.add_argument('--black-team', dest = 'black_team_func', metavar = 'TEAM_CREATION_FUNC',
            action = 'store', type = str, default = chessai.util.alias.AGENT_RANDOM.short,
            help = ('Select the chess team that will play on the black team (default: %(default)s).'
                    + f' Builtin teams: {chessai.util.alias.AGENT_SHORT_NAMES}.'))

    return parser

def init_from_args(args: argparse.Namespace) -> tuple[dict[bool, chessai.core.agentinfo.AgentInfo], list[bool], dict[str, typing.Any]]:
    """
    Setup agents based on Chess rules.

    Agent infos are supplied via the --white-team and --black-team arguments.
    Missing agents will be filled in with random agents.
    """
    # TODO(Lucas): Fix base_agent_infos to actually get the agentinfo from the args.
    # The commented out code below gives dict[bool, Agent], not AgentInfos.
    # white_team = white_team_func
    # black_team = black_team_func

    base_agent_infos: dict[bool, chessai.core.agentinfo.AgentInfo] = {
        chess.WHITE: chessai.core.agentinfo.AgentInfo(name = args.white_team_func),
        chess.BLACK: chessai.core.agentinfo.AgentInfo(name = args.black_team_func),
    }

    # base_agent_infos: dict[bool, chessai.core.agentinfo.AgentInfo] = {
    #     chess.WHITE: white_team_func,
    #     chess.BLACK: black_team_func,
    # }

    # TODO(Lucas): Expand the board offerings.
    # Check for random boards.
    # args.board = chessai.chess.game.Game.check_for_random_board(args.board)

    return base_agent_infos, [], {}

def log_chess_results(results: list[chessai.core.game.GameResult], winning_agent_indexes: set[int], prefix: str = '') -> None:
    """
    Log the result of running several games.
    """

    outcomes = [result.outcome for result in results]
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

    logging.info('White Wins: %d, Black Wins: %d, Ties: %d', num_white_wins, num_black_wins, num_ties)

    # Avoid logging long lists (which can be a bit slow in Python's logging module).
    log_lists_to_info = (len(results) < chessai.util.bin.SCORE_LIST_MAX_INFO_LENGTH)
    log_lists_to_debug = (logging.getLogger().getEffectiveLevel() <= logging.DEBUG)

    # joined_results = ''
    # joined_record = ''
    joined_turn_counts = ''

    if (log_lists_to_info or log_lists_to_debug):
    #     joined_results = ', '.join([outcome.result() for outcome in outcomes])
    #     joined_record = ', '.join(record)
        joined_turn_counts = ', '.join([str(turn_count) for turn_count in turn_counts])

    # if (log_lists_to_info):
    #     logging.info('%sResults:        %s', prefix, joined_results)
    # elif (log_lists_to_debug):
    #     logging.debug('%sResults:        %s', prefix, joined_results)

    # if (log_lists_to_info):
    #     logging.info('%sRecord:        %s', prefix, joined_record)
    # elif (log_lists_to_debug):
    #     logging.debug('%sRecord:        %s', prefix, joined_record)

    logging.info('%sAverage Turns: %s', prefix, sum(turn_counts) / float(len(results)))

    if (log_lists_to_info):
        logging.info('%sTurn Counts:   %s', prefix, joined_turn_counts)
    elif (log_lists_to_debug):
        logging.debug('%sTurn Counts:   %s', prefix, joined_turn_counts)

def main(argv: list[str] | None = None,
        ) -> list[chessai.core.game.GameResult]:
    """
    Invoke a game of chess.

    Will return the results of the games.
    """

    return chessai.util.bin.run_main(
        description = "Play a game of chess.",
        game_class = chessai.chess.game.Game,
        default_board = None,
        custom_set_cli_args = set_cli_args,
        custom_init_from_args = init_from_args,
        argv = argv,
    )

if (__name__ == '__main__'):
    main()
