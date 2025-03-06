"""Tests for pidstats parser"""

import pytest
from datetime import datetime
from pathlib import Path
from pidsis import parser, utils

SAMPLE_CPU_SECTION = '''09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
09:56:46 PM     0       497    0.02    0.02    0.00    0.02    0.03     0  systemd-journal
09:56:46 PM   993       670    0.17    0.02    0.00    0.00    0.18     0  prometheus
09:56:46 PM   992       676    0.07    0.03    0.00    0.00    0.10     0  node_exporter'''

SAMPLE_MEMORY_SECTION = '''09:55:46 PM   UID       PID  minflt/s  majflt/s     VSZ     RSS   %MEM  Command
09:56:46 PM     0       497      0.17      0.00  129300    7036   0.89  systemd-journal
09:56:46 PM   993       670      0.05      0.00 2124408   67916   8.61  prometheus
09:56:46 PM   992       676      0.00      0.02 1241952   16172   2.05  node_exporter'''

def test_linux_header():
    """Test detection of Linux system info header"""
    header = "Linux 4.18.0-553.16.1.el8_10.x86_64 (host) 03/02/2025 _x86_64_ (1 CPU)"
    assert utils.is_linux_header(header)
    assert not utils.is_linux_header(SAMPLE_CPU_SECTION)

def test_column_header():
    """Test column header detection and validation"""
    # Test CPU header columns
    cpu_header = "09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command"
    assert parser.is_header_line(cpu_header)
    assert parser.get_section_type(cpu_header) == 'cpu'
    
    # Verify all required CPU columns are present
    cpu_columns = ['UID', 'PID', '%usr', '%system', '%CPU', 'Command']
    for column in cpu_columns:
        assert column in cpu_header
    
    # Test memory header columns
    mem_header = "09:55:46 PM   UID       PID  minflt/s  majflt/s     VSZ     RSS   %MEM  Command"
    assert parser.is_header_line(mem_header)
    assert parser.get_section_type(mem_header) == 'memory'
    
    # Verify all required memory columns are present
    mem_columns = ['UID', 'PID', 'VSZ', 'RSS', '%MEM', 'Command']
    for column in mem_columns:
        assert column in mem_header
    
    # Test malformed headers
    malformed_headers = [
        # Missing Command column
        "09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU",
        # Missing PID column
        "09:55:46 PM   UID           %usr %system  %guest   %wait    %CPU   CPU  Command",
        # Empty string
        "",
        # Random text
        "This is not a header line"
    ]
    for header in malformed_headers:
        assert not parser.is_header_line(header)
        assert parser.get_section_type(header) is None

def test_parse_line_complete():
    """Test parsing of complete data lines"""
    # Test CPU line parsing
    cpu_line = "09:56:46 PM   993       670    0.17    0.02    0.00    0.00    0.18     0  prometheus"
    timestamp = "09:56:46 PM"
    
    cpu_data = parser.parse_cpu_line(cpu_line, timestamp)
    assert isinstance(cpu_data, dict)
    assert cpu_data['timestamp'] == timestamp
    assert cpu_data['uid'] == 993
    assert cpu_data['pid'] == 670
    assert cpu_data['usr'] == 0.17
    assert cpu_data['system'] == 0.02
    assert cpu_data['guest'] == 0.0
    assert cpu_data['wait'] == 0.0
    assert cpu_data['cpu'] == 0.18
    assert cpu_data['cpu_id'] == 0
    assert cpu_data['command'] == 'prometheus'
    
    # Test memory line parsing
    mem_line = "09:56:46 PM   993       670      0.05      0.00 2124408   67916   8.61  prometheus"
    mem_data = parser.parse_memory_line(mem_line, timestamp)
    assert isinstance(mem_data, dict)
    assert mem_data['timestamp'] == timestamp
    assert mem_data['uid'] == 993
    assert mem_data['pid'] == 670
    assert mem_data['minflt'] == 0.05
    assert mem_data['majflt'] == 0.0
    assert mem_data['vsz'] == 2124408
    assert mem_data['rss'] == 67916
    assert mem_data['mem_percent'] == 8.61
    assert mem_data['command'] == 'prometheus'

