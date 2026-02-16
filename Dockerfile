# We use the official edulinq python grader for Ubuntu.
# https://github.com/edulinq/autograder-docker-python/blob/0.1.1.1/ubuntu/Dockerfile
FROM ghcr.io/edulinq/grader.python:0.1.1.1-ubuntu22.04

RUN apt install \
    curl \
    tar

WORKDIR /autograder/work

# Install Stockfish
RUN curl -o /autograder/work/stockfish.tar "https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64-avx2.tar"

RUN tar -xf stockfish.tar

# TODO: Use ./stockfish/ to generate moves in a game loop.
