# Chessai

An AI educational project disguised as [Chess](https://en.wikipedia.org/wiki/Chess)!

## Documentation

TODO: Release documentation.
API documentation for all releases is available at [lucas-ellenberger.github.io/chessai](https://lucas-ellenberger.github.io/chessai).

## Installation / Requirements

This project requires [Python](https://www.python.org/) >= 3.8.

Standard Python requirements are listed in `pyproject.toml`.
The project and Python dependencies can be installed from source with:
```sh
pip3 install .
```

## Using Chessai

Once installed, you can play a game of Chess with:
```sh
python3 -m chessai.chess
```

To see all the available options, use the `--help` flag:
```sh
python3 -m chessai.chess --help
```

### Boards

You can change the board that you are playing on with the `--board` option.
Any [chess FEN](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation) can be used to set the board.

TODO: Provide default boards / puzzles and update documentation.
Chessai comes with several different boards in the [chessai/resources/boards directory](chessai/resources/boards).
For example:
```sh
python3 -m chessai.chess --board "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"
```

You can also specify a path to a board file if you want to use a custom board:
```sh
python3 -m chessai.chess --board chessai/resources/boards/classic-small.board
```


### Choosing an Agent

In Chess, you can choose which agent you use with the `--white` and `--black` options.
The `--help` flag will list all the agent's available by default.
Agents may be specialized and not work on every board.

For example, you can use a random agent with:
```sh
python3 -m chessai.chess --white agent-random --black agent-random
```

You can also use `--white` and `--black` to point to any importable module or file/class.
```sh
# Use an importable module name.
python3 -m chessai.chess --white chessai.agents.random.RandomAgent

# Point to an agent class inside of a file.
python3 -m chessai.chess --black chessai/agents/random.py:RandomAgent
```

#### Agent Arguments

TODO: Expand agent argument example.

Many agents will accept arguments that can be used to tweak that agent's behavior.
These arguments can be passed using the `--agent-arg` options
(which can be specified as many times as you wish).
The argument to `--agent-arg` is formatted as: `<agent color>::<option name>=<option value>`.

Note that the agent now finds the optimal path much faster.

## For Students

Students who are working on this project as part of a class should note a few things:
 1. Never share your solutions or implemented code.
    In many courses, this would be considered cheating.
 2. Make sure that your version of this repo is private.
    Having a public repo may be indirectly sharing code.
    You can follow GitHub's directions on
    [creating a repo from a template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).
    Pay close attention to make the repository private.
 3. All or most of the code you will implement will be in the [chessai/student directory](chessai/student).

## Acknowledgements

This project has been built up from the work of many people.
Here are just a few that we know about:
 - TODO(List Acknowledgements)
 - TAs, grader, and graduates of UCSC's CMPS/CSE 240 class who have helped pave the way for future classes
   (their identities are immortalized in the git history).

## Licensing

See [LICENSE](LICENSE).

The majority of this project is licensed under an [MIT license](LICENSE-code).
Non-code portions of the code (e.g., images) under the [chessai/resources directory](/chessai/resources)
are license under a [CC BY-SA 4.0 license](LICENSE-noncode).

Additionally, solutions (implementations (full or partial) of the code in the [chessai/student directory](/chessai/student))
should never be published or distributed.

[This notice](LICENSE) should always be retained.
