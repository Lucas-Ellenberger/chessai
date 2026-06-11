import edq.testing.unittest

import chessai.core.gamestate
import chessai.core.coordinate
import chessai.core.action
import chessai.core.types
import chessai.tour.gamestate

class GameStateTest(edq.testing.unittest.BaseTest):
    """ Test chessai.chess.gamestate.GameState functionality. """

    def test_legal_actions(self):
        """ Test the legal action generator. """

        # [(FEN, expected_actions, is_checkmate, is_stalemate), ...]
        test_cases: list[tuple[str | None, list[str], bool, bool]] = [
            (
                None,
                [
                    'a2a3', 'a2a4', 'b2b3', 'b2b4',
                    'c2c3', 'c2c4', 'd2d3', 'd2d4',
                    'e2e3', 'e2e4', 'f2f3', 'f2f4',
                    'g2g3', 'g2g4', 'h2h3', 'h2h4',
                    'b1a3', 'b1c3', 'g1f3', 'g1h3',
                ],
                False,
                False,
            ),
            (
                edq.util.json.dumps(chessai.tour.parser.TourInfo(
                    fen = 'n7/8/8/8/8/8/8/8 w - - 0 1',
                    search_targets = ['a6'],
                )),
                ['a1b3', 'a1c2'],
                False,
                False,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            with self.subTest(msg = f"Case {i}:"):
                (start_fen, uci_actions, checkmate, stalemate) = test_case

                expected_actions: list[chessai.core.action.Action] = []
                for uci_action in uci_actions:
                    expected_actions.append(chessai.core.action.from_uci(uci_action))

                state = chessai.tour.gamestate.GameState.from_fen(fen = start_fen)

                self.assertEqual(state.is_checkmate(), checkmate)
                self.assertEqual(state.is_stalemate(), stalemate)

                actual_actions = state.get_legal_actions()

                self.assertEqual(len(actual_actions), len(expected_actions))

                for expected_action in expected_actions:
                    self.assertIn(expected_action, actual_actions)