def test_is_header_line():
    """Test header line detection"""
    # Test valid headers
    cpu_header = "09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command"
    mem_header = "09:55:46 PM   UID       PID  minflt/s  majflt/s     VSZ     RSS   %MEM  Command"
    assert parser.is_header_line(cpu_header)
    assert parser.is_header_line(mem_header)
    
    # Test non-header lines
    data_line = "09:56:46 PM     0       497    0.02    0.02    0.00    0.02    0.03     0  systemd-journal"
    empty_line = ""
    linux_header = "Linux 4.18.0-553.16.1.el8_10.x86_64 (host) 03/02/2025"
    assert not parser.is_header_line(data_line)
    assert not parser.is_header_line(empty_line)
    assert not parser.is_header_line(linux_header)

def test_get_section_type():
    """Test section type identification"""
    # Test CPU header
    cpu_header = "09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command"
    assert parser.get_section_type(cpu_header) == 'cpu'
    
    # Test memory header
    mem_header = "09:55:46 PM   UID       PID  minflt/s  majflt/s     VSZ     RSS   %MEM  Command"
    assert parser.get_section_type(mem_header) == 'memory'
    
    # Test invalid headers
    invalid_header = "09:55:46 PM   UID       PID    other columns    Command"
    assert parser.get_section_type(invalid_header) is None
    
    # Test non-header lines
    data_line = "09:56:46 PM     0       497    0.02    0.02    0.00    0.02    0.03     0  systemd-journal"
    assert parser.get_section_type(data_line) is None

def test_section_detection_with_sample_data():
    """Test section detection with actual sample data"""
    sample_path = Path(__file__).parent / "data" / "sample.log"
    section_types = []
    
    for line in utils.read_file_lines(str(sample_path)):
        if parser.is_header_line(line):
            section_type = parser.get_section_type(line)
            if section_type:
                section_types.append(section_type)
    
    # Verify we found both CPU and memory sections
    assert 'cpu' in section_types
    assert 'memory' in section_types
    # Verify correct order: CPU section comes before memory section
    assert section_types.index('cpu') < section_types.index('memory')

def test_extract_timestamp():
    """Test timestamp extraction from different formats"""
    # Test 12-hour format with AM/PM
    header = "09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command"
    dt = parser.extract_timestamp(header)
    assert isinstance(dt, datetime)
    assert dt.hour == 21  # 9 PM = 21:00
    assert dt.minute == 55
    assert dt.second == 46

    # Test AM time
    header_am = "10:30:15 AM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command"
    dt_am = parser.extract_timestamp(header_am)
    assert dt_am.hour == 10
    assert dt_am.minute == 30
    assert dt_am.second == 15

    # Test midnight (12 AM)
    header_midnight = "12:00:00 AM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command"
    dt_midnight = parser.extract_timestamp(header_midnight)
    assert dt_midnight.hour == 0
    assert dt_midnight.minute == 0
    assert dt_midnight.second == 0

    # Test noon (12 PM)
    header_noon = "12:00:00 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command"
    dt_noon = parser.extract_timestamp(header_noon)
    assert dt_noon.hour == 12
    assert dt_noon.minute == 0
    assert dt_noon.second == 0

def test_extract_timestamp_with_date():
    """Test timestamp extraction when date is available"""
    # First line of pidstats typically contains the date
    linux_header = "Linux 4.18.0-553.16.1.el8_10.x86_64 (host) 03/02/2025 _x86_64_ (1 CPU)"
    parser.set_current_date("03/02/2025")  # Set the date context

    header = "09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command"
    dt = parser.extract_timestamp(header)
    assert isinstance(dt, datetime)
    assert dt.year == 2025
    assert dt.month == 3
    assert dt.day == 2
    assert dt.hour == 21
    assert dt.minute == 55
    assert dt.second == 46

def test_timestamp_error_handling():
    """Test error handling for malformed timestamps"""
    invalid_headers = [
        "",  # Empty string
        "Invalid header",  # No timestamp
        "25:00:00 PM   UID   PID",  # Invalid hour
        "10:60:00 AM   UID   PID",  # Invalid minute
        "10:00:60 AM   UID   PID",  # Invalid second
        "10:00:00 ZZ   UID   PID",  # Invalid AM/PM
    ]

    for header in invalid_headers:
        with pytest.raises(ValueError):
            parser.extract_timestamp(header)

def test_timestamp_from_sample_data():
    """Test timestamp extraction with real data from sample file"""
    sample_path = Path(__file__).parent / "data" / "sample.log"
    
    headers = []
    for line in utils.read_file_lines(str(sample_path)):
        if parser.is_header_line(line):
            headers.append(line)
    
    # Test timestamps from actual headers
    for header in headers:
        dt = parser.extract_timestamp(header)
        assert isinstance(dt, datetime)
        assert dt.hour in (21, 22)  # 9 PM or 10 PM
        assert dt.minute in range(60)
        assert dt.second in range(60)

