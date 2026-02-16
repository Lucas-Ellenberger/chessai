import typing

import chessai.core.agentinfo

@typing.runtime_checkable
class TeamCreationFunction(typing.Protocol):
    """
    A function that can be used to create a capture team.
    """

    def __call__(self) -> list[chessai.core.agentinfo.AgentInfo]:
        """
        Get the agent infos used to construct a capture team.

        Standard capture usually uses two agents per team, but can technically support 10 total agents.
        If more agents than necessary are supplied, then the extra agents should be ignored.
        If fewer agent than necessary are supplied, then random agents should be used to fill out the rest of the team.
        """

def create_team_random() -> list[chessai.core.agentinfo.AgentInfo]:
    """
    Create a team with just random agents.
    """

    return [
        chessai.core.agentinfo.AgentInfo(name = chessai.util.alias.AGENT_RANDOM.long),
        chessai.core.agentinfo.AgentInfo(name = chessai.util.alias.AGENT_RANDOM.long),
        chessai.core.agentinfo.AgentInfo(name = chessai.util.alias.AGENT_RANDOM.long),
        chessai.core.agentinfo.AgentInfo(name = chessai.util.alias.AGENT_RANDOM.long),
        chessai.core.agentinfo.AgentInfo(name = chessai.util.alias.AGENT_RANDOM.long),
    ]
