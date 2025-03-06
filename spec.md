# PidStats Parser Specification

## Project Overview
Create a Python script that parses a pidstats log file and converts the data into two separate pandas DataFrames - one for CPU statistics and one for memory statistics. The script will be used for data visualization and analysis.

## Requirements

### Functional Requirements
- Parse any pidstats log file with the format shown in the provided example
- Extract CPU usage data into one DataFrame
- Extract memory usage data into another DataFrame
- Handle multiple time intervals within the same file
- Preserve timestamps as a time index for each data point
- Convert all numeric data to appropriate types (float/int)
- Support command line operation with file path as input

### Technical Requirements
- Python 3.8+
- Pandas for DataFrame manipulation
- Rich test suite with integration tests

## Input Data Format
The input file contains alternating sections of CPU and memory statistics:

1. **CPU Statistics Sections** begin with header row containing:
   - Timestamp, UID, PID, %usr, %system, %guest, %wait, %CPU, CPU, Command

2. **Memory Statistics Sections** begin with header row containing:
   - Timestamp, UID, PID, minflt/s, majflt/s, VSZ, RSS, %MEM, Command

Each section contains multiple processes at the same timestamp.

## Output Data Format

### CPU DataFrame
- **Index**: Multi-index of [timestamp, PID]
- **Columns**:
  - `uid`: int - User ID
  - `usr_pct`: float - User space CPU utilization percentage
  - `system_pct`: float - System CPU utilization percentage
  - `guest_pct`: float - Guest CPU utilization percentage
  - `wait_pct`: float - CPU wait percentage
  - `cpu_pct`: float - Total CPU utilization percentage
  - `cpu_num`: int - CPU number
  - `command`: str - Command name

### Memory DataFrame
- **Index**: Multi-index of [timestamp, PID]
- **Columns**:
  - `uid`: int - User ID
  - `minflt_per_sec`: float - Minor faults per second
  - `majflt_per_sec`: float - Major faults per second
  - `vsz`: int - Virtual memory size in KB
  - `rss`: int - Resident set size in KB
  - `mem_pct`: float - Memory utilization percentage
  - `command`: str - Command name

## Architecture and Implementation

### Core Components

1. **File Reader**: Read log file lines
2. **Section Detector**: Identify CPU/Memory sections in the log
3. **Section Parser**: Parse each type of section into structured data
4. **DataFrame Builder**: Convert parsed data into properly formatted DataFrames
5. **Main Controller**: Orchestrate the overall process

### Implementation Details

```python
# File structure
pidsis/
  ├── __init__.py
  ├── parser.py         # Core parsing logic
  ├── dataframe.py      # DataFrame creation functions
  ├── main.py           # Script entry point
  ├── utils.py          # Utility functions
  └── tests/
      ├── __init__.py
      ├── test_parser.py
      ├── test_dataframe.py
      ├── test_integration.py
      └── data/
          └── pidstats_sample.log
```

## Processing Logic

1. **Preprocessing**:
   - Read the file line by line
   - Skip the initial Linux system information line
   - Identify section headers to determine data type (CPU or memory)

2. **Section Parsing**:
   - Parse timestamp from section header
   - Extract column names from section header
   - For each data row:
     - Extract values according to column positions
     - Convert to appropriate data types
     - Associate with the current timestamp
     - Store in appropriate collection (CPU or memory)

3. **DataFrame Creation**:
   - Convert collections to pandas DataFrames
   - Set multi-index on timestamp and PID
   - Ensure proper column data types
   - Name columns appropriately

## Error Handling

- Validate input file exists and is readable
- Check for expected header formats
- Handle unexpected log format variations
- Provide meaningful error messages for:
  - Missing files
  - Permission issues
  - Malformed log entries
  - Unexpected data types
  - Memory issues with large files

## Testing Strategy

### Unit Tests
- Test section detection functions
- Test parsing of individual log lines
- Test data type conversions
- Test timestamp extraction and formatting

### Integration Tests
- End-to-end test using sample log files
- Verify correct DataFrame structure
- Check data type conversions
- Validate multi-index creation
- Compare parsed output against expected values
- Test error handling scenarios

