"""
This file provides useful aliases/shortcuts or short names for different objects in chessai.
# TODO(Lucas): Change example.
For example, the `web` alias can be used to reference `chessai.ui.web.WebUI`.
"""

class Alias:
    """ An alias for some object name. """

    _alias_map: dict[str, str] = {}
    """ Keep track of all aliases for testing purposes. """

    _all_aliases: list['Alias'] = []
    """ Keep track of all aliases mappings for lookup. """

    def __init__(self,
            short: str, long: str,
            is_qualified_name: bool = True, skip_windows_test: bool = False,
            ) -> None:
        self.short: str = short
        """ The short name for this alias. """

        self.long: str = long
        """ The long name for this alias. """

        self.is_qualified_name: bool = is_qualified_name
        """
        Whether this alias represents a qualified name.
        Alias that are qualified names will be tested with reflection.
        """

        self.skip_windows_test: bool = skip_windows_test
        """ If this alias' reflection test should be skipped on Windows. """

        if ('.' in short):
            raise ValueError(f"Dots ('.') are not allowed in aliases. Found '{short}'.")

        if (short in Alias._alias_map):
            raise ValueError(f"Found duplicate alias: '{short}' -> '{long}'.")

        Alias._alias_map[short] = long
        Alias._all_aliases.append(self)

    def __repr__(self) -> str:
        return f"('{self.short}' -> '{self.long}')"

def lookup(short: str, default: str | None = None) -> str:
    """
    Lookup the long name for an alias.
    Return the alias long name if the alias is found,
    and the default value if the alias is not found.
    If the alias is not found and no default is specified,
    then raise an error.
    """

    if (short in Alias._alias_map):
        return Alias._alias_map[short]

    if (default is not None):
        return default

    raise ValueError(f"Could not find alias: '{short}'.")

# TODO(Lucas): Implement all of the alias agents.
# AGENT_CHEATING: Alias = Alias('agent-cheating', 'chessai.agents.cheating.CheatingAgent')
AGENT_AGGRESSIVE: Alias = Alias('agent-aggressive', 'chessai.agents.aggressive.AggressiveAgent')
AGENT_DUMMY: Alias = Alias('agent-dummy', 'chessai.agents.dummy.DummyAgent')
# AGENT_MINIMAX: Alias = Alias('agent-minimax', 'chessai.student.multiagents.MyMinimaxLikeAgent')
AGENT_RANDOM: Alias = Alias('agent-random', 'chessai.agents.random.RandomAgent')
AGENT_SCRIPTED: Alias = Alias('agent-scripted', 'chessai.agents.scripted.ScriptedAgent')
# AGENT_TIMEOUT: Alias = Alias('agent-timeout', 'chessai.agents.testing.TimeoutAgent')

AGENT_SHORT_NAMES: list[str] = [
    AGENT_AGGRESSIVE.short,
    # AGENT_CHEATING.short,
    AGENT_DUMMY.short,
    # AGENT_MINIMAX.short,
    AGENT_RANDOM.short,
    AGENT_SCRIPTED.short,
    # AGENT_TIMEOUT.short,
]

# TODO(Lucas): Implement all of the alias evals.
STATE_EVAL_BASE: Alias = Alias('state-eval-base', 'chessai.core.gamestate.base_eval')
# STATE_EVAL_MINIMAX_BETTER: Alias = Alias('state-eval-minimax-better', 'chessai.student.multiagents.better_state_eval')

STATE_EVAL_SHORT_NAMES: list[str] = [
    STATE_EVAL_BASE.short,
    # STATE_EVAL_MINIMAX_BETTER.short,
]
