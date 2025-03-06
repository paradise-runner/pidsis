# Building a PidStats Parser - Implementation Blueprint

After reviewing the specification, I'll outline a step-by-step approach to building this project using test-driven development. I'll break this down into manageable, iterative chunks that build on each other, with each step small enough to implement safely but substantial enough to make progress.

## Project Implementation Blueprint

### 1. Project Setup and Initial Structure
- Create basic directory structure
- Set up Python environment  
- Initialize empty module files

### 2. Data Processing Components
- Implement file reading utilities
- Create section detection (CPU vs memory)
- Develop timestamp extraction
- Build line parsers for CPU and memory data

### 3. DataFrame Creation
- Convert parsed CPU data to DataFrame
- Convert parsed memory data to DataFrame
- Set proper indices and data types

### 4. Integration and CLI
- Connect parsers and DataFrame creators
- Implement command-line interface
- Add CSV output capabilities

### 5. Testing and Refinement
- Create comprehensive test suite
- Handle edge cases and errors
- Add documentation

## Iterative Implementation Steps

Now I'll break these down into smaller, testable steps:

1. **Project initialization**
2. **File reading utilities**
3. **Section header detection**
4. **Timestamp extraction**
5. **CPU line parsing**
6. **Memory line parsing**
7. **Complete file section parsing**
8. **DataFrame creation for CPU data**
9. **DataFrame creation for memory data**
10. **Full integration of parser and DataFrame creation**
11. **Command-line interface**
12. **CSV output functionality**
13. **Error handling and refinement**

## LLM Prompts for Test-Driven Implementation

### Prompt 1: Project Setup

```
I need to create a Python package called 'pidsis' that will parse pidstats log files into pandas DataFrames. Let's start by setting up the project structure.

Please create:
1. The necessary directory structure with __init__.py files
2. Empty skeleton files for parser.py, dataframe.py, utils.py, and main.py
3. A basic test directory with empty test files
4. A sample test for the project setup

Follow best practices for Python projects. The package should be importable as 'pidsis'.

Include a sample section from a pidstats log file that we can use for testing throughout the project. This should include both CPU and memory statistics sections.
```

### Prompt 2: File Reading Utilities

```
Now let's implement the file reading utilities for our pidsis package. 

In utils.py, create a function called `read_file_lines` that:
1. Takes a file path as input
2. Opens and reads the file line by line
3. Handles file not found and permission errors gracefully
4. Returns an iterator or generator of lines

Also, implement a basic utility function to check if a line is empty or a Linux system info line that should be skipped.

Write comprehensive unit tests for these functions in tests/test_utils.py including:
1. Test for reading a valid file
2. Test for handling a non-existent file
3. Test for identifying lines that should be skipped

Use the sample pidstats data we created earlier for testing.
```

### Prompt 3: Section Header Detection

```
Let's implement section header detection for our pidstats parser.

In parser.py, create functions that:
1. Detect if a line is a section header (contains 'UID', 'PID', etc.)
2. Determine if a header is for CPU statistics ('%usr' in header) or memory statistics ('minflt/s' in header)

Write tests in tests/test_parser.py that:
1. Test header detection with various input lines
2. Test section type identification (CPU vs memory)
3. Test handling of non-header lines

Make sure to include integration tests that use the sample data we created earlier.
```

### Prompt 4: Timestamp Extraction

```
Now let's implement timestamp extraction from section headers.

In parser.py, create a function called `extract_timestamp` that:
1. Takes a section header line as input
2. Extracts the timestamp component
3. Converts it to a Python datetime object
4. Handles various timestamp formats gracefully

Write tests in tests/test_parser.py that:
1. Test timestamp extraction from different header formats
2. Test conversion to datetime objects
3. Test error handling for malformed headers

Include integration tests that use real section headers from our sample data.
```

### Prompt 5: CPU Line Parsing

```
Let's implement CPU line parsing for our pidstats parser.

In parser.py, create a function called `parse_cpu_line` that:
1. Takes a CPU data line and its associated timestamp as input
2. Extracts all fields (UID, PID, %usr, %system, etc.)
3. Converts fields to appropriate data types (int for PID, float for percentages)
4. Returns a dictionary or named tuple with all data

Write tests in tests/test_parser.py that:
1. Test parsing of valid CPU data lines
2. Test data type conversions
3. Test handling of malformed lines
4. Test with real CPU data lines from our sample

Ensure the function properly validates and handles the data according to the spec.
```

### Prompt 6: Memory Line Parsing

```
Let's implement memory line parsing for our pidstats parser.

In parser.py, create a function called `parse_mem_line` that:
1. Takes a memory data line and its associated timestamp as input
2. Extracts all fields (UID, PID, minflt/s, majflt/s, etc.)
3. Converts fields to appropriate data types (int for PID, float for fault rates)
4. Returns a dictionary or named tuple with all data

Write tests in tests/test_parser.py that:
1. Test parsing of valid memory data lines
2. Test data type conversions
3. Test handling of malformed lines
4. Test with real memory data lines from our sample

Ensure the function properly validates and handles the data according to the spec.
```