### Test Data
- Use excerpts of the provided log file
- Create synthetic test cases for edge cases
- Include malformed data for error testing

## Script Usage

```
# Basic usage
python -m pidsis.main /path/to/pidstats.log

# Save results to CSV
python -m pidsis.main /path/to/pidstats.log --output-dir ./output

# Get help
python -m pidsis.main --help
```

## Sample Implementation

Here's a skeleton of the core implementation:

```python
# parser.py
def parse_pidstats_file(file_path):
    """Parse a pidstats log file into CPU and memory data."""
    cpu_data = []
    mem_data = []
    current_section = None
    section_timestamp = None
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and Linux system info
            if not line or line.startswith('Linux'):
                continue
                
            # Check if this is a header line
            if 'UID' in line and 'PID' in line:
                if '%usr' in line:  # CPU section header
                    current_section = 'cpu'
                    section_timestamp = extract_timestamp(line)
                elif 'minflt/s' in line:  # Memory section header
                    current_section = 'mem'
                    section_timestamp = extract_timestamp(line)
                continue
            
            # Parse data rows
            if current_section == 'cpu':
                cpu_entry = parse_cpu_line(line, section_timestamp)
                if cpu_entry:
                    cpu_data.append(cpu_entry)
            elif current_section == 'mem':
                mem_entry = parse_mem_line(line, section_timestamp)
                if mem_entry:
                    mem_data.append(mem_entry)
    
    return cpu_data, mem_data

# dataframe.py
def create_dataframes(cpu_data, mem_data):
    """Convert parsed data lists into pandas DataFrames."""
    cpu_df = pd.DataFrame(cpu_data)
    mem_df = pd.DataFrame(mem_data)
    
    # Set multi-index on timestamp and PID
    cpu_df.set_index(['timestamp', 'pid'], inplace=True)
    mem_df.set_index(['timestamp', 'pid'], inplace=True)
    
    # Convert data types
    cpu_df = convert_cpu_datatypes(cpu_df)
    mem_df = convert_mem_datatypes(mem_df)
    
    return cpu_df, mem_df

# main.py
def main():
    parser = argparse.ArgumentParser(description='Parse pidstats log file')
    parser.add_argument('file_path', help='Path to pidstats log file')
    parser.add_argument('--output-dir', help='Directory to save output CSVs')
    args = parser.parse_args()
    
    try:
        cpu_data, mem_data = parse_pidstats_file(args.file_path)
        cpu_df, mem_df = create_dataframes(cpu_data, mem_data)
        
        print(f"CPU DataFrame shape: {cpu_df.shape}")
        print(f"Memory DataFrame shape: {mem_df.shape}")
        
        if args.output_dir:
            os.makedirs(args.output_dir, exist_ok=True)
            cpu_df.to_csv(os.path.join(args.output_dir, 'cpu_stats.csv'))
            mem_df.to_csv(os.path.join(args.output_dir, 'mem_stats.csv'))
            print(f"CSV files saved to {args.output_dir}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Integration Test Example

```python
def test_end_to_end_parsing():
    """Test end-to-end parsing of a sample log file."""
    sample_log = os.path.join(os.path.dirname(__file__), 'data', 'pidstats_sample.log')
    
    cpu_data, mem_data = parse_pidstats_file(sample_log)
    cpu_df, mem_df = create_dataframes(cpu_data, mem_data)
    
    # Verify CPU DataFrame
    assert not cpu_df.empty
    assert 'usr_pct' in cpu_df.columns
    assert 'system_pct' in cpu_df.columns
    assert 'command' in cpu_df.columns
    
    # Verify Memory DataFrame
    assert not mem_df.empty
    assert 'minflt_per_sec' in mem_df.columns
    assert 'vsz' in mem_df.columns
    assert 'mem_pct' in mem_df.columns
    
    # Check specific data point
    assert 'next-server' in ' '.join(cpu_df[cpu_df['cpu_pct'] > 0.1]['command'].tolist())
```