"""Streamlit app for visualizing pidstats data."""
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from typing import List, Tuple, Optional
from parser import parse_pidstats_file 
from dataframe import create_dataframes

st.set_page_config(
    page_title="Pidsis - Process Performance Analyzer",
    page_icon="📊",
    layout="wide"
)

# Cache the data loading function to improve performance
@st.cache_data
def load_data(file_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load data from a pidstats log file.
    
    Args:
        file_path: Path to the pidstats log file
        
    Returns:
        Tuple of (cpu_df, memory_df)
    """
    cpu_data, memory_data = parse_pidstats_file(file_path)
    return create_dataframes(cpu_data, memory_data)

def get_sample_files() -> List[Path]:
    """Get list of sample pidstats files in data directory.
    
    Returns:
        List of file paths
    """
    data_dir = Path(__file__).parent / "data"
    return sorted(data_dir.glob("pidstats*.log"))

def display_summary_metrics(cpu_df: pd.DataFrame, memory_df: pd.DataFrame):
    """Display summary metrics in the app.
    
    Args:
        cpu_df: DataFrame containing CPU usage data
        memory_df: DataFrame containing memory usage data
    """
    st.subheader("Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Processes", len(cpu_df.index.get_level_values('pid').unique()))
    
    with col2:
        st.metric("Time Points", len(cpu_df.index.get_level_values('timestamp').unique()))
    
    with col3:
        max_cpu_process = cpu_df.groupby('command')['cpu'].max().idxmax()
        max_cpu = cpu_df.groupby('command')['cpu'].max().max()
        st.metric("Highest CPU Process", f"{max_cpu_process} ({max_cpu:.2f}%)")
    
    with col4:
        max_mem_process = memory_df.groupby('command')['mem_percent'].max().idxmax()
        max_mem = memory_df.groupby('command')['mem_percent'].max().max()
        st.metric("Highest Memory Process", f"{max_mem_process} ({max_mem:.2f}%)")

def plot_cpu_time_series(cpu_df: pd.DataFrame, selected_processes: List[str]) -> go.Figure:
    """Create interactive CPU time series plot.
    
    Args:
        cpu_df: DataFrame containing CPU usage data
        selected_processes: List of process names to include
        
    Returns:
        Plotly figure object
    """
    # Filter by selected processes if specified
    if selected_processes:
        filtered_df = cpu_df[cpu_df['command'].isin(selected_processes)]
    else:
        # Get top processes by max CPU usage
        top_processes = cpu_df.groupby('command')['cpu'].max().nlargest(10).index.tolist()
        filtered_df = cpu_df[cpu_df['command'].isin(top_processes)]
    
    # Group by timestamp and command
    cpu_by_command = filtered_df.groupby(['timestamp', 'command'])['cpu'].mean().unstack()
    
    # Create plot with Plotly
    fig = go.Figure()
    for command in cpu_by_command.columns:
        fig.add_trace(go.Scatter(
            x=cpu_by_command.index,
            y=cpu_by_command[command],
            mode='lines+markers',
            name=command,
            hovertemplate='%{y:.2f}% CPU<br>%{x}'
        ))
    
    fig.update_layout(
        title='CPU Usage Over Time',
        xaxis_title='Time',
        yaxis_title='CPU %',
        legend_title='Process',
        hovermode='closest',
        height=500
    )
    
    return fig

def plot_memory_time_series(memory_df: pd.DataFrame, selected_processes: List[str]) -> go.Figure:
    """Create interactive memory time series plot.
    
    Args:
        memory_df: DataFrame containing memory usage data
        selected_processes: List of process names to include
        
    Returns:
        Plotly figure object
    """
    # Filter by selected processes if specified
    if selected_processes:
        filtered_df = memory_df[memory_df['command'].isin(selected_processes)]
    else:
        # Get top processes by max memory usage
        top_processes = memory_df.groupby('command')['mem_percent'].max().nlargest(10).index.tolist()
        filtered_df = memory_df[memory_df['command'].isin(top_processes)]
    
    # Group by timestamp and command
    mem_by_command = filtered_df.groupby(['timestamp', 'command'])['mem_percent'].mean().unstack()
    
    # Create plot with Plotly
    fig = go.Figure()
    for command in mem_by_command.columns:
        fig.add_trace(go.Scatter(
            x=mem_by_command.index,
            y=mem_by_command[command],
            mode='lines+markers',
            name=command,
            hovertemplate='%{y:.2f}% Memory<br>%{x}'
        ))
    
    fig.update_layout(
        title='Memory Usage Over Time',
        xaxis_title='Time',
        yaxis_title='Memory %',
        legend_title='Process',
        hovermode='closest',
        height=500
    )
    
    return fig

def plot_resource_summary(cpu_df: pd.DataFrame, memory_df: pd.DataFrame, num_processes: int = 15) -> Tuple[go.Figure, go.Figure]:
    """Create bar charts summarizing resource usage by process.
    
    Args:
        cpu_df: DataFrame containing CPU usage data
        memory_df: DataFrame containing memory usage data
        num_processes: Number of top processes to display
        
    Returns:
        Tuple of (cpu_fig, mem_fig) Plotly figures
    """
    # CPU summary
    cpu_maxes = cpu_df.groupby('command')['cpu'].max().nlargest(num_processes)
    cpu_fig = px.bar(
        x=cpu_maxes.values,
        y=cpu_maxes.index,
        orientation='h',
        labels={'x': 'Maximum CPU %', 'y': 'Process'},
        title=f'Top {num_processes} Processes by CPU Usage',
        color=cpu_maxes.values,
        color_continuous_scale='blues'
    )
    
    # Memory summary
    mem_maxes = memory_df.groupby('command')['mem_percent'].max().nlargest(num_processes)
    mem_fig = px.bar(
        x=mem_maxes.values,
        y=mem_maxes.index,
        orientation='h',
        labels={'x': 'Maximum Memory %', 'y': 'Process'},
        title=f'Top {num_processes} Processes by Memory Usage',
        color=mem_maxes.values,
        color_continuous_scale='reds'
    )
    
    # Update layout for better appearance
    for fig in [cpu_fig, mem_fig]:
        fig.update_layout(height=400)
    
    return cpu_fig, mem_fig

def plot_correlation_heatmap(cpu_df: pd.DataFrame, memory_df: pd.DataFrame, selected_processes: List[str]) -> Optional[go.Figure]:
    """Create heatmap showing correlation between CPU and memory usage.
    
    Args:
        cpu_df: DataFrame containing CPU usage data
        memory_df: DataFrame containing memory usage data
        selected_processes: List of process names to include
        
    Returns:
        Plotly figure object or None if insufficient data
    """
    if not selected_processes:
        return None
    
    # Prepare data for correlation analysis
    data = []
    for process in selected_processes:
        # Get CPU and memory data for the process
        cpu_process = cpu_df[cpu_df['command'] == process]
        mem_process = memory_df[memory_df['command'] == process]
        
        # Make sure we have data for this process
        if cpu_process.empty or mem_process.empty:
            continue
        
        # Merge on timestamp and pid
        merged = pd.merge(
            cpu_process.reset_index(), 
            mem_process.reset_index(),
            on=['timestamp', 'pid'],
            suffixes=('_cpu', '_mem')
        )
        
        if not merged.empty:
            data.append(merged)
    
    if not data:
        return None
    
    # Combine all process data
    combined = pd.concat(data)
    
    # Calculate correlation matrix
    corr_cols = ['usr', 'system', 'cpu', 'mem_percent', 'vsz', 'rss']
    corr_data = combined[corr_cols].corr()
    
    # Create heatmap
    fig = px.imshow(
        corr_data,
        text_auto=True,
        color_continuous_scale='RdBu_r',
        title='Resource Usage Correlation Matrix'
    )
    
    fig.update_layout(height=500)
    return fig

def main():
    """Main application function."""
    st.title("Pidsis - Process Performance Analyzer")
    st.write("Analyze CPU and memory usage from pidstats log files")
    
    # Sidebar for file selection and controls
    with st.sidebar:
        st.header("Data Selection")
        
        # File upload or sample selection
        upload_method = st.radio("Select data source:", ["Upload File", "Use Sample File"])
        
        if upload_method == "Upload File":
            uploaded_file = st.file_uploader("Upload a pidstats log file", type=["log"])
            if uploaded_file:
                # Save uploaded file temporarily
                temp_path = Path("temp_upload.log")
                temp_path.write_bytes(uploaded_file.getvalue())
                file_path = str(temp_path)
            else:
                st.info("Please upload a pidstats log file to begin")
                return
        else:
            sample_files = get_sample_files()
            if not sample_files:
                st.error("No sample files found in data directory")
                return
            
            sample_file_names = [f.name for f in sample_files]
            selected_file = st.selectbox("Select a sample file", sample_file_names)
            file_path = str(next(f for f in sample_files if f.name == selected_file))
        
        st.divider()
        st.header("Visualization Options")
        show_raw_data = st.checkbox("Show raw data tables", value=False)
    
    # Load the data
    try:
        with st.spinner("Loading and parsing data..."):
            cpu_df, memory_df = load_data(file_path)
        
        if cpu_df.empty or memory_df.empty:
            st.error("No valid data found in the file")
            return
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return
    
    # Display summary metrics
    display_summary_metrics(cpu_df, memory_df)
    
    # Process selection
    st.subheader("Process Selection")
    all_processes = sorted(cpu_df['command'].unique())
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_processes = st.multiselect(
            "Select processes to analyze (leave empty for top processes by usage)",
            all_processes
        )
    
    with col2:
        num_top_processes = st.slider("Number of top processes to show", 5, 30, 15)
    
    # Time series tabs
    st.subheader("Resource Usage Over Time")
    tab1, tab2 = st.tabs(["CPU Usage", "Memory Usage"])
    
    with tab1:
        cpu_fig = plot_cpu_time_series(cpu_df, selected_processes)
        st.plotly_chart(cpu_fig, use_container_width=True)
    
    with tab2:
        mem_fig = plot_memory_time_series(memory_df, selected_processes)
        st.plotly_chart(mem_fig, use_container_width=True)
    
    # Resource summary
    st.subheader("Resource Usage Summary")
    cpu_summary_fig, mem_summary_fig = plot_resource_summary(cpu_df, memory_df, num_top_processes)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(cpu_summary_fig, use_container_width=True)
    
    with col2:
        st.plotly_chart(mem_summary_fig, use_container_width=True)
    
    # Correlation analysis
    st.subheader("Resource Correlation Analysis")
    if selected_processes:
        corr_fig = plot_correlation_heatmap(cpu_df, memory_df, selected_processes)
        if corr_fig:
            st.plotly_chart(corr_fig, use_container_width=True)
        else:
            st.info("Insufficient data for correlation analysis. Select different processes.")
    else:
        st.info("Select specific processes to view correlation analysis")
    
    # Show raw data if requested
    if show_raw_data:
        st.subheader("Raw Data")
        tab1, tab2 = st.tabs(["CPU Data", "Memory Data"])
        
        with tab1:
            st.dataframe(cpu_df.reset_index())
        
        with tab2:
            st.dataframe(memory_df.reset_index())

def run():
    """Entry point for the Streamlit app."""
    main()

if __name__ == "__main__":
    run()