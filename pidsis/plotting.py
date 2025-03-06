"""Plotting functionality for pidsis package."""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def sort_and_limit_by_max_value(df_grouped: pd.DataFrame, limit: int = 20) -> pd.DataFrame:
    """Sort DataFrame columns by maximum values and limit to top N.
    
    Args:
        df_grouped: DataFrame with time series data grouped by command
        limit: Maximum number of processes to include
        
    Returns:
        DataFrame sorted by max values and limited to top N processes
    """
    max_values = df_grouped.max()
    sorted_cols = max_values.sort_values(ascending=False).index[:limit]
    return df_grouped[sorted_cols]


def create_cpu_time_series_plot(cpu_df: pd.DataFrame, output_path: Path) -> None:
    """Create time series plot of CPU usage by process.
    
    Args:
        cpu_df: DataFrame containing CPU usage data
        output_path: Path to save the plot
    """
    plt.figure(figsize=(12, 6))
    
    # Group by command and get mean values over time
    cpu_by_command = cpu_df.groupby(['timestamp', 'command'])['cpu'].mean().unstack()
    # Sort columns by maximum values and limit to top 20
    cpu_by_command = sort_and_limit_by_max_value(cpu_by_command)
    
    # Plot CPU usage
    ax = plt.gca()
    cpu_by_command.plot(ax=ax, linestyle='-', marker='o')
    ax.set_xlabel('Time')
    ax.set_ylabel('CPU %')
    ax.grid(True)
    
    plt.title('CPU Usage Over Time by Top 20 Processes')
    plt.legend(bbox_to_anchor=(1.05, 1.0))
    plt.tight_layout()
    
    plt.savefig(output_path / 'cpu_time_series.png', bbox_inches='tight')
    plt.close()


def create_memory_time_series_plot(memory_df: pd.DataFrame, output_path: Path) -> None:
    """Create time series plot of memory usage by process.
    
    Args:
        memory_df: DataFrame containing memory usage data
        output_path: Path to save the plot
    """
    plt.figure(figsize=(12, 6))
    
    # Group by command and get mean values over time
    mem_by_command = memory_df.groupby(['timestamp', 'command'])['mem_percent'].mean().unstack()
    # Sort columns by maximum values and limit to top 20
    mem_by_command = sort_and_limit_by_max_value(mem_by_command)
    
    # Plot memory usage
    ax = plt.gca()
    mem_by_command.plot(ax=ax, linestyle='-', marker='o')
    ax.set_xlabel('Time')
    ax.set_ylabel('Memory %')
    ax.grid(True)
    
    plt.title('Memory Usage Over Time by Top 20 Processes')
    plt.legend(bbox_to_anchor=(1.05, 1.0))
    plt.tight_layout()
    
    plt.savefig(output_path / 'memory_time_series.png', bbox_inches='tight')
    plt.close()


def create_cpu_summary_plot(cpu_df: pd.DataFrame, output_path: Path) -> None:
    """Create bar plot of average CPU usage by process.
    
    Args:
        cpu_df: DataFrame containing CPU usage data
        output_path: Path to save the plot
    """
    plt.figure(figsize=(10, 6))
    
    # Calculate max usage by command to determine order
    cpu_maxes = cpu_df.groupby('command')['cpu'].max()
    cpu_maxes = cpu_maxes.sort_values(ascending=True)[-20:]  # Get top 20
    
    # Create bar plot
    y_pos = range(len(cpu_maxes))
    plt.barh(y_pos, cpu_maxes, color='skyblue')
    
    plt.yticks(y_pos, cpu_maxes.index)
    plt.xlabel('Maximum CPU %')
    plt.title('Maximum CPU Usage by Top 20 Processes')
    plt.grid(True, axis='x')
    
    plt.savefig(output_path / 'cpu_summary.png', bbox_inches='tight')
    plt.close()


def create_memory_summary_plot(memory_df: pd.DataFrame, output_path: Path) -> None:
    """Create bar plot of average memory usage by process.
    
    Args:
        memory_df: DataFrame containing memory usage data
        output_path: Path to save the plot
    """
    plt.figure(figsize=(10, 6))
    
    # Calculate max usage by command to determine order
    mem_maxes = memory_df.groupby('command')['mem_percent'].max()
    mem_maxes = mem_maxes.sort_values(ascending=True)[-20:]  # Get top 20
    
    # Create bar plot
    y_pos = range(len(mem_maxes))
    plt.barh(y_pos, mem_maxes, color='lightcoral')
    
    plt.yticks(y_pos, mem_maxes.index)
    plt.xlabel('Maximum Memory %')
    plt.title('Maximum Memory Usage by Top 20 Processes')
    plt.grid(True, axis='x')
    
    plt.savefig(output_path / 'memory_summary.png', bbox_inches='tight')
    plt.close()


def generate_plots(cpu_df: pd.DataFrame, memory_df: pd.DataFrame, output_path: Path) -> None:
    """Generate all plots for CPU and memory usage.
    
    Args:
        cpu_df: DataFrame containing CPU usage data
        memory_df: DataFrame containing memory usage data
        output_path: Path to save the plots
    """
    create_cpu_time_series_plot(cpu_df, output_path)
    create_memory_time_series_plot(memory_df, output_path)
    create_cpu_summary_plot(cpu_df, output_path)
    create_memory_summary_plot(memory_df, output_path)