def test_parse_cpu_line_validation():
    """Test validation in CPU line parsing"""
    timestamp = "09:56:46 PM"
    
    # Test invalid percentage values
    invalid_percentages = [
        "09:56:46 PM   993       670    101.0    0.02    0.00    0.00    0.18     0  prometheus",  # usr > 100
        "09:56:46 PM   993       670    0.17    -0.02    0.00    0.00    0.18     0  prometheus",  # negative system
        "09:56:46 PM   993       670    0.17    0.02    0.00    0.00    150.0     0  prometheus",  # cpu > 100
    ]
    for line in invalid_percentages:
        with pytest.raises(ValueError, match="Invalid percentage"):
            parser.parse_cpu_line(line, timestamp)
            
    # Test invalid UIDs and PIDs
    invalid_ids = [
        "09:56:46 PM   -1        670    0.17    0.02    0.00    0.00    0.18     0  prometheus",  # negative UID
        "09:56:46 PM   993       -2     0.17    0.02    0.00    0.00    0.18     0  prometheus",  # negative PID
    ]
    for line in invalid_ids:
        with pytest.raises(ValueError, match="Invalid UID or PID"):
            parser.parse_cpu_line(line, timestamp)
            
    # Test insufficient fields
    insufficient = [
        "09:56:46 PM   993",  # too few fields
        "09:56:46 PM   993       670    0.17    0.02    0.00    0.00    0.18",  # missing command
    ]
    for line in insufficient:
        with pytest.raises(IndexError, match="Insufficient fields"):
            parser.parse_cpu_line(line, timestamp)

def test_parse_cpu_line_command_handling():
    """Test parsing of CPU lines with various command formats"""
    timestamp = "09:56:46 PM"
    
    # Test multi-word command
    line = "09:56:46 PM   993       670    0.17    0.02    0.00    0.00    0.18     0  java -jar app.jar"
    data = parser.parse_cpu_line(line, timestamp)
    assert data['command'] == "java -jar app.jar"
    
    # Test command with special characters
    line = "09:56:46 PM   993       670    0.17    0.02    0.00    0.00    0.18     0  /usr/bin/python3 --version"
    data = parser.parse_cpu_line(line, timestamp)
    assert data['command'] == "/usr/bin/python3 --version"

def test_parse_cpu_line_numeric_conversions():
    """Test numeric value conversions in CPU line parsing"""
    timestamp = "09:56:46 PM"
    line = "09:56:46 PM   993       670    0.17    0.02    0.00    0.00    0.18     0  prometheus"
    data = parser.parse_cpu_line(line, timestamp)
    
    # Check numeric type conversions
    assert isinstance(data['uid'], int)
    assert isinstance(data['pid'], int)
    assert isinstance(data['usr'], float)
    assert isinstance(data['system'], float)
    assert isinstance(data['guest'], float)
    assert isinstance(data['wait'], float)
    assert isinstance(data['cpu'], float)
    assert isinstance(data['cpu_id'], int)
    
    # Check exact values
    assert data['uid'] == 993
    assert data['pid'] == 670
    assert data['usr'] == 0.17
    assert data['system'] == 0.02
    assert data['guest'] == 0.0
    assert data['wait'] == 0.0
    assert data['cpu'] == 0.18
    assert data['cpu_id'] == 0

def test_parse_cpu_line_real_data():
    """Test CPU line parsing with real data from sample file"""
    sample_path = Path(__file__).parent / "data" / "sample.log"
    
    timestamp = "09:56:46 PM"
    test_lines = []
    in_cpu_section = False
    
    # Extract real CPU data lines from sample file
    for line in utils.read_file_lines(str(sample_path)):
        if parser.is_header_line(line):
            in_cpu_section = parser.get_section_type(line) == 'cpu'
            continue
        if in_cpu_section:
            test_lines.append(line)
    
    # Test parsing of real data lines
    for line in test_lines:
        data = parser.parse_cpu_line(line, timestamp)
        assert isinstance(data, dict)
        assert all(key in data for key in ['timestamp', 'uid', 'pid', 'usr', 'system', 
                                         'guest', 'wait', 'cpu', 'cpu_id', 'command'])
        assert data['timestamp'] == timestamp
        assert 0 <= data['cpu'] <= 100  # Validate CPU percentage range

