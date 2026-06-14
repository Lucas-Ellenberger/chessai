import edq.testing.unittest

import chessai.core.action
import chessai.core.coordinate
import chessai.core.gamestate
import chessai.core.types
import chessai.tour.gamestate

class GameStateTest(edq.testing.unittest.BaseTest):
    """ Test chessai.chess.gamestate.GameState functionality. """

    def test_legal_actions(self):
        """ Test the legal action generator. """

        # [(tour_filepath, expected_actions, is_checkmate, is_stalemate), ...]
        test_cases: list[tuple[str, list[str], bool, bool]] = [
            (
                'tour-base',
                ['a1b3', 'a1c2'],
                False,
                False,
            ),
            (
                'tour-multi',
                [
                    'd4b3', 'd4b5', 'd4c2', 'd4c6',
                    'd4e2', 'd4e6', 'd4f3', 'd4f5',
                ],
                False,
                False,
            ),
            (
                'tour-rocks',
                ['a1c2'],
                False,
                False,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            with self.subTest(msg = f"Case {i}:"):
                (tour_filepath, uci_actions, checkmate, stalemate) = test_case

                expected_actions: list[chessai.core.action.Action] = []
                for uci_action in uci_actions:
                    expected_actions.append(chessai.core.action.from_uci(uci_action))

                state = chessai.tour.gamestate.GameState.from_fen(fen = tour_filepath)

                self.assertEqual(state.is_checkmate(), checkmate)
                self.assertEqual(state.is_stalemate(), stalemate)

                actual_actions = state.get_legal_actions()

                self.assertEqual(len(actual_actions), len(expected_actions))

                for expected_action in expected_actions:
                    self.assertIn(expected_action, actual_actions)
