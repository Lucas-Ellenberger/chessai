import edq.testing.unittest

import chessai.chess.gamestate
import chessai.core.action
import chessai.core.coordinate
import chessai.core.gamestate
import chessai.core.types

class GameStateTest(edq.testing.unittest.BaseTest):
    """ Test chessai.chess.gamestate.GameState functionality. """

    def test_default_state(self):
        """ Test default gamestate for some basic properties. """

        state = chessai.chess.gamestate.GameState.from_fen()

        # Basic State
        self.assertEqual(state.get_fen(), chessai.core.gamestate.DEFAULT_FEN)
        self.assertEqual(state.turn, chessai.core.types.Color.WHITE)

        # Core Functions
        self.assertFalse(state.is_game_over())
        self.assertIsNone(state.previous_action)

        # Legal actions
        legal_actions = state.get_legal_actions()
        self.assertNotEqual(len(legal_actions), 0)

        # Make sure each action is well-formed.
        for legal_action in legal_actions:
            if (not isinstance(legal_action, chessai.core.action.MoveAction)):
                continue

            self.assertNotEqual(legal_action.start_coordinate, legal_action.end_coordinate) # pylint: disable=no-member

        # Push an action and observe the resulting state.
        chosen_action = legal_actions[0]
        state.push(chosen_action)

        # Check it updated the basic state.
        self.assertEqual(state.turn, chessai.core.types.Color.BLACK)
        self.assertNotEqual(state.get_fen(), chessai.core.gamestate.DEFAULT_FEN)

        # Check state history.
        self.assertEqual(state.previous_action, chosen_action)

    def test_generate_successor_does_not_modify_original(self):
        """ Test generate successor properly deep copies the state. """

        state = chessai.chess.gamestate.GameState.from_fen()
        actions = state.get_legal_actions()

        action = actions[0]

        successor = state.generate_successor(action)

        # Original should remain unchanged
        self.assertIsNone(state.previous_action)
        self.assertEqual(successor.previous_action, action)
        self.assertNotEqual(state.turn, successor.turn)

    def test_get_neighbors_filters_by_start_coordinate(self):
        """ Test get neighbors returns actions only from the start coordinate. """

        state = chessai.chess.gamestate.GameState.from_fen()
        actions = state.get_legal_actions()

        action = actions[0]
        start = action.start_coordinate

        neighbors = state.get_neighbors(start)

        for (action, _) in neighbors:
            self.assertEqual(action.start_coordinate, start)

    def test_push_illegal_action_raises(self):
        """ Test illegal actions raise errors. """

        state = chessai.chess.gamestate.GameState.from_fen()

        fake_action = chessai.core.action.MoveAction(chessai.core.coordinate.NULL_COORDINATE, chessai.core.coordinate.NULL_COORDINATE)

        with self.assertRaises(ValueError):
            state.push(fake_action)

    def test_legal_actions(self):
        """ Test the legal action generator. """

        # [(FEN, expected_actions, is_checkmate, is_stalemate), ...]
        test_cases: list[tuple[str | None, list[str], bool, bool]] = [
            (
                None,
                [
                    'a2a3', 'a2a4', 'b2b3', 'b2b4', 'c2c3', 'c2c4',
                    'd2d3', 'd2d4', 'e2e3', 'e2e4', 'f2f3', 'f2f4',
                    'g2g3', 'g2g4', 'h2h3', 'h2h4', 'b1a3', 'b1c3',
                    'g1f3', 'g1h3', 'Propose Draw', 'Forfeit',
                ],
                False,
                False,
            ),
            (
                "1rr5/p1p2Rpp/2Qpk3/4n1q1/4P3/8/PPP3PP/R6K w - - 0 1",
                [
                    'a2a3', 'a2a4', 'b2b3', 'b2b4', 'c2c3', 'c2c4',
                    'g2g3', 'g2g4', 'h2h3', 'h2h4', 'a1b1', 'a1c1',
                    'a1d1', 'a1e1', 'a1f1', 'a1g1', 'f7c7', 'f7f1',
                    'f7f2', 'f7f3', 'f7f4', 'f7f5', 'f7f6', 'f7f8',
                    'f7d7', 'f7e7', 'f7g7', 'h1g1', 'c6a4', 'c6a6',
                    'c6a8', 'c6b5', 'c6b6', 'c6b7', 'c6c3', 'c6c4',
                    'c6c5', 'c6c7', 'c6d5', 'c6d6', 'c6d7', 'c6e8',
                    'Propose Draw', 'Forfeit',
                ],
                False,
                False,
            ),
            (
                'rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3',
                ['Propose Draw', 'Forfeit'],
                True,
                False,
            ),
            (
                'r1bqkbnr/pppp1Qpp/8/4P3/2Bn4/8/PPPP1PPP/RNB1KBNR b KQkq - 0 5',
                ['Propose Draw', 'Forfeit'],
                True,
                False,
            ),
            (
                '7k/6R1/8/5N2/7R/8/8/K7 b - - 0 1',
                ['Propose Draw', 'Forfeit'],
                True,
                False,
            ),
            (
                'rnb1kbnr/pppp1pPp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3',
                ['Propose Draw', 'Forfeit'],
                True,
                False,
            ),
            (
                '4R1k1/p4ppp/8/8/8/5B2/PP1r1PPP/R5K1 b - - 0 1',
                ['Propose Draw', 'Forfeit'],
                True,
                False,
            ),
            (
                '7k/p4p2/P4P2/1P6/6R1/3B4/6PP/R5K1 b - - 0 1',
                ['Propose Draw', 'Forfeit'],
                False,
                True,
            ),
            (
                'r3k2r/8/8/7B/8/2n4n/8/R3K2R w KQkq - 0 1',
                [
                    'a1a2', 'a1a3', 'a1a4', 'a1a5',
                    'a1a6', 'a1a7', 'a1a8', 'a1b1',
                    'a1c1', 'a1d1', 'e1d2', 'e1f1',
                    'h1f1', 'h1g1', 'h1h2', 'h1h3',
                    'h5d1', 'h5e2', 'h5e8', 'h5f3',
                    'h5f7', 'h5g4', 'h5g6',
                    'Propose Draw', 'Forfeit',
                ],
                False,
                False,
            ),
            (
                'r3k2r/8/8/7B/8/2n4n/8/R3K2R b KQkq - 0 1',
                [
                    'e8d7', 'e8d8', 'e8e7', 'e8f8',
                    'h8h5', 'Propose Draw', 'Forfeit',
                ],
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

                state = chessai.chess.gamestate.GameState.from_fen(fen = start_fen)

                self.assertEqual(state.is_checkmate(), checkmate)
                self.assertEqual(state.is_stalemate(), stalemate)

                actual_actions = state.get_legal_actions()

                self.assertEqual(len(actual_actions), len(expected_actions))

                for expected_action in expected_actions:
                    self.assertIn(expected_action, actual_actions)

    def test_final_action(self):
        """ Test mate in 1 or stalemate in 1. """

        # [(FEN, action, is_checkmate, is_stalemate, is_insufficient_material), ...]
        test_cases: list[tuple[str, chessai.core.action.Action, bool, bool, bool]] = [
            # En-passant capture into checkmate.
            (
                '2R5/p6k/P7/1P3Pp1/3B4/6R1/3B2PP/6K1 w - g6 0 1',
                chessai.core.action.from_uci('f5g6'),
                True,
                False,
                False,
            ),

            # action into checkmate.
            (
                '6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1',
                chessai.core.action.from_uci('e1e8'),
                True,
                False,
                False,
            ),

            # Castling into checkmate (kingside)
            (
                '1nbqrkr1/p1ppp1pp/8/8/1b6/8/PPPPP1PP/RNBQK2R w KQ - 0 1',
                chessai.core.action.from_uci('e1g1'),
                True,
                False,
                False,
            ),

            # Castling into checkmate (queenside)
            (
                '1brkr1nn/ppp1p1pp/8/8/5B2/2N1Q3/P1P1P1PP/R3K2R w KQ - 0 1',
                chessai.core.action.from_uci('e1c1'),
                True,
                False,
                False,
            ),

            # Double pawn push leading to checkmate
            (
                'rnb2Nnr/ppppQppp/8/4pk2/8/5PP1/PPPPP2P/RNB1KB1R w KQ - 1 3',
                chessai.core.action.from_uci('e2e4'),
                True,
                False,
                False,
            ),

            # Double pawn push for discovered checkmate
            (
                '3q3r/1bp2ppp/k1n5/4p3/3B4/1N6/PPPPPPPP/R2QKB1R w KQ - 0 8',
                chessai.core.action.from_uci('e2e4'),
                True,
                False,
                False,
            ),

            # Knight action checkmate
            (
                '5rkr/5ppp/8/3N4/8/8/5PRP/7K w - - 0 1',
                chessai.core.action.from_uci('d5f6'),
                True,
                False,
                False,
            ),

            # Bishop action checkmate
            (
                '6kr/3N2pp/8/8/8/8/5PPP/5BRK w - - 0 1',
                chessai.core.action.from_uci('f1c4'),
                True,
                False,
                False,
            ),

            # Queen action checkmate (Scholar's Mate)
            (
                'r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4',
                chessai.core.action.from_uci('h5f7'),
                True,
                False,
                False,
            ),

            # Pawn promotion to queen for checkmate
            (
                '6k1/2P2p1p/7P/7K/8/8/8/8 w - - 0 1',
                chessai.core.action.from_uci('c7c8Q'),
                True,
                False,
                False,
            ),

            # Action into stalemate
            (
                '8/p6k/P7/1P6/3B4/5R2/3B2PP/6K1 w - - 0 1',
                chessai.core.action.from_uci('f3g3'),
                False,
                True,
                False,
            ),

            # Capture leading to stalemate
            (
                '7k/5K2/4Q1p1/8/8/8/8/8 w - - 0 1',
                chessai.core.action.from_uci('e6g6'),
                False,
                True,
                False,
            ),

            # Promotion to queen causing stalemate
            (
                '8/6P1/7k/8/6K1/8/8/8 w - - 0 1',
                chessai.core.action.from_uci('g7g8Q'),
                False,
                True,
                False,
            ),

            # Checkmate by moving bishop
            (
                '2r2k2/8/8/b2b4/5n2/8/8/3K4 b - - 0 1',
                chessai.core.action.from_uci('d5b3'),
                True,
                False,
                False,
            ),

            # Underpromotion to knight for checkmate
            (
                '5bnr/Q3Pnkq/5ppp/8/8/4PP2/PPPP1KP1/RNBR4 w - - 0 1',
                chessai.core.action.from_uci('e7e8N'),
                True,
                False,
                False,
            ),

            # Capture and promote to queen for checkmate
            (
                '6k1/5ppp/8/8/8/8/2p2PPP/1N4K1 b - - 0 1',
                chessai.core.action.from_uci('c2b1q'),
                True,
                False,
                False,
            ),

            # King action into stalemate (capturing into stalemate)
            (
                '4K2k/3R4/8/8/8/8/8/8 w - - 0 1',
                chessai.core.action.from_uci('e8f8'),
                False,
                True,
                False,
            ),

            # Smothered mate with knight
            (
                '6rk/4N1pn/8/8/8/8/8/5K1R w - - 0 1',
                chessai.core.action.from_uci('e7g6'),
                True,
                False,
                False,
            ),

            # Pawn push causing stalemate
            (
                'k7/8/1KP5/8/8/8/8/8 w - - 0 1',
                chessai.core.action.from_uci('c6c7'),
                False,
                True,
                False,
            ),

            # Two rooks checkmate (ladder mate)
            (
                '6k1/8/6K1/8/8/8/7R/7R w - - 0 1',
                chessai.core.action.from_uci('h2h8'),
                True,
                False,
                False,
            ),

            # Queen action checkmate
            (
                '7k/5Q2/6K1/8/8/8/8/8 w - - 0 1',
                chessai.core.action.from_uci('f7f8'),
                True,
                False,
                False,
            ),

            # King only insufficient material
            (
                '4k3/3Q4/8/8/8/8/8/4K3 b - - 0 1',
                chessai.core.action.from_uci('e8d7'),
                False,
                False,
                True,
            ),

            # Insufficient material, king and bishop
            (
                '8/8/6p1/8/4B3/8/k7/2K5 w - - 0 1',
                chessai.core.action.from_uci('e4g6'),
                False,
                False,
                True,
            ),

            # Insufficient material, king and knight
            (
                '8/8/5p2/8/4N3/8/k7/2K5 w - - 0 1',
                chessai.core.action.from_uci('e4f6'),
                False,
                False,
                True,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            with self.subTest(msg = f"Case {i}:"):
                (start_fen, action, checkmate, stalemate, material) = test_case

                state = chessai.chess.gamestate.GameState.from_fen(fen = start_fen)

                # Check that it is not a checkmate or stalemate before the action.
                self.assertFalse(state.is_checkmate())
                self.assertFalse(state.is_stalemate())
                self.assertFalse(state.is_insufficient_material())

                state.process_turn(action)

                # Check that it is a checkmate or stalemate after the action.
                self.assertEqual(state.is_checkmate(), checkmate)
                self.assertEqual(state.is_stalemate(), stalemate)
                self.assertEqual(state.is_insufficient_material(), material)