def test_parse_memory_line_validation():
    """Test validation in memory line parsing"""
    timestamp = "09:56:46 PM"
    
    # Test invalid percentage values
    invalid_percentages = [
        "09:56:46 PM   993       670      0.05      0.00 2124408   67916   101.0  prometheus",  # mem > 100
        "09:56:46 PM   993       670      0.05      0.00 2124408   67916   -1.0  prometheus",  # negative mem
    ]
    for line in invalid_percentages:
        with pytest.raises(ValueError, match="Invalid percentage"):
            parser.parse_memory_line(line, timestamp)
            
    # Test invalid UIDs and PIDs
    invalid_ids = [
        "09:56:46 PM   -1        670      0.05      0.00 2124408   67916   8.61  prometheus",  # negative UID
        "09:56:46 PM   993       -2       0.05      0.00 2124408   67916   8.61  prometheus",  # negative PID
    ]
    for line in invalid_ids:
        with pytest.raises(ValueError, match="Invalid UID or PID"):
            parser.parse_memory_line(line, timestamp)
            
    # Test invalid memory values
    invalid_memory = [
        "09:56:46 PM   993       670      0.05      0.00    -100   67916   8.61  prometheus",  # negative VSZ
        "09:56:46 PM   993       670      0.05      0.00  2124408     -1   8.61  prometheus",  # negative RSS
    ]
    for line in invalid_memory:
        with pytest.raises(ValueError, match="Invalid memory value"):
            parser.parse_memory_line(line, timestamp)
            
    # Test insufficient fields
    insufficient = [
        "09:56:46 PM   993",  # too few fields
        "09:56:46 PM   993       670      0.05      0.00 2124408   67916   8.61",  # missing command
    ]
    for line in insufficient:
        with pytest.raises(IndexError, match="Insufficient fields"):
            parser.parse_memory_line(line, timestamp)

def test_parse_memory_line_command_handling():
    """Test parsing of memory lines with various command formats"""
    timestamp = "09:56:46 PM"
    
    # Test multi-word command
    line = "09:56:46 PM   993       670      0.05      0.00 2124408   67916   8.61  java -jar app.jar"
    data = parser.parse_memory_line(line, timestamp)
    assert data['command'] == "java -jar app.jar"
    
    # Test command with special characters
    line = "09:56:46 PM   993       670      0.05      0.00 2124408   67916   8.61  /usr/bin/python3 --version"
    data = parser.parse_memory_line(line, timestamp)
    assert data['command'] == "/usr/bin/python3 --version"

def test_parse_memory_line_numeric_conversions():
    """Test numeric value conversions in memory line parsing"""
    timestamp = "09:56:46 PM"
    line = "09:56:46 PM   993       670      0.05      0.00 2124408   67916   8.61  prometheus"
    data = parser.parse_memory_line(line, timestamp)
    
    # Check numeric type conversions
    assert isinstance(data['uid'], int)
    assert isinstance(data['pid'], int)
    assert isinstance(data['minflt'], float)
    assert isinstance(data['majflt'], float)
    assert isinstance(data['vsz'], int)
    assert isinstance(data['rss'], int)
    assert isinstance(data['mem_percent'], float)
    
    # Check exact values
    assert data['uid'] == 993
    assert data['pid'] == 670
    assert data['minflt'] == 0.05
    assert data['majflt'] == 0.0
    assert data['vsz'] == 2124408
    assert data['rss'] == 67916
    assert data['mem_percent'] == 8.61

def test_parse_memory_line_real_data():
    """Test memory line parsing with real data from sample file"""
    sample_path = Path(__file__).parent / "data" / "sample.log"
    
    timestamp = "09:56:46 PM"
    test_lines = []
    in_memory_section = False
    
    # Extract real memory data lines from sample file
    for line in utils.read_file_lines(str(sample_path)):
        if parser.is_header_line(line):
            in_memory_section = parser.get_section_type(line) == 'memory'
            continue
        if in_memory_section:
            test_lines.append(line)
    
    # Test parsing of real data lines
    for line in test_lines:
        data = parser.parse_memory_line(line, timestamp)
        assert isinstance(data, dict)
        assert all(key in data for key in ['timestamp', 'uid', 'pid', 'minflt', 'majflt', 
                                         'vsz', 'rss', 'mem_percent', 'command'])
        assert data['timestamp'] == timestamp
        assert 0 <= data['mem_percent'] <= 100  # Validate memory percentage range
        assert data['vsz'] >= 0  # Validate non-negative memory values
        assert data['rss'] >= 0