### Prompt 7: Complete File Section Parsing

```
Let's implement complete section parsing for our pidstats parser.

In parser.py, create functions that:
1. Parse a complete CPU section (header + multiple data lines)
2. Parse a complete memory section (header + multiple data lines)
3. Associate all data lines with their section timestamp
4. Collect all entries from each section

Write tests in tests/test_parser.py that:
1. Test parsing complete CPU and memory sections
2. Test handling sections with multiple data lines
3. Test handling of malformed sections
4. Test with real sections from our sample data

Ensure the functions properly handle transitions between headers and data lines.
```

### Prompt 8: File Parsing Integration

```
Let's integrate section parsing into a complete file parser.

In parser.py, create a function called `parse_pidstats_file` that:
1. Takes a file path as input
2. Uses our file reading utility to read the file
3. Identifies and parses alternating CPU and memory sections
4. Collects all CPU and memory data entries
5. Returns two separate lists - one for CPU data and one for memory data

Write tests in tests/test_parser.py and tests/test_integration.py that:
1. Test parsing a complete file with multiple sections
2. Test handling of transitions between CPU and memory sections
3. Test with our complete sample data file

Ensure proper error handling and validation throughout the process.
```

### Prompt 9: CPU DataFrame Creation

```
Let's implement CPU DataFrame creation from our parsed data.

In dataframe.py, create a function called `create_cpu_dataframe` that:
1. Takes a list of CPU data entries as input
2. Converts the data to a pandas DataFrame
3. Sets a multi-index on [timestamp, PID]
4. Ensures proper column names as specified in the spec
5. Converts all data to appropriate types
6. Returns the properly formatted DataFrame

Write tests in tests/test_dataframe.py that:
1. Test DataFrame creation with sample CPU data
2. Test index and column creation
3. Test data type conversions
4. Test with real parsed CPU data

Include integration tests that connect parsing and DataFrame creation for CPU data.
```

### Prompt 10: Memory DataFrame Creation

```
Let's implement memory DataFrame creation from our parsed data.

In dataframe.py, create a function called `create_memory_dataframe` that:
1. Takes a list of memory data entries as input
2. Converts the data to a pandas DataFrame
3. Sets a multi-index on [timestamp, PID]
4. Ensures proper column names as specified in the spec
5. Converts all data to appropriate types
6. Returns the properly formatted DataFrame

Write tests in tests/test_dataframe.py that:
1. Test DataFrame creation with sample memory data
2. Test index and column creation
3. Test data type conversions
4. Test with real parsed memory data

Include integration tests that connect parsing and DataFrame creation for memory data.
```

### Prompt 11: Parser Integration

```
Let's create the main integrated parser function that combines all our components.

In dataframe.py, create a function called `create_dataframes` that:
1. Takes CPU and memory data lists as input
2. Uses our DataFrame creation functions to generate both DataFrames
3. Returns both DataFrames as a tuple

In parser.py (or a new module if preferred), create a main function called `parse_pidstats` that:
1. Takes a file path as input
2. Uses file parsing to extract CPU and memory data
3. Uses the DataFrame creation functions to generate both DataFrames
4. Returns both DataFrames as a tuple

Write comprehensive integration tests in tests/test_integration.py that:
1. Test the complete parsing process from file to DataFrames
2. Verify DataFrame structures match the specification
3. Test with our complete sample data file

Ensure the integration works smoothly and maintains all required functionality.
```

### Prompt 12: Command-Line Interface

```
Let's implement the command-line interface for our pidstats parser.

In main.py, create:
1. An argument parser using argparse that accepts:
   - Required file path to the pidstats log
   - Optional output directory for CSV files
   - Help documentation
2. A main function that:
   - Parses command-line arguments
   - Calls our parsing functions
   - Displays basic information about the parsed DataFrames
   - Handles output to CSV if requested
   - Provides appropriate error handling

Write tests in tests/test_main.py that:
1. Test argument parsing
2. Test main function execution
3. Test CSV output functionality
4. Test error handling

Ensure the CLI works according to the specification.
```

### Prompt 13: Final Integration and Error Handling

```
Let's finalize our pidstats parser with comprehensive error handling and documentation.

1. Review all functions and add robust error handling for:
   - Malformed log entries
   - Unexpected data types
   - Memory issues with large files
   - Other potential edge cases

2. Add detailed docstrings to all functions following PEP 257

3. Enhance the main.py script to provide useful feedback and error messages

4. Add any missing tests, particularly for edge cases and error conditions

5. Create a comprehensive end-to-end integration test that validates all functionality

Ensure the parser works reliably with various input formats and handles errors gracefully.
```

## Conclusion

This implementation plan provides a step-by-step approach to building the pidstats parser, broken down into manageable chunks. Each step builds incrementally on previous work, and testing is integrated throughout the development process. Following these prompts will help create a robust, well-tested parser that meets all the requirements in the specification.