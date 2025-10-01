# Course Scheduler MCP Server - Complete Documentation

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Architecture](#architecture)
4. [API Reference](#api-reference)
5. [Usage Examples](#usage-examples)
6. [Business Rules](#business-rules)
7. [Error Handling](#error-handling)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

## Overview

The Course Scheduler MCP Server is a Model Context Protocol implementation that exposes an intelligent course scheduling system. It helps students plan their semester by:

- Analyzing learning history and prerequisites
- Respecting student preferences
- Optimizing credit load
- Following curriculum framework
- Providing clear reasoning for suggestions

### Key Features

✅ **Smart Suggestions**: AI-powered course recommendations  
✅ **Prerequisite Validation**: Automatic checking of requirements  
✅ **Flexible Preferences**: Priority and non-priority courses  
✅ **Credit Optimization**: Maximizes learning within credit limits  
✅ **Clear Reasoning**: Explains every recommendation  
✅ **Catch-up Detection**: Identifies courses behind schedule  
✅ **Advanced Warning**: Flags courses ahead of curriculum

## Installation

### Requirements

- Python 3.10 or higher
- pip package manager
- Windows/Linux/macOS

### Step-by-Step Installation

1. **Clone or download the repository**

```bash
cd e:\HaUI_Agent
```

2. **Install Python dependencies**

```bash
cd mcp_course_scheduler
pip install -r requirements.txt
```

3. **Verify installation**

```bash
python verify_installation.py
```

Expected output: All tests should pass with ✓ marks.

### Dependencies

- `mcp>=1.0.0` - Model Context Protocol SDK

The course scheduler itself has no external dependencies (uses only Python standard library).

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP Client Layer                         │
│              (Claude Desktop, Custom Clients)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ MCP Protocol (JSON-RPC)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   MCP Server (server.py)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Tool Handlers:                                       │  │
│  │ - initialize_scheduler                               │  │
│  │ - suggest_courses                                    │  │
│  │ - validate_prerequisites                             │  │
│  │ - get_course_info                                    │  │
│  │ - search_courses                                     │  │
│  │ - get_semester_courses                               │  │
│  │ - calculate_remaining_credits                        │  │
│  │ - format_suggestions                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Python Function Calls
                         │
┌────────────────────────▼────────────────────────────────────┐
│              CourseScheduler (course_scheduler.py)           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Core Logic:                                          │  │
│  │ - Prerequisite validation (BR-001, BR-002)           │  │
│  │ - Co-requisite handling (BR-004, BR-005)             │  │
│  │ - Elective credit limits (BR-003)                    │  │
│  │ - Optimization strategies (1, 2, 3)                  │  │
│  │ - Credit load management (BR-006, BR-007)            │  │
│  │ - Preference handling (BR-008, BR-009)               │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Data Loading
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Curriculum Data                           │
│  - khung ctrinh cntt.json (Full curriculum)                 │
│  - sample.json (Processed structure)                         │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Client Request** → MCP Client sends tool call
2. **Server Processing** → MCP Server validates and routes
3. **Business Logic** → CourseScheduler applies rules
4. **Data Access** → Curriculum data queried
5. **Response** → Results formatted and returned

## API Reference

### Tool: initialize_scheduler

**Purpose**: Initialize the course scheduler with curriculum data

**Parameters**:

- `curriculum_file` (string, required): Path to curriculum JSON
- `processed_file` (string, required): Path to processed JSON

**Returns**:

```json
{
  "success": true,
  "message": "Course scheduler initialized successfully",
  "curriculum_file": "path/to/file.json",
  "processed_file": "path/to/file.json",
  "total_courses": 84
}
```

**Example**:

```json
{
  "curriculum_file": "e:\\HaUI_Agent\\khung ctrinh cntt.json",
  "processed_file": "e:\\HaUI_Agent\\sample.json"
}
```

### Tool: suggest_courses

**Purpose**: Generate optimized course enrollment suggestions

**Parameters**:

- `priority_courses` (array[string], optional): Wanted courses
- `non_priority_courses` (array[string], optional): Unwanted courses
- `max_credits` (integer, required): Maximum credits (1-30)
- `completed_courses` (array[string], required): Completed course codes
- `current_semester` (integer, required): Current semester (1-8)

**Returns**:

```json
{
  "success": true,
  "suggestions": [
    {
      "course_code": "IT6002",
      "course_name": "Cấu trúc dữ liệu và giải thuật",
      "credits": 3.0,
      "reason": "ON-TRACK: This course aligns...",
      "strategy": "ON-TRACK",
      "warnings": [],
      "is_auto_included": false
    }
  ],
  "total_credits": 18.0,
  "warnings": [],
  "errors": []
}
```

**Example**:

```json
{
  "priority_courses": ["Cấu trúc dữ liệu và giải thuật"],
  "non_priority_courses": ["Thiết kế đồ hoạ 2D"],
  "max_credits": 18,
  "completed_courses": ["IT6015", "BS6001", "LP6010"],
  "current_semester": 3
}
```

### Tool: validate_prerequisites

**Purpose**: Check if prerequisites are met for a course

**Parameters**:

- `course_code` (string, required): Course code to validate
- `completed_courses` (array[string], required): Completed courses

**Returns**:

```json
{
  "success": true,
  "course_code": "IT6002",
  "course_name": "Cấu trúc dữ liệu và giải thuật",
  "is_valid": true,
  "prerequisites_required": ["IT6015"],
  "missing_prerequisites": [],
  "message": "Prerequisites satisfied"
}
```

### Tool: get_course_info

**Purpose**: Get detailed information about a course

**Parameters**:

- `course_identifier` (string, required): Course code or name

**Returns**:

```json
{
  "success": true,
  "course_code": "IT6015",
  "course_name": "Kỹ thuật lập trình",
  "credits": 3.0,
  "semester": 2,
  "is_mandatory": true,
  "elective_group": null,
  "group_min_credits": null,
  "prerequisites": [],
  "co_requisites": []
}
```

### Tool: search_courses

**Purpose**: Search for courses by name or code

**Parameters**:

- `query` (string, required): Search query
- `max_results` (integer, optional): Maximum results (default: 10)

**Returns**:

```json
{
  "success": true,
  "query": "lập trình",
  "results_found": 3,
  "results": [
    {
      "course_code": "IT6015",
      "course_name": "Kỹ thuật lập trình",
      "credits": 3.0,
      "semester": 2,
      "is_mandatory": true
    }
  ]
}
```

### Tool: get_semester_courses

**Purpose**: Get all courses for a specific semester

**Parameters**:

- `semester` (integer, required): Semester number (1-8)
- `include_electives` (boolean, optional): Include electives (default: true)

**Returns**:

```json
{
  "success": true,
  "semester": 3,
  "total_courses": 8,
  "mandatory_courses": [...],
  "elective_courses": [...],
  "total_credits": 24.0
}
```

### Tool: calculate_remaining_credits

**Purpose**: Calculate remaining credits for graduation

**Parameters**:

- `completed_courses` (array[string], required): Completed course codes

**Returns**:

```json
{
  "success": true,
  "total_required_credits": 140,
  "completed_credits": 45.0,
  "remaining_credits": 95.0,
  "completion_percentage": 32.14,
  "courses_completed": 15
}
```

### Tool: format_suggestions

**Purpose**: Format suggestions to human-readable text

**Parameters**:

- `suggestions_json` (string, required): JSON string of suggestions

**Returns**: Plain text formatted output

## Usage Examples

### Example 1: New Student (Semester 1)

```python
# Initialize
initialize_scheduler({
  "curriculum_file": "e:\\HaUI_Agent\\khung ctrinh cntt.json",
  "processed_file": "e:\\HaUI_Agent\\sample.json"
})

# Get suggestions
suggest_courses({
  "completed_courses": [],
  "current_semester": 1,
  "max_credits": 20
})
```

**Expected Result**: Courses from semester 1, prioritizing mandatory courses.

### Example 2: Mid-Program Student with Preferences

```python
suggest_courses({
  "priority_courses": ["Trí tuệ nhân tạo", "Mạng máy tính"],
  "non_priority_courses": ["Thiết kế đồ hoạ 2D"],
  "max_credits": 18,
  "completed_courses": [
    "IT6015", "IT6016", "IT6120", "IT6126",
    "BS6001", "BS6002", "LP6010", "LP6011"
  ],
  "current_semester": 4
})
```

**Expected Result**: Prioritizes requested courses if eligible, excludes non-priority.

### Example 3: Catch-Up Student

```python
suggest_courses({
  "completed_courses": ["IT6015", "BS6002"],
  "current_semester": 5,
  "max_credits": 22
})
```

**Expected Result**: Heavy emphasis on catch-up courses from semesters 1-4.

### Example 4: Prerequisite Validation

```python
validate_prerequisites({
  "course_code": "IT6002",
  "completed_courses": ["IT6015", "IT6120"]
})
```

**Expected Result**: Validation status with missing prerequisites if any.

## Business Rules

### BR-001: Mandatory Prerequisites

- Mandatory courses require ≥1 completed prerequisite
- Empty prerequisite list = immediately eligible

### BR-002: Elective Prerequisites

- Elective courses require ≥1 completed prerequisite
- Same logic as mandatory courses

### BR-003: Elective Credit Limits

- Total credits in elective group ≤ group minimum required
- Formula: `Σ(Completed) + Σ(Suggested) ≤ Minimum`

### BR-004: Co-requisite Auto-Inclusion

- Unmet co-requisites automatically included
- Both courses must fit in credit limit

### BR-005: Completed Co-requisites

- Completed co-requisites allow independent enrollment
- No automatic inclusion needed

### BR-006: Maximum Credit Limit

- Total suggested credits ≤ user-specified maximum
- Hard constraint, never violated

### BR-007: Course Addition Algorithm

- Stops when max credits OR no eligible courses
- Greedy approach with semester ordering

### BR-008: Non-Priority Exclusion

- Excludes non-priority courses unless:
  - Required as co-requisite, OR
  - Catch-up priority course

### BR-009: Priority Course Handling

- Priority courses processed first (after catch-up)
- May fail if prerequisites not met

## Error Handling

### Common Errors

| Error                         | Cause                    | Solution                           |
| ----------------------------- | ------------------------ | ---------------------------------- |
| "Scheduler not initialized"   | Tool called before init  | Call initialize_scheduler first    |
| "Course not found"            | Invalid course code/name | Verify course exists in curriculum |
| "Maximum credits must be > 0" | Invalid max_credits      | Use positive integer               |
| "File not found"              | Wrong file path          | Check absolute path is correct     |
| "Invalid JSON"                | Corrupted data file      | Verify JSON syntax                 |

### Error Response Format

```json
{
  "success": false,
  "error": "Error message here"
}
```

## Testing

### Unit Tests

Run core functionality tests:

```bash
cd e:\HaUI_Agent
python test_scheduler.py
```

### Integration Tests

Test MCP server:

```bash
cd e:\HaUI_Agent\mcp_course_scheduler
python test_mcp_server.py
```

### Verification

Quick verification:

```bash
python verify_installation.py
```

## Deployment

### Claude Desktop

1. Copy `claude_desktop_config_example.json` content
2. Paste into `%APPDATA%\Claude\claude_desktop_config.json`
3. Update paths if necessary
4. Restart Claude Desktop

### Custom MCP Client

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["-u", "path/to/server.py"],
    env={"PYTHONPATH": "path/to/parent"}
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        # Use tools...
```

## Troubleshooting

### Issue: Server Not Starting

**Symptoms**: Claude doesn't show the server

**Solutions**:

1. Check Python is in PATH
2. Verify absolute paths in config
3. Check file permissions
4. Review Claude logs

### Issue: Import Errors

**Symptoms**: ModuleNotFoundError

**Solutions**:

1. Verify PYTHONPATH includes parent directory
2. Check course_scheduler.py exists
3. Install requirements: `pip install -r requirements.txt`

### Issue: No Courses Suggested

**Symptoms**: Empty suggestion list

**Solutions**:

1. Check completed courses are valid codes
2. Verify current_semester is correct
3. Increase max_credits
4. Review non_priority_courses list

### Issue: Prerequisite Always Failing

**Symptoms**: All courses blocked by prerequisites

**Solutions**:

1. Verify completed_courses includes valid codes
2. Check at least 1 prerequisite is completed
3. Review course prerequisite structure in data

## Performance Considerations

- **Initialization**: ~1 second for 84 courses
- **Suggestions**: <0.5 seconds typical
- **Search**: <0.1 seconds
- **Memory**: ~10MB for curriculum data

## Security Notes

- Server runs locally only
- No network connections
- No data persistence
- No user authentication (local use)

## Version History

- **v1.0.0** (October 2025): Initial release
  - 8 MCP tools
  - Full business rule compliance
  - Comprehensive documentation

## Contributing

For bug reports or feature requests:

1. Document the issue clearly
2. Provide reproduction steps
3. Include test cases if applicable

## License

Part of the HaUI Course Scheduling System  
For educational use

---

**Last Updated**: October 1, 2025  
**Author**: Business Analyst / Development Team  
**Version**: 1.0.0
