# Quick Start Guide - Course Scheduler MCP Server

## Prerequisites

- Python 3.10 or higher
- pip package manager

## Installation Steps

### 1. Install Dependencies

```bash
cd e:\HaUI_Agent\mcp_course_scheduler
pip install -r requirements.txt
```

### 2. Verify Installation

Test that the server works:

```bash
python test_mcp_server.py
```

You should see test results for all 9 test cases.

## Configuration for Claude Desktop

### Windows Configuration

1. Open Claude Desktop configuration file:

   - Location: `%APPDATA%\Claude\claude_desktop_config.json`
   - Or: `C:\Users\<YourUsername>\AppData\Roaming\Claude\claude_desktop_config.json`

2. Add the server configuration:

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

3. Restart Claude Desktop

4. Verify the server appears in the MCP section

## Usage in Claude

### Step 1: Initialize the Scheduler

First, always initialize the scheduler:

```
Please initialize the course scheduler with:
- curriculum_file: e:\HaUI_Agent\khung ctrinh cntt.json
- processed_file: e:\HaUI_Agent\sample.json
```

### Step 2: Get Course Suggestions

Example request:

```
I'm a student in semester 3. I've completed:
- LP6010, BS6018, BS6002, DC6005, DC6004, DC6007, DC6006
- IT6011, IT6015, BS6027, IT6016, BS6001, LP6011

I want to take "Cấu trúc dữ liệu và giải thuật" this semester.
I don't want to take "Thiết kế đồ hoạ 2D".
Maximum 18 credits.

Please suggest courses for me.
```

### Step 3: Explore Other Tools

- **Search courses**: "Search for courses about 'an toàn'"
- **Get course info**: "Tell me about course IT6002"
- **Check prerequisites**: "Can I take IT6002 if I've completed IT6015?"
- **View semester**: "Show me all courses in semester 4"
- **Check progress**: "How many credits have I completed?"

## Common Use Cases

### 1. New Student Planning

```
I'm a new student starting semester 1.
Show me all courses for semester 1 and suggest a 20-credit schedule.
```

### 2. Mid-Program Student

```
I'm in semester 4 with these completed courses: [list]
I want to prioritize: [courses]
Avoid: [courses]
Max credits: 18
Please suggest my schedule.
```

### 3. Catch-Up Student

```
I'm in semester 5 but only completed: [short list]
Help me catch up with priority on missing core courses.
Max credits: 22
```

### 4. Advanced Planning

```
I want to graduate early. I'm in semester 3.
Show me which advanced courses I can take from semester 5 or 6.
```

## Troubleshooting

### Server Not Appearing in Claude

1. Check the config file path is correct
2. Verify Python is in system PATH
3. Check file paths use absolute paths
4. Restart Claude Desktop completely

### Import Errors

Make sure `PYTHONPATH` includes the parent directory:

```json
"env": {
  "PYTHONPATH": "e:\\HaUI_Agent"
}
```

### File Not Found Errors

Verify the curriculum files exist:

- `e:\HaUI_Agent\khung ctrinh cntt.json`
- `e:\HaUI_Agent\sample.json`

### Testing Without Claude

Run the test client:

```bash
cd e:\HaUI_Agent\mcp_course_scheduler
python test_mcp_server.py
```

## Example Workflow

1. **Initialize** → Load curriculum data
2. **Search** → Find courses of interest
3. **Get Info** → Check prerequisites and details
4. **Validate** → Confirm you can take a course
5. **Suggest** → Get optimized schedule
6. **Format** → Get readable output
7. **Calculate** → Track graduation progress

## Available Tools Summary

| Tool                          | Purpose                    | Required After Init? |
| ----------------------------- | -------------------------- | -------------------- |
| `initialize_scheduler`        | Load curriculum data       | No (first step)      |
| `suggest_courses`             | Get course recommendations | Yes                  |
| `validate_prerequisites`      | Check if can take course   | Yes                  |
| `get_course_info`             | Get course details         | Yes                  |
| `search_courses`              | Find courses               | Yes                  |
| `get_semester_courses`        | View semester curriculum   | Yes                  |
| `calculate_remaining_credits` | Check progress             | Yes                  |
| `format_suggestions`          | Pretty print results       | Yes                  |

## Tips for Best Results

1. **Always initialize first** - The server needs curriculum data loaded
2. **Use specific course codes** - More reliable than names
3. **Provide complete history** - Better suggestions with full completion list
4. **Set realistic max credits** - Typically 15-22 credits per semester
5. **Review warnings** - Pay attention to co-requisite and advanced course warnings

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the [Use Case Description](../USE_CASE.md) for business rules
- Check [course_scheduler.py](../course_scheduler.py) for implementation details

## Support

For issues or questions:

1. Check the test client output for errors
2. Review the business rules in the use case document
3. Verify your curriculum data files are valid JSON
4. Check Python version compatibility (3.10+)
