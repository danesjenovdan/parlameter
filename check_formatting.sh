#!/usr/bin/env bash

# exit immediately if a command exits with a non-zero status
set -e

# check if black is installed
if ! command -v black &> /dev/null
then
    echo "black could not be found, please install it to check formatting"
    exit 1
fi
# check if isort is installed
if ! command -v isort &> /dev/null
then
    echo "isort could not be found, please install it to check formatting"
    exit 1
fi

# change directory to the app directory
cd ./parladata

# run formatters if "--fix" argument is passed
if [[ "$1" == "--fix" ]]; then
    echo "Running formatters..."
    echo ""
    black .
    isort . --profile black
    exit
fi

# run black and isort in check mode otherwise
echo "Checking formatting... (run with --fix to format)"
echo ""
black . --check --diff
isort . --check --diff --profile black
