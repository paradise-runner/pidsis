"""Module for converting parsed pidstats data into pandas DataFrames"""

from typing import List, Dict, Any, Tuple
import pandas as pd

def create_cpu_dataframe(cpu_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert CPU statistics data into a properly formatted DataFrame.
    
    Args:
        cpu_data: List of dictionaries containing CPU statistics
        
    Returns:
        DataFrame with multi-index [timestamp, pid] and proper column names/types
    """
    if not cpu_data:
        return pd.DataFrame()
        
    # Create DataFrame from raw data
    df = pd.DataFrame(cpu_data)
    
    # Set multi-index on timestamp and PID
    df.set_index(['timestamp', 'pid'], inplace=True)
    
    # Ensure proper column names as per spec
    rename_map = {
        'usr': 'usr',
        'system': 'system',
        'guest': 'guest',
        'wait': 'wait',
        'cpu': 'cpu',
        'cpu_id': 'cpu_num',
        'command': 'command',
        'uid': 'uid'
    }
    df.rename(columns=rename_map, inplace=True)
    
    # Convert data types only for columns that exist
    type_map = {
        'usr': float,
        'system': float,
        'guest': float,
        'wait': float,
        'cpu': float,
        'cpu_num': int,
        'uid': int
    }
    for col, dtype in type_map.items():
        if col in df.columns:
            df[col] = df[col].astype(dtype)
    
    # Fill missing optional columns with defaults
    if 'guest' not in df.columns:
        df['guest'] = 0.0
    if 'wait' not in df.columns:
        df['wait'] = 0.0
    if 'cpu_num' not in df.columns:
        df['cpu_num'] = 0
    
    # Ensure consistent column order
    columns = ['uid', 'usr', 'system', 'guest', 'wait', 'cpu', 'cpu_num', 'command']
    df = df.reindex(columns=columns)
    
    return df

def create_memory_dataframe(memory_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert memory statistics data into a properly formatted DataFrame.
    
    Args:
        memory_data: List of dictionaries containing memory statistics
        
    Returns:
        DataFrame with multi-index [timestamp, pid] and proper column names/types
    """
    if not memory_data:
        return pd.DataFrame()
        
    # Create DataFrame from raw data
    df = pd.DataFrame(memory_data)
    
    # Set multi-index on timestamp and PID
    df.set_index(['timestamp', 'pid'], inplace=True)
    
    # Ensure proper column names as per spec
    rename_map = {
        'minflt': 'minflt',
        'majflt': 'majflt',
        'vsz': 'vsz',
        'rss': 'rss',
        'mem_percent': 'mem_percent',
        'command': 'command',
        'uid': 'uid'
    }
    df.rename(columns=rename_map, inplace=True)
    
    # Convert data types only for columns that exist
    type_map = {
        'uid': int,
        'minflt': float,
        'majflt': float,
        'vsz': int,
        'rss': int,
        'mem_percent': float
    }
    for col, dtype in type_map.items():
        if col in df.columns:
            df[col] = df[col].astype(dtype)
    
    # Fill missing optional columns with defaults
    if 'minflt' not in df.columns:
        df['minflt'] = 0.0
    if 'majflt' not in df.columns:
        df['majflt'] = 0.0
    
    # Ensure consistent column order
    columns = ['uid', 'minflt', 'majflt', 'vsz', 'rss', 'mem_percent', 'command']
    df = df.reindex(columns=columns)
    
    return df

def create_dataframes(cpu_data: List[Dict[str, Any]], 
                     memory_data: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Create both CPU and memory DataFrames from parsed data.
    
    Args:
        cpu_data: List of dictionaries containing CPU statistics
        memory_data: List of dictionaries containing memory statistics
        
    Returns:
        Tuple of (cpu_df, memory_df) with properly formatted DataFrames
    """
    cpu_df = create_cpu_dataframe(cpu_data)
    memory_df = create_memory_dataframe(memory_data)
    return cpu_df, memory_df