"""Utility functions for pidstats parsing"""

from typing import Iterator
from pathlib import Path

def read_file_lines(file_path: str) -> Iterator[str]:
    """Read lines from a file, skipping lines that should be ignored.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        Iterator of lines from the file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read
    """
    try:
        with Path(file_path).open() as f:
            for line in f:
                line = line.strip()
                if not should_skip_line(line):
                    yield line
    except (FileNotFoundError, PermissionError) as e:
        # Re-raise these specific exceptions for proper error handling
        raise
    except Exception as e:
        # Convert unexpected errors to a more specific exception
        raise IOError(f"Error reading file {file_path}: {str(e)}") from e

def is_linux_header(line: str) -> bool:
    """Check if a line is the Linux system info header.
    
    Args:
        line: Line to check
        
    Returns:
        True if the line is a Linux system info header
    """
    return line.strip().startswith('Linux')

def should_skip_line(line: str) -> bool:
    """Check if a line should be skipped during processing.
    
    Args:
        line: Line to check
        
    Returns:
        True if the line should be skipped (empty, whitespace, or Linux header)
    """
    line = line.strip()
    return not line or is_linux_header(line)