def test_parse_cpu_section():
    """Test parsing of complete CPU sections"""
    # Test valid CPU section
    cpu_lines = SAMPLE_CPU_SECTION.split('\n')
    timestamp, entries = parser.parse_cpu_section(cpu_lines)
    
    assert isinstance(timestamp, datetime)
    assert len(entries) == 3
    
    # Verify first entry
    assert entries[0]['uid'] == 0
    assert entries[0]['pid'] == 497
    assert entries[0]['command'] == 'systemd-journal'
    
    # Verify prometheus entry
    prometheus_entry = next(entry for entry in entries if entry['command'] == 'prometheus')
    assert prometheus_entry['usr'] == 0.17
    assert prometheus_entry['cpu'] == 0.18
    
    # Test invalid sections
    invalid_sections = [
        [],  # Empty section
        ["Not a header line"],  # Missing header
        ["09:55:46 PM   UID       PID  minflt/s  majflt/s     VSZ     RSS   %MEM  Command"],  # Wrong section type
    ]
    for section in invalid_sections:
        with pytest.raises(ValueError):
            parser.parse_cpu_section(section)

def test_parse_memory_section():
    """Test parsing of complete memory sections"""
    # Test valid memory section
    memory_lines = SAMPLE_MEMORY_SECTION.split('\n')
    timestamp, entries = parser.parse_memory_section(memory_lines)
    
    assert isinstance(timestamp, datetime)
    assert len(entries) == 3
    
    # Verify first entry
    assert entries[0]['uid'] == 0
    assert entries[0]['pid'] == 497
    assert entries[0]['command'] == 'systemd-journal'
    
    # Verify prometheus entry
    prometheus_entry = next(entry for entry in entries if entry['command'] == 'prometheus')
    assert prometheus_entry['vsz'] == 2124408
    assert prometheus_entry['rss'] == 67916
    assert prometheus_entry['mem_percent'] == 8.61
    
    # Test invalid sections
    invalid_sections = [
        [],  # Empty section
        ["Not a header line"],  # Missing header
        ["09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command"],  # Wrong section type
    ]
    for section in invalid_sections:
        with pytest.raises(ValueError):
            parser.parse_memory_section(section)

def test_section_transitions():
    """Test handling of transitions between sections"""
    # Create test data with multiple sections
    test_data = f"{SAMPLE_CPU_SECTION}\n{SAMPLE_MEMORY_SECTION}"
    lines = test_data.split('\n')
    
    cpu_entries, memory_entries = parser.parse_sections(lines)
    
    # Verify section parsing
    assert len(cpu_entries) == 3
    assert len(memory_entries) == 3
    
    # Verify section order preserved
    assert all('usr' in entry for entry in cpu_entries)
    assert all('vsz' in entry for entry in memory_entries)
    
    # Verify timestamps consistent within sections
    cpu_timestamps = {entry['timestamp'] for entry in cpu_entries}
    mem_timestamps = {entry['timestamp'] for entry in memory_entries}
    assert len(cpu_timestamps) == 1  # All entries in a section share timestamp
    assert len(mem_timestamps) == 1

def test_malformed_sections():
    """Test handling of malformed sections"""
    # Create test data with malformed sections
    malformed_data = '''09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
09:56:46 PM   993   invalid_line
09:56:46 PM   993       670    0.17    0.02    0.00    0.00    0.18     0  prometheus
09:55:46 PM   UID       PID  minflt/s  majflt/s     VSZ     RSS   %MEM  Command
09:56:46 PM   993   another_invalid
09:56:46 PM   993       670      0.05      0.00 2124408   67916   8.61  prometheus'''
    
    lines = malformed_data.split('\n')
    cpu_entries, memory_entries = parser.parse_sections(lines)
    
    # Verify valid entries were parsed despite malformed lines
    assert len(cpu_entries) == 1
    assert len(memory_entries) == 1
    assert cpu_entries[0]['command'] == 'prometheus'
    assert memory_entries[0]['command'] == 'prometheus'

