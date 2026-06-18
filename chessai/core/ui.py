import abc
import argparse
import typing

import chessai.core.gamestate

class UI(abc.ABC):
    """
    UIs represent the basic way that a game interacts with the user,
    by displaying the state of the game.
    """

    def __init__(self,
            **kwargs: typing.Any) -> None:
        self._update_count: int = 0
        """ Keep track of the number of times update() has been called. """

    def update(self,
            state: chessai.core.gamestate.GameState,
            termination_reason: chessai.core.types.TerminationReason | None = None,
            ) -> None:
        """
        Update the UI with the current state of the game.
        This is the main entry point for the game into the UI.
        """

        self.draw(state, termination_reason = termination_reason)

        self._update_count += 1

    def game_start(self,
            initial_state: chessai.core.gamestate.GameState,
            ) -> None:
        """ Initialize the UI with the game's initial state. """

        self.update(initial_state)

    def game_complete(self,
            final_state: chessai.core.gamestate.GameState,
            termination_reason: chessai.core.types.TerminationReason,
            ) -> None:
        """ Update the UI with the game's final state. """

        self.update(final_state, termination_reason)

    def close(self) -> None:
        """ Close the UI and release all owned resources. """

    @abc.abstractmethod
    def draw(self, state: chessai.core.gamestate.GameState, **kwargs: typing.Any) -> None:
        """
        Visualize the state of the game to the UI.
        This is the typically the main override point for children.
        Note that how this method visualizes the game completely unrelated
        to how the draw_image() method works.
        draw() will render to whatever the specific UI for the child class is,
        while draw_image() specifically creates an image which will be used for animations.
        If the child UI is also image-based than it can leverage draw_image(),
        but there is no requirement to do that.
        """

def set_cli_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Set common CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    parser.add_argument('--ui', dest = 'ui',
            action = 'store', type = str, default = chessai.util.alias.UI_STDIO.short,
            help = ('Set the UI/graphics to use (default: %(default)s).'
                    + ' Builtin options:'
                    + f' `{chessai.util.alias.UI_NULL.short}` (`{chessai.util.alias.UI_NULL.long}`)'
                    +       ' -- Do not show any ui/graphics (best if you want to run fast and just need the result),'
                    + f' `{chessai.util.alias.UI_STDIO.short}` (`{chessai.util.alias.UI_STDIO.long}`)'
                    +       ' -- Use stdin/stdout from the terminal (default).'))

    return parser

def init_from_args(
        args: argparse.Namespace,
        num_uis: int = 0,
        null_out_uis: int = 0,
        additional_args: dict | None = None,
        ) -> argparse.Namespace:
    """
    Take in args from a parser that was passed to set_cli_args(),
    and initialize the proper components.
    Constructed UIs will be placed `args._uis`.
    If `num_uis` is not provided (or <= 0),
    then `args.num_games` will be used.
    If `null_out_uis` is > 0, then at most that number of UIs (starting at the beginning)
    will be converted to null UIs.
    This will not change the total number of UIs, just null out the first number of UIs.
    """

    ui_args = {
        # 'fps': args.fps,
        # 'animation_path': args.animation_path,
        # 'animation_fps': args.animation_fps,
        # 'animation_skip_frames': args.animation_skip_frames,
        # 'animation_optimize': args.animation_optimize,
    }

    if (additional_args is not None):
        ui_args.update(additional_args)

    if (num_uis <= 0):
        num_uis = args.num_games

    uis = []
    for i in range(num_uis):
        ui_name = args.ui
        if (i < null_out_uis):
            ui_name = chessai.util.alias.UI_NULL.long

        uis.append(chessai.util.reflection.new_object(ui_name, **ui_args))

    setattr(args, '_uis', uis)

    return args
