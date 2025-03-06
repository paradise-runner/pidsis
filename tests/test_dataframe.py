"""Tests for DataFrame creation"""

import pytest
import pandas as pd
from pidsis import dataframe

def test_create_cpu_dataframe():
    """Test basic CPU DataFrame creation with minimal data"""
    cpu_data = [{
        'timestamp': '09:55:46 PM',
        'pid': 123,
        'uid': 1000,
        'usr': 0.5,
        'system': 0.2,
        'guest': 0.0,
        'wait': 0.1,
        'cpu': 0.8,
        'cpu_id': 0,
        'command': 'test_process'
    }]
    
    df = dataframe.create_cpu_dataframe(cpu_data)
    
    # Verify DataFrame was created
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    
    # Verify multi-index
    assert df.index.names == ['timestamp', 'pid']
    
    # Verify columns exist and order
    expected_columns = ['uid', 'usr', 'system', 'guest', 'wait', 'cpu', 'cpu_num', 'command']
    assert list(df.columns) == expected_columns

def test_cpu_dataframe_types():
    """Test data type conversions in CPU DataFrame"""
    cpu_data = [{
        'timestamp': '09:55:46 PM',
        'pid': 123,
        'uid': 1000,
        'usr': '0.5',  # String values should be converted
        'system': '0.2',
        'guest': '0.0',
        'wait': '0.1',
        'cpu': '0.8',
        'cpu_id': '0',
        'command': 'test_process'
    }]
    
    df = dataframe.create_cpu_dataframe(cpu_data)
    
    # Verify numeric types
    assert df['uid'].dtype == 'int64'
    assert df['usr'].dtype == 'float64'
    assert df['system'].dtype == 'float64'
    assert df['guest'].dtype == 'float64'
    assert df['wait'].dtype == 'float64'
    assert df['cpu'].dtype == 'float64'
    assert df['cpu_num'].dtype == 'int64'
    assert df['command'].dtype == 'object'  # String/object type

def test_create_cpu_dataframe_empty():
    """Test handling of empty input data"""
    df = dataframe.create_cpu_dataframe([])
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0

def test_create_cpu_dataframe_multiple_timestamps():
    """Test DataFrame creation with multiple timestamps"""
    cpu_data = [
        {
            'timestamp': '09:55:46 PM',
            'pid': 123,
            'uid': 1000,
            'usr': 0.5,
            'system': 0.2,
            'guest': 0.0,
            'wait': 0.1,
            'cpu': 0.8,
            'cpu_id': 0,
            'command': 'test_process'
        },
        {
            'timestamp': '09:56:46 PM',
            'pid': 123,
            'uid': 1000,
            'usr': 0.6,
            'system': 0.3,
            'guest': 0.0,
            'wait': 0.1,
            'cpu': 1.0,
            'cpu_id': 0,
            'command': 'test_process'
        }
    ]
    
    df = dataframe.create_cpu_dataframe(cpu_data)
    
    # Verify multiple entries
    assert len(df) == 2
    assert len(df.index.unique(level='timestamp')) == 2

def test_create_cpu_dataframe_validation():
    """Test validation of CPU DataFrame values"""
    cpu_data = [{
        'timestamp': '09:55:46 PM',
        'pid': 123,
        'uid': 1000,
        'usr': 0.5,
        'system': 0.2,
        'guest': 0.0,
        'wait': 0.1,
        'cpu': 0.8,
        'cpu_id': 0,
        'command': 'test_process'
    }]
    
    df = dataframe.create_cpu_dataframe(cpu_data)
    
    # Verify numeric ranges
    assert (df['usr'] >= 0).all() and (df['usr'] <= 100).all()
    assert (df['system'] >= 0).all() and (df['system'] <= 100).all()
    assert (df['guest'] >= 0).all() and (df['guest'] <= 100).all()
    assert (df['wait'] >= 0).all() and (df['wait'] <= 100).all()
    assert (df['cpu'] >= 0).all() and (df['cpu'] <= 100).all()

