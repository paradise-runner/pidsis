"""Integration tests for pidsis package"""

import pytest
from pathlib import Path
import pandas as pd
from pidsis import parser, dataframe

def test_complete_parsing_pipeline():
    """Test the complete parsing pipeline from file to DataFrames"""
    sample_path = Path(__file__).parent / "data" / "sample.log"
    
    # Parse the file into raw data
    cpu_data, memory_data = parser.parse_pidstats_file(str(sample_path))
    
    # Verify CPU data
    assert len(cpu_data) == 3  # We expect 3 CPU entries
    assert all(isinstance(entry, dict) for entry in cpu_data)
    assert all('timestamp' in entry for entry in cpu_data)
    assert all('pid' in entry for entry in cpu_data)
    
    # Check specific CPU values
    prometheus_entry = next(entry for entry in cpu_data if entry['command'] == 'prometheus')
    assert prometheus_entry['uid'] == 993
    assert prometheus_entry['cpu'] == 0.18
    
    # Verify memory data
    assert len(memory_data) == 3  # We expect 3 memory entries
    assert all(isinstance(entry, dict) for entry in memory_data)
    assert all('timestamp' in entry for entry in memory_data)
    assert all('pid' in entry for entry in memory_data)
    
    # Check specific memory values
    prometheus_mem = next(entry for entry in memory_data if entry['command'] == 'prometheus')
    assert prometheus_mem['vsz'] == 2124408
    assert prometheus_mem['rss'] == 67916
    assert prometheus_mem['mem_percent'] == 8.61

def test_dataframe_creation():
    """Test creation of pandas DataFrames from parsed data"""
    sample_path = Path(__file__).parent / "data" / "sample.log"
    cpu_data, memory_data = parser.parse_pidstats_file(str(sample_path))
    
    # Create DataFrames
    cpu_df, memory_df = dataframe.create_dataframes(cpu_data, memory_data)
    
    # Verify CPU DataFrame
    assert isinstance(cpu_df, pd.DataFrame)
    assert len(cpu_df) == 3
    assert all(col in cpu_df.columns for col in ['usr', 'system', 'cpu', 'command'])
    
    # Check specific CPU DataFrame values
    prometheus_cpu = cpu_df[cpu_df['command'] == 'prometheus'].iloc[0]
    assert prometheus_cpu['usr'] == 0.17
    assert prometheus_cpu['system'] == 0.02
    assert prometheus_cpu['cpu'] == 0.18
    
    # Verify Memory DataFrame
    assert isinstance(memory_df, pd.DataFrame)
    assert len(memory_df) == 3
    assert all(col in memory_df.columns for col in ['vsz', 'rss', 'mem_percent', 'command'])
    
    # Check specific Memory DataFrame values
    prometheus_mem = memory_df[memory_df['command'] == 'prometheus'].iloc[0]
    assert prometheus_mem['vsz'] == 2124408
    assert prometheus_mem['rss'] == 67916
    assert prometheus_mem['mem_percent'] == 8.61

def test_multi_timestamp_aggregation():
    """Test handling of multiple timestamps in the data"""
    # Create test data with multiple timestamps
    cpu_data = [
        {'timestamp': '09:55:46 PM', 'pid': 123, 'command': 'test1', 'cpu': 0.5},
        {'timestamp': '09:56:46 PM', 'pid': 123, 'command': 'test1', 'cpu': 1.0},
        {'timestamp': '09:55:46 PM', 'pid': 456, 'command': 'test2', 'cpu': 0.3},
        {'timestamp': '09:56:46 PM', 'pid': 456, 'command': 'test2', 'cpu': 0.6}
    ]
    
    memory_data = [
        {'timestamp': '09:55:46 PM', 'pid': 123, 'command': 'test1', 'rss': 1000},
        {'timestamp': '09:56:46 PM', 'pid': 123, 'command': 'test1', 'rss': 1200},
        {'timestamp': '09:55:46 PM', 'pid': 456, 'command': 'test2', 'rss': 500},
        {'timestamp': '09:56:46 PM', 'pid': 456, 'command': 'test2', 'rss': 600}
    ]
    
    cpu_df, memory_df = dataframe.create_dataframes(cpu_data, memory_data)
    
    # Verify time series aspects
    assert len(cpu_df.index.unique(level='timestamp')) == 2
    assert len(memory_df.index.unique(level='timestamp')) == 2
    
    # Check that we can get process-specific time series
    test1_cpu = cpu_df[cpu_df['command'] == 'test1']
    assert len(test1_cpu) == 2
    assert test1_cpu['cpu'].tolist() == [0.5, 1.0]

