#!/bin/bash

# Make the script executable with: chmod +x run.sh

# Check if there are arguments
if [ $# -eq 0 ]; then
    echo "Usage: ./run.sh COMMAND [ARGS]"
    echo "Examples:"
    echo "  ./run.sh --audio_file ./output/recording.wav"
    echo "  ./run.sh --help"
    exit 1
fi

# Run the docker container with the provided arguments
docker compose run --rm standup-summarizer python src/main.py "$@"