def test_create_cpu_dataframe_real_data():
    """Test CPU DataFrame creation with real parsed data"""
    # Create test data mimicking real pidstats output
    cpu_data = [
        {
            'timestamp': '09:55:46 PM',
            'pid': 497,
            'uid': 0,
            'usr': 0.02,
            'system': 0.02,
            'guest': 0.00,
            'wait': 0.02,
            'cpu': 0.03,
            'cpu_id': 0,
            'command': 'systemd-journal'
        },
        {
            'timestamp': '09:55:46 PM',
            'pid': 670,
            'uid': 993,
            'usr': 0.17,
            'system': 0.02,
            'guest': 0.00,
            'wait': 0.00,
            'cpu': 0.18,
            'cpu_id': 0,
            'command': 'prometheus'
        }
    ]
    
    df = dataframe.create_cpu_dataframe(cpu_data)
    
    # Verify structure with real data
    assert len(df) == 2
    assert df.index.names == ['timestamp', 'pid']
    
    # Check specific values
    prometheus = df.xs(670, level='pid')
    assert prometheus['usr'].iloc[0] == 0.17
    assert prometheus['system'].iloc[0] == 0.02
    assert prometheus['cpu'].iloc[0] == 0.18
    assert prometheus['command'].iloc[0] == 'prometheus'

def test_missing_values():
    """Test handling of missing or invalid values"""
    # Test with missing optional columns
    minimal_data = [{
        'timestamp': '09:55:46 PM',
        'pid': 123,
        'uid': 1000,
        'usr': 0.5,
        'system': 0.2,
        'cpu': 0.7,
        'command': 'test_process'
    }]
    
    df = dataframe.create_cpu_dataframe(minimal_data)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1

def test_multiple_cpu_entries():
    """Test handling of multiple CPUs and processes"""
    cpu_data = [
        {
            'timestamp': '09:55:46 PM',
            'pid': 123,
            'uid': 1000,
            'usr': 0.5,
            'system': 0.2,
            'guest': 0.0,
            'wait': 0.1,
            'cpu': 0.8,
            'cpu_id': 0,
            'command': 'process1'
        },
        {
            'timestamp': '09:55:46 PM',
            'pid': 124,
            'uid': 1000,
            'usr': 0.3,
            'system': 0.1,
            'guest': 0.0,
            'wait': 0.0,
            'cpu': 0.4,
            'cpu_id': 1,
            'command': 'process2'
        }
    ]
    
    df = dataframe.create_cpu_dataframe(cpu_data)
    
    # Verify multiple processes
    assert len(df) == 2
    assert len(df['cpu_num'].unique()) == 2
    
    # Verify we can group by command
    by_command = df.groupby('command')['cpu'].sum()
    assert len(by_command) == 2
    assert by_command['process1'] == 0.8
    assert by_command['process2'] == 0.4

def test_create_memory_dataframe():
    """Test basic memory DataFrame creation with minimal data"""
    memory_data = [{
        'timestamp': '09:55:46 PM',
        'pid': 123,
        'uid': 1000,
        'minflt': 0.05,
        'majflt': 0.00,
        'vsz': 2124408,
        'rss': 67916,
        'mem_percent': 8.61,
        'command': 'test_process'
    }]
    
    df = dataframe.create_memory_dataframe(memory_data)
    
    # Verify DataFrame was created
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    
    # Verify multi-index
    assert df.index.names == ['timestamp', 'pid']
    
    # Verify columns exist and order
    expected_columns = ['uid', 'minflt', 'majflt', 'vsz', 'rss', 'mem_percent', 'command']
    assert list(df.columns) == expected_columns

def test_memory_dataframe_types():
    """Test data type conversions in memory DataFrame"""
    memory_data = [{
        'timestamp': '09:55:46 PM',
        'pid': 123,
        'uid': 1000,
        'minflt': '0.05',  # String values should be converted
        'majflt': '0.00',
        'vsz': '2124408',
        'rss': '67916',
        'mem_percent': '8.61',
        'command': 'test_process'
    }]
    
    df = dataframe.create_memory_dataframe(memory_data)
    
    # Verify numeric types
    assert df['uid'].dtype == 'int64'
    assert df['minflt'].dtype == 'float64'
    assert df['majflt'].dtype == 'float64'
    assert df['vsz'].dtype == 'int64'
    assert df['rss'].dtype == 'int64'
    assert df['mem_percent'].dtype == 'float64'
    assert df['command'].dtype == 'object'  # String/object type

def test_create_memory_dataframe_empty():
    """Test handling of empty input data"""
    df = dataframe.create_memory_dataframe([])
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0

