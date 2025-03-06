"""Tests for command-line interface"""

import pytest
import sys
from pathlib import Path
import pandas as pd
from pidsis import main
from io import StringIO

@pytest.fixture
def sample_log(tmp_path):
    """Create a sample pidstats log file for testing."""
    log_file = tmp_path / "test.log"
    content = '''Linux 4.18.0-553.16.1.el8_10.x86_64 (host) 03/02/2025 _x86_64_ (1 CPU)

09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
09:56:46 PM     0       497    0.02    0.02    0.00    0.02    0.03     0  systemd-journal
09:56:46 PM   993       670    0.17    0.02    0.00    0.00    0.18     0  prometheus

09:55:46 PM   UID       PID  minflt/s  majflt/s     VSZ     RSS   %MEM  Command
09:56:46 PM     0       497      0.17      0.00  129300    7036   0.89  systemd-journal
09:56:46 PM   993       670      0.05      0.00 2124408   67916   8.61  prometheus'''
    log_file.write_text(content)
    return log_file

def test_create_parser():
    """Test argument parser creation"""
    parser = main.create_parser()
    
    # Test required file_path argument
    with pytest.raises(SystemExit):
        parser.parse_args([])
    
    # Test with file path
    args = parser.parse_args(['test.log'])
    assert args.file_path == 'test.log'
    assert args.output_dir is None
    
    # Test with output directory
    args = parser.parse_args(['test.log', '--output-dir', 'output'])
    assert args.file_path == 'test.log'
    assert args.output_dir == 'output'

def test_process_file(sample_log, capsys):
    """Test processing of a pidstats file"""
    # Test basic processing without CSV output
    exit_code = main.process_file(str(sample_log))
    assert exit_code == 0
    
    captured = capsys.readouterr()
    assert "CPU DataFrame shape:" in captured.out
    assert "Memory DataFrame shape:" in captured.out
    assert "Unique processes: 2" in captured.out

def test_process_file_with_output(sample_log, tmp_path, capsys):
    """Test processing with CSV output"""
    output_dir = tmp_path / "output"
    
    # Test with CSV output
    exit_code = main.process_file(str(sample_log), str(output_dir))
    assert exit_code == 0
    
    # Verify files were created
    cpu_file = output_dir / "cpu_stats.csv"
    mem_file = output_dir / "mem_stats.csv"
    assert cpu_file.exists()
    assert mem_file.exists()
    
    # Verify CSV content
    cpu_df = pd.read_csv(cpu_file)
    mem_df = pd.read_csv(mem_file)
    assert len(cpu_df) == 2
    assert len(mem_df) == 2
    
    # Check output messages
    captured = capsys.readouterr()
    assert "CSV files saved to:" in captured.out
    assert str(cpu_file) in captured.out
    assert str(mem_file) in captured.out

def test_error_handling(tmp_path, capsys):
    """Test error handling scenarios"""
    # Test non-existent file
    exit_code = main.process_file("nonexistent.log")
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error: File not found" in captured.err
    
    # Test invalid output directory (permission error simulation)
    # Create a file with the same name as our intended directory
    invalid_dir = tmp_path / "invalid"
    invalid_dir.touch()
    exit_code = main.process_file(str(tmp_path), str(invalid_dir))
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err

def test_main_function(sample_log, monkeypatch):
    """Test main entry point function"""
    # Test successful execution
    with monkeypatch.context() as m:
        m.setattr(sys, 'argv', ['pidsis', str(sample_log)])
        assert main.main() == 0
    
    # Test with invalid arguments
    with monkeypatch.context() as m:
        m.setattr(sys, 'argv', ['pidsis'])
        with pytest.raises(SystemExit):
            main.main()