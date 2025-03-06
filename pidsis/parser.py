"""Module for parsing pidstats log files"""

from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime
import re
from .utils import read_file_lines

# Global variable to store the current date context
_current_date = None

def set_current_date(date_str: str) -> None:
    """Set the current date context for timestamp parsing.
    
    Args:
        date_str: Date string in MM/DD/YYYY format
    """
    global _current_date
    try:
        _current_date = datetime.strptime(date_str.strip(), '%m/%d/%Y').date()
    except ValueError as e:
        raise ValueError(f"Invalid date format. Expected MM/DD/YYYY, got: {date_str}") from e

def extract_timestamp(line: str) -> datetime:
    """Extract and parse timestamp from a pidstats line.
    
    Args:
        line: Line containing a timestamp in "HH:MM:SS AM/PM" format
        
    Returns:
        datetime object representing the timestamp
        
    Raises:
        ValueError: If timestamp format is invalid
    """
    # Regular expression for "HH:MM:SS AM/PM" format
    time_pattern = r'^(\d{2}):(\d{2}):(\d{2})\s+(AM|PM)'
    match = re.match(time_pattern, line.strip())
    
    if not match:
        raise ValueError(f"Invalid timestamp format in line: {line}")
    
    hour = int(match.group(1))
    minute = int(match.group(2))
    second = int(match.group(3))
    meridiem = match.group(4)
    
    # Validate time components
    if minute >= 60 or second >= 60:
        raise ValueError(f"Invalid time components in: {line}")
        
    # Convert to 24-hour format
    if meridiem == 'PM' and hour < 12:
        hour += 12
    elif meridiem == 'AM' and hour == 12:
        hour = 0
        
    if hour >= 24:
        raise ValueError(f"Invalid hour in: {line}")
    
    # If we have a date context, use it
    if _current_date:
        return datetime.combine(_current_date, datetime.min.time().replace(
            hour=hour, minute=minute, second=second
        ))
    
    # Otherwise return just the time portion
    return datetime.min.replace(hour=hour, minute=minute, second=second)

def is_header_line(line: str) -> bool:
    """Check if a line is a section header.
    
    Args:
        line: Line to check
        
    Returns:
        True if the line contains standard pidstats header columns
    """
    required_columns = ['UID', 'PID', 'Command']
    return all(col in line for col in required_columns)

def get_section_type(header_line: str) -> Optional[str]:
    """Determine the type of statistics section from a header line.
    
    Args:
        header_line: A header line from the pidstats log
        
    Returns:
        'cpu' for CPU statistics section
        'memory' for memory statistics section
        None if not a recognized section header
    """
    if not is_header_line(header_line):
        return None
        
    if '%usr' in header_line and '%CPU' in header_line:
        return 'cpu'
    elif 'minflt/s' in header_line and '%MEM' in header_line:
        return 'memory'
    return None

def parse_cpu_line(line: str, timestamp: str) -> Dict[str, Any]:
    """Parse a CPU statistics line.
    
    Args:
        line: A line from the CPU statistics section
        timestamp: Associated timestamp for the line
        
    Returns:
        Dictionary containing parsed CPU statistics
    
    Raises:
        ValueError: If line format is invalid or contains invalid numeric values
        IndexError: If line has insufficient fields
    """
    try:
        parts = line.split()
        if len(parts) < 11:  # Minimum required fields: timestamp(2) + uid + pid + 6 stats + command
            raise IndexError(f"Insufficient fields in CPU line: {line}")
            
        # Extract and validate numeric values
        uid = int(parts[2])
        pid = int(parts[3])
        if uid < 0 or pid < 0:
            raise ValueError(f"Invalid UID or PID (must be non-negative): {line}")
            
        # Extract and validate percentage values
        usr = float(parts[4])
        system = float(parts[5])
        guest = float(parts[6])
        wait = float(parts[7])
        cpu = float(parts[8])
        cpu_id = int(parts[9])
        
        # Validate percentage ranges
        for name, value in [('usr', usr), ('system', system), ('guest', guest), 
                          ('wait', wait), ('cpu', cpu)]:
            if not (0 <= value <= 100):
                raise ValueError(f"Invalid percentage for {name}: {value}")
                
        # Reconstruct command (might contain spaces)
        command = ' '.join(parts[10:])
        if not command:
            raise ValueError("Missing command field")
            
        return {
            'timestamp': timestamp,
            'uid': uid,
            'pid': pid,
            'usr': usr,
            'system': system,
            'guest': guest,
            'wait': wait,
            'cpu': cpu,
            'cpu_id': cpu_id,
            'command': command
        }
        
    except (IndexError, ValueError) as e:
        raise type(e)(f"Error parsing CPU line '{line}': {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error parsing CPU line '{line}': {str(e)}")