def test_create_memory_dataframe_multiple_timestamps():
    """Test DataFrame creation with multiple timestamps"""
    memory_data = [
        {
            'timestamp': '09:55:46 PM',
            'pid': 123,
            'uid': 1000,
            'minflt': 0.05,
            'majflt': 0.00,
            'vsz': 2124408,
            'rss': 67916,
            'mem_percent': 8.61,
            'command': 'test_process'
        },
        {
            'timestamp': '09:56:46 PM',
            'pid': 123,
            'uid': 1000,
            'minflt': 0.06,
            'majflt': 0.00,
            'vsz': 2124500,
            'rss': 68000,
            'mem_percent': 8.63,
            'command': 'test_process'
        }
    ]
    
    df = dataframe.create_memory_dataframe(memory_data)
    
    # Verify multiple entries
    assert len(df) == 2
    assert len(df.index.unique(level='timestamp')) == 2

def test_create_memory_dataframe_validation():
    """Test validation of memory DataFrame values"""
    memory_data = [{
        'timestamp': '09:55:46 PM',
        'pid': 123,
        'uid': 1000,
        'minflt': 0.05,
        'majflt': 0.00,
        'vsz': 2124408,
        'rss': 67916,
        'mem_percent': 8.61,
        'command': 'test_process'
    }]
    
    df = dataframe.create_memory_dataframe(memory_data)
    
    # Verify numeric ranges
    assert (df['minflt'] >= 0).all()
    assert (df['majflt'] >= 0).all()
    assert (df['vsz'] >= 0).all()
    assert (df['rss'] >= 0).all()
    assert (df['mem_percent'] >= 0).all() and (df['mem_percent'] <= 100).all()

def test_create_memory_dataframe_real_data():
    """Test memory DataFrame creation with real parsed data"""
    # Create test data mimicking real pidstats output
    memory_data = [
        {
            'timestamp': '09:55:46 PM',
            'pid': 497,
            'uid': 0,
            'minflt': 0.17,
            'majflt': 0.00,
            'vsz': 129300,
            'rss': 7036,
            'mem_percent': 0.89,
            'command': 'systemd-journal'
        },
        {
            'timestamp': '09:55:46 PM',
            'pid': 670,
            'uid': 993,
            'minflt': 0.05,
            'majflt': 0.00,
            'vsz': 2124408,
            'rss': 67916,
            'mem_percent': 8.61,
            'command': 'prometheus'
        }
    ]
    
    df = dataframe.create_memory_dataframe(memory_data)
    
    # Verify structure with real data
    assert len(df) == 2
    assert df.index.names == ['timestamp', 'pid']
    
    # Check specific values
    prometheus = df.xs(670, level='pid')
    assert prometheus['vsz'].iloc[0] == 2124408
    assert prometheus['rss'].iloc[0] == 67916
    assert prometheus['mem_percent'].iloc[0] == 8.61
    assert prometheus['command'].iloc[0] == 'prometheus'

def test_memory_missing_values():
    """Test handling of missing or invalid values"""
    # Test with missing optional columns
    minimal_data = [{
        'timestamp': '09:55:46 PM',
        'pid': 123,
        'uid': 1000,
        'vsz': 2124408,
        'rss': 67916,
        'mem_percent': 8.61,
        'command': 'test_process'
    }]
    
    df = dataframe.create_memory_dataframe(minimal_data)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df['minflt'].iloc[0] == 0.0  # Default value
    assert df['majflt'].iloc[0] == 0.0  # Default value

def test_multiple_memory_entries():
    """Test handling of multiple processes"""
    memory_data = [
        {
            'timestamp': '09:55:46 PM',
            'pid': 123,
            'uid': 1000,
            'minflt': 0.05,
            'majflt': 0.00,
            'vsz': 2124408,
            'rss': 67916,
            'mem_percent': 8.61,
            'command': 'process1'
        },
        {
            'timestamp': '09:55:46 PM',
            'pid': 124,
            'uid': 1000,
            'minflt': 0.06,
            'majflt': 0.01,
            'vsz': 1241952,
            'rss': 16172,
            'mem_percent': 2.05,
            'command': 'process2'
        }
    ]
    
    df = dataframe.create_memory_dataframe(memory_data)
    
    # Verify multiple processes
    assert len(df) == 2
    
    # Verify we can group by command
    by_command = df.groupby('command')['mem_percent'].sum()
    assert len(by_command) == 2
    assert by_command['process1'] == 8.61
    assert by_command['process2'] == 2.05