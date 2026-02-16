# Text Sampler Server-Client

# This project implements a server-client pair for sampling lines from large text files.
# The server provides two methods:
# - load(): Appends lines from a text file to a global cache. Returns the number of lines read.
# - sample(): Returns N random lines from the cache, removing them so they cannot be sampled again.

## Features
# Key features include thread-safe server, concurrent clients, local communication, and robust edge case handling.
- Thread-safe server supporting concurrent clients
- Clients can load files and sample lines
- All communication is local (localhost)
- Edge cases handled: empty files, duplicates, oversampling, concurrency

## Directory Structure
# Project structure for clarity and organization.
- `src/`: Server and client code
- `tests/`: Unit and integration tests

## Usage
# Usage instructions for running the server and client.
1. Start the server
2. Use the client to load files and sample lines

## Setup
# Setup requirements and installation steps.
- Python 3.8+
- Install dependencies: `pip install -r requirements.txt`

## Testing
# Run tests to verify functionality and edge cases.
- Run `uvicorn src.server:app --reload`
- Run tests with `pytest`

## Example
# Example commands for loading and sampling lines.
- Load a file: `client.py load test_data/src/large.txt`
- Sample lines: `client.py sample 10`