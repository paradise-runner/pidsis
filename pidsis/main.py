"""Command-line interface for pidsis package."""

import argparse
import sys
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
from . import parser, dataframe, plotting


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the pidsis CLI.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description='Parse pidstats log files into pandas DataFrames'
    )
    parser.add_argument(
        'file_path',
        type=str,
        help='Path to the pidstats log file'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Directory to save output CSV files and plots (default: ./outputs)'
    )
    parser.add_argument(
        '--no-output',
        action='store_true',
        help='Disable saving CSV files and plots'
    )
    return parser


def parse_data(file_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Parse pidstats log file and create DataFrames.
    
    Args:
        file_path: Path to the pidstats log file
        
    Returns:
        Tuple of (cpu_df, memory_df) DataFrames
        
    Raises:
        FileNotFoundError: If the input file doesn't exist
        PermissionError: If there are permission issues accessing the file
    """
    cpu_data, memory_data = parser.parse_pidstats_file(file_path)
    return dataframe.create_dataframes(cpu_data, memory_data)


def print_dataframe_info(cpu_df: pd.DataFrame, memory_df: pd.DataFrame) -> None:
    """Print summary information about the DataFrames.
    
    Args:
        cpu_df: DataFrame containing CPU usage data
        memory_df: DataFrame containing memory usage data
    """
    print(f"CPU DataFrame shape: {cpu_df.shape}")
    print(f"\tTimestamps: {len(cpu_df.index.unique(level='timestamp'))}")
    print(f"\tUnique processes: {len(cpu_df.index.unique(level='pid'))}")
    
    print(f"\nMemory DataFrame shape: {memory_df.shape}")
    print(f"\tTimestamps: {len(memory_df.index.unique(level='timestamp'))}")
    print(f"\tUnique processes: {len(memory_df.index.unique(level='pid'))}")


def save_data(cpu_df: pd.DataFrame, memory_df: pd.DataFrame, output_path: Path) -> None:
    """Save DataFrames to CSV files.
    
    Args:
        cpu_df: DataFrame containing CPU usage data
        memory_df: DataFrame containing memory usage data
        output_path: Path to save the CSV files
    """
    output_path.mkdir(parents=True, exist_ok=True)
    
    cpu_file = output_path / 'cpu_stats.csv'
    memory_file = output_path / 'mem_stats.csv'
    
    cpu_df.to_csv(cpu_file)
    memory_df.to_csv(memory_file)
    
    print(f"\nCSV files saved to:")
    print(f"\t{cpu_file}")
    print(f"\t{memory_file}")


def process_file(file_path: str, output_dir: Optional[str] = None, no_output: bool = False) -> int:
    """Process a pidstats log file and save CSV files and plots.
    
    Args:
        file_path: Path to the pidstats log file
        output_dir: Optional directory to save CSV output and plots (default: ./outputs)
        no_output: If True, skip saving CSV files and plots
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Parse file and create DataFrames
        cpu_df, memory_df = parse_data(file_path)

        # filter out the last anything above the last 500 rows
        cpu_df = cpu_df.iloc[-10000:]
        memory_df = memory_df.iloc[-10000:]

        print_dataframe_info(cpu_df, memory_df)
        
        # Skip output if requested
        if no_output:
            return 0
            
        # Set up output directory and save data
        output_path = Path(output_dir) if output_dir else Path('outputs')
        save_data(cpu_df, memory_df, output_path)
        
        # Generate plots
        plotting.generate_plots(cpu_df, memory_df, output_path)
        
        print(f"\nPlots saved to:")
        print(f"\t{output_path}/cpu_time_series.png")
        print(f"\t{output_path}/memory_time_series.png")
        print(f"\t{output_path}/cpu_summary.png")
        print(f"\t{output_path}/memory_summary.png")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {file_path}", file=sys.stderr)
        return 1
    except PermissionError as e:
        print(f"Error: Permission denied accessing file - {file_path}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point for pidsis command-line interface.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    arg_parser = create_parser()
    args = arg_parser.parse_args()
    return process_file(args.file_path, args.output_dir, args.no_output)