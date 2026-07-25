import edq.testing.unittest

import chessai.chess.gamestate
import chessai.core.gameparser

# The standard starting position FEN, used across multiple tests.
STARTING_FEN: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

class ParseSinglePGNTest(edq.testing.unittest.BaseTest):
    """ Test the parsing of a single raw PGN into a ParsedPGN. """

    def test_parse_single_pgn(self):
        """ Test the parsing of a single raw PGN into a ParsedPGN. """

        # [(raw PGN, error substring, expected ParsedPGN), ...]
        test_cases: list[tuple[str, chessai.core.gameparser.ParsedPGN]] = [
            # Default headers and move SANs.
            (
                """
                [Event "Test"]
                [Site "Here"]
                [Date "2024.01.01"]
                [Round "1"]
                [White "A"]
                [Black "B"]
                [Result "1/2-1/2"]

                1. e4 e5 2. Nf3 Nc6 1/2-1/2
                """,
                chessai.core.gameparser.ParsedPGN(
                    headers = chessai.core.gameparser.StandardHeaders(
                        event = "Test",
                        site = "Here",
                        date = "2024.01.01",
                        game_round = "1",
                        white = "A",
                        black = "B",
                        result = "1/2-1/2",
                    ),
                    initial_actions = [
                        chessai.core.action.from_uci("e2e4"),
                        chessai.core.action.from_uci("e7e5"),
                        chessai.core.action.from_uci("g1f3"),
                        chessai.core.action.from_uci("b8c6"),
                        chessai.core.action.ProposeDrawAction(),
                        chessai.core.action.AcceptDrawAction(),
                    ],
                    result = chessai.core.gameparser.PGNResult('1/2-1/2'),
                )
            ),

            # Ignore RAVs.
            (
                """
                [Event "Test"]
                [Site "Here"]
                [Date "2024.01.01"]
                [Round "1"]
                [White "A"]
                [Black "B"]
                [Result "*"]

                1. e4 (1. d4 d5) e5 2. Nf3 Nc6 *
                """,
                chessai.core.gameparser.ParsedPGN(
                    headers = chessai.core.gameparser.StandardHeaders(
                        event = "Test",
                        site = "Here",
                        date = "2024.01.01",
                        game_round = "1",
                        white = "A",
                        black = "B",
                        result = "*",
                    ),
                    initial_actions = [
                        chessai.core.action.from_uci("e2e4"),
                        chessai.core.action.from_uci("e7e5"),
                        chessai.core.action.from_uci("g1f3"),
                        chessai.core.action.from_uci("b8c6"),
                    ],
                    result = chessai.core.gameparser.PGNResult('*'),
                )
            ),

            # Ignore nested RAVs.
            (
                """
                [Event "Test"]
                [Site "Here"]
                [Date "2024.01.01"]
                [Round "1"]
                [White "A"]
                [Black "B"]
                [Result "*"]

                1. e4 (1. d4 (1... d5) d5) e5 2. Nf3 Nc6 *
                """,
                chessai.core.gameparser.ParsedPGN(
                    headers = chessai.core.gameparser.StandardHeaders(
                        event = "Test",
                        site = "Here",
                        date = "2024.01.01",
                        game_round = "1",
                        white = "A",
                        black = "B",
                        result = "*",
                    ),
                    initial_actions = [
                        chessai.core.action.from_uci("e2e4"),
                        chessai.core.action.from_uci("e7e5"),
                        chessai.core.action.from_uci("g1f3"),
                        chessai.core.action.from_uci("b8c6"),
                    ],
                    result = chessai.core.gameparser.PGNResult('*'),
                )
            ),

            # Capture in-line comments.
            (
                """
                [Event "Test"]
                [Site "Here"]
                [Date "2024.01.01"]
                [Round "1"]
                [White "A"]
                [Black "B"]
                [Result "*"]

                1. e4 {Very interesting move!} e5 2. Nf3 Nc6 *
                """,
                chessai.core.gameparser.ParsedPGN(
                    headers = chessai.core.gameparser.StandardHeaders(
                        event = "Test",
                        site = "Here",
                        date = "2024.01.01",
                        game_round = "1",
                        white = "A",
                        black = "B",
                        result = "*",
                    ),
                    initial_actions = [
                        chessai.core.action.from_uci("e2e4"),
                        chessai.core.action.from_uci("e7e5"),
                        chessai.core.action.from_uci("g1f3"),
                        chessai.core.action.from_uci("b8c6"),
                    ],
                    comments = ["Very interesting move!"],
                    result = chessai.core.gameparser.PGNResult('*'),
                )
            ),

            # Capture multi-line comments.
            (
                """
                [Event "Test"]
                [Site "Here"]
                [Date "2024.01.01"]
                [Round "1"]
                [White "A"]
                [Black "B"]
                [Result "*"]

                1. e4 {This is a
                multi-line
                comment!} e5 2. Nf3 Nc6 *
                """,
                chessai.core.gameparser.ParsedPGN(
                    headers = chessai.core.gameparser.StandardHeaders(
                        event = "Test",
                        site = "Here",
                        date = "2024.01.01",
                        game_round = "1",
                        white = "A",
                        black = "B",
                        result = "*",
                    ),
                    initial_actions = [
                        chessai.core.action.from_uci("e2e4"),
                        chessai.core.action.from_uci("e7e5"),
                        chessai.core.action.from_uci("g1f3"),
                        chessai.core.action.from_uci("b8c6"),
                    ],
                    comments = [
                        """This is a\nmulti-line\ncomment!"""
                    ],
                    result = chessai.core.gameparser.PGNResult('*'),
                )
            ),

            # Custom starting position with FEN header.
            (
                """
                [Event "Test"]
                [Site "Here"]
                [Date "2024.01.01"]
                [Round "1"]
                [White "A"]
                [Black "B"]
                [Result "*"]
                [FEN "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"]

                1... Nc6 2. Nf3 Nf6 *
                """,
                chessai.core.gameparser.ParsedPGN(
                    headers = chessai.core.gameparser.StandardHeaders(
                        event = "Test",
                        site = "Here",
                        date = "2024.01.01",
                        game_round = "1",
                        white = "A",
                        black = "B",
                        result = "*",
                    ),
                    optional_headers = {"FEN": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"},
                    initial_actions = [
                        chessai.core.action.from_uci("b8c6"),
                        chessai.core.action.from_uci("g1f3"),
                        chessai.core.action.from_uci("g8f6"),
                    ],
                    result = "*",
                )
            ),

            # Draw accepted.
            (
                """
                    [Event "casual correspondence game"]
                    [Site "https://lichess.org/s7o9V5ny"]
                    [Date "2026.05.07"]
                    [Round "-"]
                    [White "ScrimScram"]
                    [Black "Anonymous"]
                    [Result "1/2-1/2"]
                    [GameId "s7o9V5ny"]
                    [UTCDate "2026.05.07"]
                    [UTCTime "21:09:09"]
                    [WhiteElo "1500"]
                    [BlackElo "?"]
                    [Variant "Standard"]
                    [TimeControl "-"]
                    [ECO "C00"]
                    [Opening "French Defense"]
                    [Termination "Normal"]
                    [Annotator "lichess.org"]

                1. e4 e6 { C00 French Defense } { The game is a draw. } 1/2-1/2
                """,
                chessai.core.gameparser.ParsedPGN(
                    headers = chessai.core.gameparser.StandardHeaders(
                        event = "casual correspondence game",
                        site = "https://lichess.org/s7o9V5ny",
                        date = "2026.05.07",
                        game_round = "-",
                        white = "ScrimScram",
                        black = "Anonymous",
                        result = "1/2-1/2",
                    ),
                    optional_headers = {
                        "GameId": "s7o9V5ny",
                        "UTCDate": "2026.05.07",
                        "UTCTime": "21:09:09",
                        "WhiteElo": "1500",
                        "BlackElo": "?",
                        "Variant": "Standard",
                        "TimeControl": "-",
                        "ECO": "C00",
                        "Opening": "French Defense",
                        "Termination": "Normal",
                        "Annotator": "lichess.org",
                    },
                    comments = ["C00 French Defense", "The game is a draw."],
                    initial_actions = [
                        chessai.core.action.from_uci("e2e4"),
                        chessai.core.action.from_uci("e7e6"),
                        chessai.core.action.ProposeDrawAction(),
                        chessai.core.action.AcceptDrawAction(),
                    ],
                    result = "1/2-1/2",
                )
            ),

            # Missing some headers.
            (
                """
                [Event "Test"]

                1. e4 e5
                """,
                chessai.core.gameparser.ParsedPGN(
                    headers = chessai.core.gameparser.StandardHeaders(
                        event = "Test",
                        result = "*",
                    ),
                    optional_headers = {},
                    initial_actions = [
                        chessai.core.action.from_uci("e2e4"),
                        chessai.core.action.from_uci("e7e5"),
                    ],
                    result = "Unknown",
                )
            ),
        ]

        for i, test_case in enumerate(test_cases):
            (raw_pgn, expected_pgn) = test_case

            with self.subTest(msg = f"Case {i}:"):
                try:
                    actual_pgn = chessai.core.gameparser.parse_pgn(raw_pgn, chessai.chess.gamestate.GameState)
                except Exception as ex:
                    self.fail(f"Unexpected error: '{str(ex)}'.")
                    continue

                self.assertEqual(expected_pgn, actual_pgn)