def test_large_file_processing():
    """Test processing of a larger file with multiple sections"""
    # Create a larger test file with multiple alternating sections
    test_data = []
    cpu_section = '''09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
09:56:46 PM     0       497    0.02    0.02    0.00    0.02    0.03     0  systemd-journal
09:56:46 PM   993       670    0.17    0.02    0.00    0.00    0.18     0  prometheus
09:56:46 PM   992       676    0.07    0.03    0.00    0.00    0.10     0  node_exporter'''

    mem_section = '''09:55:46 PM   UID       PID  minflt/s  majflt/s     VSZ     RSS   %MEM  Command
09:56:46 PM     0       497      0.17      0.00  129300    7036   0.89  systemd-journal
09:56:46 PM   993       670      0.05      0.00 2124408   67916   8.61  prometheus
09:56:46 PM   992       676      0.00      0.02 1241952   16172   2.05  node_exporter'''
    
    # Add multiple alternating sections
    for _ in range(5):
        test_data.append(cpu_section)
        test_data.append(mem_section)
    
    test_file = Path(__file__).parent / "data" / "large_test.log"
    test_file.write_text('\n'.join(test_data))
    
    # Parse and verify
    cpu_data, memory_data = parser.parse_pidstats_file(str(test_file))
    assert len(cpu_data) == 15  # 5 sections × 3 entries
    assert len(memory_data) == 15  # 5 sections × 3 entries
    
    # Create DataFrames from large dataset
    cpu_df, memory_df = dataframe.create_dataframes(cpu_data, memory_data)
    assert len(cpu_df) == 15
    assert len(memory_df) == 15

def test_error_handling():
    """Test error handling in the parsing pipeline"""
    non_existent_path = Path(__file__).parent / "data" / "non_existent.log"
    
    # Test file not found
    with pytest.raises(FileNotFoundError):
        parser.parse_pidstats_file(str(non_existent_path))
    
    # Test malformed data handling
    malformed_data = [
        {'timestamp': '09:55:46 PM'}  # Missing required fields
    ]
    
    with pytest.raises(KeyError):
        dataframe.create_cpu_dataframe(malformed_data)

def test_section_integrity():
    """Test integrity of section parsing and transitions"""
    # Create test data with multiple sections and gaps
    test_data = '''Linux 4.18.0-553.16.1.el8_10.x86_64 (host) 03/02/2025 _x86_64_ (1 CPU)

09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
09:56:46 PM   993       670    0.17    0.02    0.00    0.00    0.18     0  prometheus

Some random text that should be ignored

09:55:46 PM   UID       PID  minflt/s  majflt/s     VSZ     RSS   %MEM  Command
09:56:46 PM   993       670      0.05      0.00 2124408   67916   8.61  prometheus

Another random line
Invalid data line

09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
09:56:46 PM   993       670    0.17    0.02    0.00    0.00    0.18     0  prometheus'''

    test_file = Path(__file__).parent / "data" / "section_test.log"
    test_file.write_text(test_data)
    
    # Parse and verify section integrity
    cpu_data, memory_data = parser.parse_pidstats_file(str(test_file))
    assert len(cpu_data) == 2  # Two CPU sections with one entry each
    assert len(memory_data) == 1  # One memory section with one entry
    
    # Verify timestamps are preserved correctly
    cpu_timestamps = {entry['timestamp'] for entry in cpu_data}
    mem_timestamps = {entry['timestamp'] for entry in memory_data}
    assert len(cpu_timestamps) == 1  # Same timestamp across sections
    assert len(mem_timestamps) == 1

def test_real_world_data():
    """Test parsing and DataFrame creation with real world pidstats data"""
    # Use the real pidstats log file
    real_data_path = Path(__file__).parent.parent / "pidsis" / "data" / "pidstats_2025-03-02_15-18-09.log"
    
    # Parse the file into raw data
    cpu_data, memory_data = parser.parse_pidstats_file(str(real_data_path))
    
    # Verify we got some data
    assert len(cpu_data) > 0, "Should have CPU data entries"
    assert len(memory_data) > 0, "Should have memory data entries"
    
    # Create DataFrames
    cpu_df, memory_df = dataframe.create_dataframes(cpu_data, memory_data)
    
    # Verify DataFrames were created properly
    assert isinstance(cpu_df, pd.DataFrame)
    assert isinstance(memory_df, pd.DataFrame)
    assert len(cpu_df) == len(cpu_data)
    assert len(memory_df) == len(memory_data)
    
    # Verify DataFrame structures
    assert all(col in cpu_df.columns for col in ['usr', 'system', 'cpu', 'command'])
    assert all(col in memory_df.columns for col in ['vsz', 'rss', 'mem_percent', 'command'])
    
    # Verify multi-index structure
    assert cpu_df.index.names == ['timestamp', 'pid']
    assert memory_df.index.names == ['timestamp', 'pid']
    
    # Check data types
    assert cpu_df['usr'].dtype == float
    assert cpu_df['system'].dtype == float
    assert cpu_df['cpu'].dtype == float
    assert memory_df['vsz'].dtype == int
    assert memory_df['rss'].dtype == int
    assert memory_df['mem_percent'].dtype == float
    
    # Verify value ranges
    assert (cpu_df['usr'] >= 0).all() and (cpu_df['usr'] <= 100).all()
    assert (cpu_df['system'] >= 0).all() and (cpu_df['system'] <= 100).all()
    assert (cpu_df['cpu'] >= 0).all() and (cpu_df['cpu'] <= 100).all()
    assert (memory_df['vsz'] >= 0).all()
    assert (memory_df['rss'] >= 0).all()
    assert (memory_df['mem_percent'] >= 0).all() and (memory_df['mem_percent'] <= 100).all()
    
    # Verify we can group and analyze the data
    process_cpu_usage = cpu_df.groupby('command')['cpu'].mean()
    process_memory_usage = memory_df.groupby('command')['mem_percent'].mean()
    
    assert not process_cpu_usage.empty, "Should be able to calculate mean CPU usage by process"
    assert not process_memory_usage.empty, "Should be able to calculate mean memory usage by process"