def parse_memory_line(line: str, timestamp: str) -> Dict[str, Any]:
    """Parse a memory statistics line.
    
    Args:
        line: A line from the memory statistics section
        timestamp: Associated timestamp for the line
        
    Returns:
        Dictionary containing parsed memory statistics
        
    Raises:
        ValueError: If line format is invalid or contains invalid numeric values
        IndexError: If line has insufficient fields
    """
    try:
        parts = line.split()
        if len(parts) < 10:  # Minimum required fields: timestamp(2) + uid + pid + 4 stats + mem_pct + command
            raise IndexError(f"Insufficient fields in memory line: {line}")
            
        # Extract and validate numeric values
        uid = int(parts[2])
        pid = int(parts[3])
        if uid < 0 or pid < 0:
            raise ValueError(f"Invalid UID or PID (must be non-negative): {line}")
            
        # Extract and validate memory statistics
        minflt = float(parts[4])
        majflt = float(parts[5])
        vsz = int(parts[6])
        rss = int(parts[7])
        mem_percent = float(parts[8])
        
        # Validate memory values
        if vsz < 0 or rss < 0:
            raise ValueError(f"Invalid memory value (must be non-negative): {line}")
            
        # Validate memory percentage
        if not (0 <= mem_percent <= 100):
            raise ValueError(f"Invalid percentage for memory: {mem_percent}")
            
        # Reconstruct command (might contain spaces)
        command = ' '.join(parts[9:])
        if not command:
            raise ValueError("Missing command field")
            
        return {
            'timestamp': timestamp,
            'uid': uid,
            'pid': pid,
            'minflt': minflt,
            'majflt': majflt,
            'vsz': vsz,
            'rss': rss,
            'mem_percent': mem_percent,
            'command': command
        }
        
    except (IndexError, ValueError) as e:
        raise type(e)(f"Error parsing memory line '{line}': {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error parsing memory line '{line}': {str(e)}")

def parse_cpu_section(lines: List[str]) -> Tuple[datetime, List[Dict[str, Any]]]:
    """Parse a complete CPU statistics section.
    
    Args:
        lines: Lines from a CPU section including header and data lines
        
    Returns:
        Tuple of (section_timestamp, list of parsed CPU entries)
        
    Raises:
        ValueError: If section format is invalid or missing header
    """
    if not lines:
        raise ValueError("Empty CPU section")
        
    header = lines[0]
    if not is_header_line(header) or get_section_type(header) != 'cpu':
        raise ValueError("Invalid CPU section header")
        
    section_timestamp = extract_timestamp(header)
    entries = []
    
    for line in lines[1:]:  # Skip header line
        try:
            entry = parse_cpu_line(line, str(section_timestamp))
            entries.append(entry)
        except (ValueError, IndexError) as e:
            # Log error but continue processing other lines
            continue
            
    return section_timestamp, entries

def parse_memory_section(lines: List[str]) -> Tuple[datetime, List[Dict[str, Any]]]:
    """Parse a complete memory statistics section.
    
    Args:
        lines: Lines from a memory section including header and data lines
        
    Returns:
        Tuple of (section_timestamp, list of parsed memory entries)
        
    Raises:
        ValueError: If section format is invalid or missing header
    """
    if not lines:
        raise ValueError("Empty memory section")
        
    header = lines[0]
    if not is_header_line(header) or get_section_type(header) != 'memory':
        raise ValueError("Invalid memory section header")
        
    section_timestamp = extract_timestamp(header)
    entries = []
    
    for line in lines[1:]:  # Skip header line
        try:
            entry = parse_memory_line(line, str(section_timestamp))
            entries.append(entry)
        except (ValueError, IndexError) as e:
            # Log error but continue processing other lines
            continue
            
    return section_timestamp, entries

def parse_sections(lines: List[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Parse all sections from a list of pidstats lines.
    
    Args:
        lines: All lines from a pidstats log file
        
    Returns:
        Tuple of (cpu_entries, memory_entries) containing parsed data
    """
    cpu_entries = []
    memory_entries = []
    current_section_lines = []
    current_section_type = None
    
    for line in lines:
        if is_header_line(line):
            # Process previous section if it exists
            if current_section_lines and current_section_type:
                try:
                    if current_section_type == 'cpu':
                        _, entries = parse_cpu_section(current_section_lines)
                        cpu_entries.extend(entries)
                    elif current_section_type == 'memory':
                        _, entries = parse_memory_section(current_section_lines)
                        memory_entries.extend(entries)
                except ValueError:
                    pass  # Skip malformed sections
                    
            # Start new section
            current_section_type = get_section_type(line)
            current_section_lines = [line]
        elif current_section_type:
            # Add line to current section
            current_section_lines.append(line)
    
    # Process final section
    if current_section_lines and current_section_type:
        try:
            if current_section_type == 'cpu':
                _, entries = parse_cpu_section(current_section_lines)
                cpu_entries.extend(entries)
            elif current_section_type == 'memory':
                _, entries = parse_memory_section(current_section_lines)
                memory_entries.extend(entries)
        except ValueError:
            pass
            
    return cpu_entries, memory_entries

# Update parse_pidstats_file to use the new section parsing
def parse_pidstats_file(file_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Parse a pidstats log file into separate CPU and memory statistics.
    
    Args:
        file_path: Path to the pidstats log file
        
    Returns:
        Tuple containing two lists of dictionaries:
        - CPU statistics entries
        - Memory statistics entries
    """
    lines = list(read_file_lines(file_path))
    return parse_sections(lines)