def test_parse_real_sections():
    """Test section parsing with real data from sample file"""
    sample_path = Path(__file__).parent / "data" / "sample.log"
    lines = list(utils.read_file_lines(str(sample_path)))
    
    cpu_entries, memory_entries = parser.parse_sections(lines)
    
    # Verify basic parsing succeeded
    assert len(cpu_entries) > 0
    assert len(memory_entries) > 0
    
    # Verify data integrity
    for entry in cpu_entries:
        assert isinstance(entry['timestamp'], str)
        assert isinstance(entry['pid'], int)
        assert isinstance(entry['cpu'], float)
        assert 0 <= entry['cpu'] <= 100
        
    for entry in memory_entries:
        assert isinstance(entry['timestamp'], str)
        assert isinstance(entry['pid'], int)
        assert isinstance(entry['vsz'], int)
        assert isinstance(entry['rss'], int)
        assert 0 <= entry['mem_percent'] <= 100

def test_parse_complete_file():
    """Test parsing a complete pidstats file with multiple sections"""
    # Create test data with multiple alternating sections
    test_data = f"{SAMPLE_CPU_SECTION}\n{SAMPLE_MEMORY_SECTION}\n{SAMPLE_CPU_SECTION}"
    test_file = Path(__file__).parent / "data" / "test_complete.log"
    test_file.write_text(test_data)
    
    cpu_entries, memory_entries = parser.parse_pidstats_file(str(test_file))
    
    # Verify number of entries (2 CPU sections, 1 memory section)
    assert len(cpu_entries) == 6  # 2 sections × 3 entries each
    assert len(memory_entries) == 3  # 1 section × 3 entries
    
    # Verify section data integrity
    assert all('cpu' in entry for entry in cpu_entries)
    assert all('vsz' in entry for entry in memory_entries)

def test_parse_file_empty_sections():
    """Test parsing files with empty sections"""
    # Create test data with empty sections
    test_data = '''09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
09:55:46 PM   UID       PID  minflt/s  majflt/s     VSZ     RSS   %MEM  Command
09:56:46 PM   993       670      0.05      0.00 2124408   67916   8.61  prometheus
09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
09:56:46 PM   993       670    0.17    0.02    0.00    0.00    0.18     0  prometheus'''
    
    test_file = Path(__file__).parent / "data" / "test_empty_sections.log"
    test_file.write_text(test_data)
    
    cpu_entries, memory_entries = parser.parse_pidstats_file(str(test_file))
    
    # Verify that empty sections are handled properly
    assert len(cpu_entries) == 1  # Only one valid CPU entry
    assert len(memory_entries) == 1  # Only one valid memory entry

def test_parse_file_mixed_content():
    """Test parsing files with mixed valid and invalid content"""
    # Create test data with mixed content
    test_data = '''Some random text
09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
09:56:46 PM   993       670    0.17    0.02    0.00    0.00    0.18     0  prometheus
Invalid line in the middle
09:55:46 PM   UID       PID  minflt/s  majflt/s     VSZ     RSS   %MEM  Command
09:56:46 PM   993       670      0.05      0.00 2124408   67916   8.61  prometheus
More invalid content'''
    
    test_file = Path(__file__).parent / "data" / "test_mixed.log"
    test_file.write_text(test_data)
    
    cpu_entries, memory_entries = parser.parse_pidstats_file(str(test_file))
    
    # Verify that valid entries were parsed despite invalid content
    assert len(cpu_entries) == 1
    assert len(memory_entries) == 1
    assert cpu_entries[0]['command'] == 'prometheus'
    assert memory_entries[0]['command'] == 'prometheus'

def test_parse_file_with_date():
    """Test parsing file with system date information"""
    # Create test data with system info line
    test_data = '''Linux 4.18.0-553.16.1.el8_10.x86_64 (host) 03/02/2025 _x86_64_ (1 CPU)

09:55:46 PM   UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
09:56:46 PM   993       670    0.17    0.02    0.00    0.00    0.18     0  prometheus

09:55:46 PM   UID       PID  minflt/s  majflt/s     VSZ     RSS   %MEM  Command
09:56:46 PM   993       670      0.05      0.00 2124408   67916   8.61  prometheus'''
    
    test_file = Path(__file__).parent / "data" / "test_with_date.log"
    test_file.write_text(test_data)
    
    # Parse file and verify date handling
    cpu_entries, memory_entries = parser.parse_pidstats_file(str(test_file))
    
    assert len(cpu_entries) == 1
    assert len(memory_entries) == 1
    # Verify date was properly extracted and applied to timestamps