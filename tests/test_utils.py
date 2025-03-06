"""Tests for utility functions"""

import pytest
from pathlib import Path
from pidsis import utils

def test_read_file_lines(tmp_path):
    """Test reading lines from a valid file"""
    # Create a temporary test file
    test_file = tmp_path / "test.log"
    test_content = [
        "Linux 4.18.0-553.16.1.el8_10.x86_64 (host)\n",
        "\n",
        "09:55:46 PM   UID       PID    %usr %system\n",
        "09:56:46 PM     0       497    0.02    0.02\n"
    ]
    test_file.write_text("".join(test_content))

    # Read and verify lines
    lines = list(utils.read_file_lines(str(test_file)))
    assert len(lines) == 2  # Should skip empty line and Linux header
    assert lines[0] == "09:55:46 PM   UID       PID    %usr %system"
    assert lines[1] == "09:56:46 PM     0       497    0.02    0.02"

def test_read_nonexistent_file():
    """Test handling of non-existent file"""
    with pytest.raises(FileNotFoundError):
        list(utils.read_file_lines("nonexistent.log"))

def test_read_sample_pidstats():
    """Test reading the actual sample pidstats file"""
    sample_path = Path(__file__).parent / "data" / "sample.log"
    lines = list(utils.read_file_lines(str(sample_path)))
    assert len(lines) > 0
    assert any(line.startswith("09:") for line in lines)
    assert not any(line.startswith("Linux") for line in lines)

def test_is_linux_header():
    """Test identification of Linux system info header"""
    header = "Linux 4.18.0-553.16.1.el8_10.x86_64 (host) 03/02/2025 _x86_64_ (1 CPU)"
    assert utils.is_linux_header(header)
    assert not utils.is_linux_header("09:55:46 PM   UID       PID    %usr %system")
    assert not utils.is_linux_header("")

def test_should_skip_line():
    """Test identification of lines that should be skipped"""
    linux_header = "Linux 4.18.0-553.16.1.el8_10.x86_64 (host)"
    empty_line = ""
    whitespace_line = "   \t  \n"
    data_line = "09:55:46 PM   UID       PID    %usr %system"
    
    assert utils.should_skip_line(linux_header)
    assert utils.should_skip_line(empty_line)
    assert utils.should_skip_line(whitespace_line)
    assert not utils.should_skip_line(data_line)