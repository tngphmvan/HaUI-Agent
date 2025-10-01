# Course Scheduler MCP Server

This MCP (Model Context Protocol) server exposes the Optimized Course Scheduling Suggestion System as a set of tools that can be used by AI assistants and other MCP clients.

## Features

The server provides the following tools:

### 1. **initialize_scheduler**

Initialize the course scheduler with curriculum data files.

- **Required before using other tools**
- Parameters:
  - `curriculum_file`: Path to curriculum JSON file
  - `processed_file`: Path to processed curriculum JSON file

### 2. **suggest_courses**

Generate optimized course enrollment suggestions.

- Parameters:
  - `priority_courses`: Courses student wants to take (optional)
  - `non_priority_courses`: Courses student wants to avoid (optional)
  - `max_credits`: Maximum credits to enroll (default: 20)
  - `completed_courses`: List of completed course codes
  - `current_semester`: Current semester number (1-8)

### 3. **validate_prerequisites**

Check if prerequisites are met for a specific course.

- Parameters:
  - `course_code`: Course code to validate
  - `completed_courses`: List of completed courses

### 4. **get_course_info**

Get detailed information about a course.

- Parameters:
  - `course_identifier`: Course code or name

### 5. **search_courses**

Search for courses by name or code.

- Parameters:
  - `query`: Search query
  - `max_results`: Maximum results to return (default: 10)

### 6. **get_semester_courses**

Get all courses for a specific semester.

- Parameters:
  - `semester`: Semester number (1-8)
  - `include_electives`: Include elective courses (default: true)

### 7. **calculate_remaining_credits**

Calculate remaining credits needed for graduation.

- Parameters:
  - `completed_courses`: List of completed course codes

### 8. **format_suggestions**

Format course suggestions into human-readable text.

- Parameters:
  - `suggestions_json`: JSON string from suggest_courses result

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Ensure the parent directory contains `course_scheduler.py` and curriculum data files.

## Configuration

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "course-scheduler": {
      "command": "python",
      "args": ["-u", "e:\\HaUI_Agent\\mcp_course_scheduler\\server.py"],
      "env": {
        "PYTHONPATH": "e:\\HaUI_Agent"
      }
    }
  }
}
```

## Usage Example

1. **Initialize the scheduler:**

```json
{
  "curriculum_file": "e:\\HaUI_Agent\\khung ctrinh cntt.json",
  "processed_file": "e:\\HaUI_Agent\\sample.json"
}
```

2. **Get course suggestions:**

```json
{
  "priority_courses": ["Cấu trúc dữ liệu và giải thuật"],
  "non_priority_courses": ["Thiết kế đồ hoạ 2D"],
  "max_credits": 18,
  "completed_courses": ["BS6001", "BS6002", "IT6015", "LP6010"],
  "current_semester": 3
}
```

3. **Validate prerequisites:**

```json
{
  "course_code": "IT6002",
  "completed_courses": ["IT6015", "BS6001"]
}
```

## Testing

Test the server using the provided test client:

```bash
python test_mcp_server.py
```

## Architecture

The MCP server wraps the `CourseScheduler` class and exposes its functionality through MCP tools:

```
┌─────────────────────┐
│   MCP Client        │
│  (Claude, etc.)     │
└──────────┬──────────┘
           │ MCP Protocol
           │
┌──────────▼──────────┐
│  MCP Server         │
│  (server.py)        │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  CourseScheduler    │
│  (course_scheduler) │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Curriculum Data    │
│  (JSON files)       │
└─────────────────────┘
```

## Business Rules Implemented

- **BR-001**: Mandatory prerequisites validation
- **BR-002**: Elective prerequisites validation
- **BR-003**: Elective credit limit enforcement
- **BR-004**: Co-requisite auto-inclusion
- **BR-005**: Completed co-requisite handling
- **BR-006**: Maximum credit limit
- **BR-007**: Course addition algorithm
- **BR-008**: Non-priority exclusion
- **BR-009**: Priority course handling

## Optimization Strategies

1. **Catch-up Priority**: Courses behind schedule
2. **On-Track Enrollment**: Current semester courses
3. **Advanced Enrollment**: Future courses with warnings

## Error Handling

The server provides detailed error messages for:

- Missing or invalid files
- Invalid course codes/names
- Unmet prerequisites
- Credit limit violations
- Invalid parameters

## Response Format

All tools return JSON responses with:

- `success`: Boolean indicating success/failure
- `error`: Error message (if applicable)
- Tool-specific data fields

## License

Part of the HaUI Course Scheduling System
Version: 1.0.0
Date: October 1, 2025
