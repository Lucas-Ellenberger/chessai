import os

import edq.testing.unittest
import edq.util.dirent

import chessai.puzzle.bin
import chessai.puzzle.parser

class GameTest(edq.testing.unittest.BaseTest):
    """ Test specifics for puzzle games. """

    def test_puzzles(self):
        """ Test every puzzle board in the resources directory. """

        expected_score = 1.0

        board_paths = []
        boards_dir = os.listdir(chessai.puzzle.parser.PUZZLES_DIR)
        for dirent in boards_dir:
            path = os.path.join(chessai.puzzle.parser.PUZZLES_DIR, dirent)
            if (not os.path.isfile(path)):
                continue

            if (os.path.splitext(path)[-1] != chessai.puzzle.parser.PUZZLE_FILE_EXTENSION):
                continue

            board_paths.append(str(path))

        board_paths.sort()

        # Ensure we find at least one puzzle.
        self.assertNotEqual(len(board_paths), 0)

        for (i, board_path) in enumerate(board_paths):
            with self.subTest(msg = f"Case {i}, path: {board_path}"):
                gamestate = chessai.puzzle.gamestate.GameState.from_fen(fen = board_path, _capture_move_lines = True)

                # Puzzle boards must include the move lines, which will be parsed by the gamestate.
                move_lines = gamestate._move_lines
                move_lines = [[action.uci() for action in line] for line in move_lines]
                agent_arg = f"{gamestate.turn.symbol()}::move_lines={move_lines}"

                argv = [
                    '--log-level', 'CRITICAL',
                    '--board', str(board_path),
                    '--agent', 'agent-multi-scripted',
                    '--agent-arg', agent_arg,
                    '--max-moves', '80',
                ]
                results = chessai.puzzle.bin.main(argv = argv)

                self.assertEqual(expected_score, results[0].score)
