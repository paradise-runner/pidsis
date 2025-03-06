# pidsis

A Python package for parsing pidstats log files into pandas DataFrames.

## Installation

```bash
pip install .
```

## Development Setup

```bash
# Install with test dependencies
pip install -e ".[test]"

# Run tests
pytest
```

## Usage

```bash
# Parse a pidstats file
pidsis /path/to/pidstats.log

# Parse and save to CSV files
pidsis /path/to/pidstats.log --output-dir ./output
```

## Project Structure

- `pidsis/` - Main package directory
  - `parser.py` - Core parsing logic
  - `dataframe.py` - DataFrame creation and manipulation
  - `utils.py` - Utility functions
  - `main.py` - Command-line interface
- `tests/` - Test directory
  - `data/` - Test data files
  - `test_parser.py` - Parser tests