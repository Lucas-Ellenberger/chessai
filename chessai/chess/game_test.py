import os

import edq.testing.unittest
import edq.util.dirent

import chessai.chess.bin
import chessai.chess.game
import chessai.core.game
import chessai.core.agentinfo
import chessai.core.gamestate
import chessai.core.types
import chessai.util.alias

AGENT_INFOS: dict[chessai.core.types.Color, chessai.core.agentinfo.AgentInfo] = {
    chessai.core.types.Color.WHITE: chessai.core.agentinfo.AgentInfo(name = chessai.util.alias.AGENT_RANDOM.long),
    chessai.core.types.Color.BLACK: chessai.core.agentinfo.AgentInfo(name = chessai.util.alias.AGENT_RANDOM.long),
}
DEFAULT_SEED: int = 1

class GameTest(edq.testing.unittest.BaseTest):
    """ Test the game's interactions with PGNs. """

    def test_from_pgn(self):
        """ Test Game.from_pgn() with various PGN inputs. """

        # [(pgn_string, expected_game), ...]
        test_cases: list[tuple[str, chessai.chess.game.Game]] = [
            # Basic game with default starting position.
            (
                """
                [Event "Test Tournament"]
                [Site "Test City"]
                [Date "2024.01.01"]
                [Round "1"]
                [White "Alice"]
                [Black "Bob"]
                [Result "*"]

                1. e4 e5 2. Nf3 Nc6 3. Bb5 *
                """,
                chessai.chess.game.Game(
                    game_info = chessai.core.game.GameInfo(
                        agent_infos = AGENT_INFOS,
                        start_fen = chessai.core.gamestate.DEFAULT_FEN,
                        event = "Test Tournament",
                        site = "Test City",
                        date = "2024.01.01",
                        game_round = "1",
                        white_player = "Alice",
                        black_player = "Bob",
                    ),
                    initial_actions = [
                        chessai.core.action.from_uci("e2e4"),
                        chessai.core.action.from_uci("e7e5"),
                        chessai.core.action.from_uci("g1f3"),
                        chessai.core.action.from_uci("b8c6"),
                        chessai.core.action.from_uci("f1b5"),
                    ],
                    expected_result = chessai.core.gameparser.PGNResult("*"),
                    is_replay = True,
                ),
            ),

            # Game with custom starting position (FEN header).
            (
                """
                [Event "Puzzle"]
                [Site "Online"]
                [Date "2024.01.15"]
                [Round "-"]
                [White "White"]
                [Black "Black"]
                [Result "*"]
                [FEN "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"]

                3. Bb5 a6 *
                """,
                chessai.chess.game.Game(
                    game_info = chessai.core.game.GameInfo(
                        agent_infos = AGENT_INFOS,
                        start_fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
                        event = "Puzzle",
                        site = "Online",
                        date = "2024.01.15",
                        game_round = "-",
                        white_player = "White",
                        black_player = "Black",
                    ),
                    initial_actions = [
                        chessai.core.action.from_uci("f1b5"),
                        chessai.core.action.from_uci("a7a6"),
                    ],
                    expected_result = chessai.core.gameparser.PGNResult("*"),
                    is_replay = True,
                ),
            ),

            # Draw result.
            (
                """
                [Event "Draw Game"]
                [Site "Test"]
                [Date "2024.02.01"]
                [Round "5"]
                [White "Player1"]
                [Black "Player2"]
                [Result "1/2-1/2"]

                1. e4 e5 2. Nf3 Nc6 1/2-1/2
                """,
                chessai.chess.game.Game(
                    game_info = chessai.core.game.GameInfo(
                        agent_infos = AGENT_INFOS,
                        start_fen = chessai.core.gamestate.DEFAULT_FEN,
                        event = "Draw Game",
                        site = "Test",
                        date = "2024.02.01",
                        game_round = "5",
                        white_player = "Player1",
                        black_player = "Player2",
                    ),
                    initial_actions = [
                        chessai.core.action.from_uci("e2e4"),
                        chessai.core.action.from_uci("e7e5"),
                        chessai.core.action.from_uci("g1f3"),
                        chessai.core.action.from_uci("b8c6"),
                        chessai.core.action.ProposeDrawAction(),
                        chessai.core.action.AcceptDrawAction(),
                    ],
                    expected_result = chessai.core.gameparser.PGNResult("1/2-1/2"),
                    is_replay = True,
                ),
            ),

            # Proposed draw.
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
                chessai.chess.game.Game(
                    game_info = chessai.core.game.GameInfo(
                        agent_infos = AGENT_INFOS,
                        start_fen = chessai.core.gamestate.DEFAULT_FEN,
                        event = "casual correspondence game",
                        site = "https://lichess.org/s7o9V5ny",
                        date = "2026.05.07",
                        game_round = "-",
                        white_player = "ScrimScram",
                        black_player = "Anonymous",
                    ),
                    initial_actions = [
                        chessai.core.action.from_uci("e2e4"),
                        chessai.core.action.from_uci("e7e6"),
                        chessai.core.action.ProposeDrawAction(),
                        chessai.core.action.AcceptDrawAction(),
                    ],
                    expected_result = chessai.core.gameparser.PGNResult("1/2-1/2"),
                    is_replay = True,
                ),
            ),
        ]

        for i, test_case in enumerate(test_cases):
            (pgn_string, expected_game) = test_case

            with self.subTest(msg = f"Case {i}:"):
                # Create Game from ParsedPGN.
                game = chessai.chess.game.Game.from_pgn(
                    pgn = pgn_string,
                    state_class = chessai.chess.gamestate.GameState,
                    game_info = expected_game.game_info,
                )

                self.assertIsNotNone(game)

                # Set the seed to the default seed to compare game info's directly.
                expected_game.game_info.seed = DEFAULT_SEED

                # Verify the game is as expected.
                self.assertEqual(game.game_info, expected_game.game_info)
                self.assertEqual(game._save_path, expected_game._save_path)
                self.assertEqual(game._is_replay, expected_game._is_replay)
                self.assertEqual(game.initial_actions, expected_game.initial_actions)
                self.assertEqual(game.expected_result, expected_game.expected_result)

    def test_load_replay(self):
        """
        Test a game can played from a PGN and the written result is the same.
        Note that some information is excluded, as our PGN reader / writer does not support them.
        """

        temp_dir = edq.util.dirent.get_temp_dir(prefix = 'chessai-test-')
        replay_path = os.path.join(temp_dir, 'test.replay')

        expected_score = 0

        # Run a short capture game and save the replay.
        argv = [
            '--seed', '2',
            '--ui', 'null',
            '--save-path', replay_path,
            '--white-team', 'agent-random',
            '--black-team', 'agent-random',
            '--max-moves', '50',
            '--log-level', 'CRITICAL',
        ]
        results = chessai.chess.bin.main(argv = argv)

        self.assertEqual(expected_score, results[0].score)

        # Replay the game and get the same result.
        argv = [
            '--replay-path', replay_path,
            '--ui', 'null',
            '--log-level', 'CRITICAL',
        ]
        results = chessai.chess.bin.main(argv = argv)

        self.assertEqual(expected_score, results[0].score)

    def test_pgn_games(self):
        """ Test every PGN in the resources directory runs. """

        game_paths = []
        games_dir = os.listdir(chessai.core.gameparser.GAMES_DIR)
        for dirent in games_dir:
            path = os.path.join(chessai.core.gameparser.GAMES_DIR, dirent)
            if (not os.path.isfile(path)):
                continue

            if (os.path.splitext(path)[-1] == '.py'):
                continue

            game_paths.append(str(path))

        game_paths.sort()

        # Ensure we find at least one game.
        self.assertNotEqual(len(game_paths), 0)

        for (i, game_path) in enumerate(game_paths):
            with self.subTest(msg = f"Case {i}, path: {game_path}"):
                argv = [
                    '--ui', 'null',
                    '--log-level', 'CRITICAL',
                    '--replay-path', str(game_path),
                    '--max-moves', '200',
                ]
                results = chessai.chess.bin.main(argv = argv)

                # Since we don't know the result, check the game concluded.
                self.assertIn(results[0].score, [0, 0.5, 1])
