# HaUI Agent System - Quick Reference Card

## 🚀 Quick Start Commands

```bash
# Start Course Scheduler
python d:\HaUI-Agent\mcp_course_scheduler\server_fastmcp.py

# Start Course Detail
python d:\HaUI-Agent\mcp_course_detail\server.py

# Start Memory Server
npx @modelcontextprotocol/server-memory
```

## 📋 Tool Cheat Sheet

### Course Scheduler Agent (9 tools)

| Tool | Use When | Input | Output |
|------|----------|-------|--------|
| `initialize_scheduler` | **FIRST** - Start session | curriculum_file | Status |
| `suggest_courses` ⭐ | Need course recommendations | completed, semester, max_credits | Course list |
| `fetch_student_info` | Get student data | None | Student profile |
| `fetch_subjects_name` | LLM semantic search | None | All course names |
| `validate_prerequisites` | Check eligibility | course_code, completed | Can take (Y/N) |
| `get_course_info` | Get course details | course_code | Course info |
| `search_courses` | Find by keyword | keyword | Matching courses |
| `get_semester_courses` | Courses in semester X | semester | Course list |
| `calculate_remaining_credits` | Track progress | completed | Credits remaining |

### Course Detail Agent (5 tools)

| Tool | Use When | Input | Output |
|------|----------|-------|--------|
| `initialize_catalog` | **FIRST** - Start session | curriculum_file | Status |
| `get_course_detail` | Need course info + readiness | course_identifier, completed | Full details |
| `get_assessment_blueprint` ⭐ | Exam prep | course_code | Study plan |
| `search_learning_resources` | Find materials | course_code, web/nonweb | Resource list |
| `generate_course_summary_table` | Compare courses | course_codes, completed | Comparison table |

### Memory Server (9 tools)

| Tool | Use When | Input | Output |
|------|----------|-------|--------|
| `create_entities` | Store new data | entities[] | Success |
| `create_relations` | Link entities | relations[] | Success |
| `add_observations` | Update entity facts | entityName, contents[] | Success |
| `delete_observations` | Remove facts | entityName, observations[] | Success |
| `delete_entities` | Remove nodes | entityNames[] | Success |
| `delete_relations` | Remove links | relations[] | Success |
| `read_graph` | Get all data | None | Full graph |
| `search_nodes` | Find by query | query | Matching entities |
| `open_nodes` | Get specific entities | names[] | Entity details |

## 🎯 Intent → Agent Routing

```
"Kỳ sau học gì?"           → Course Scheduler
"Môn X học những gì?"      → Course Detail
"Cách ôn thi Y?"           → Course Detail → Assessment
"Tôi đã học bao nhiêu?"    → Memory + Course Scheduler
"So sánh môn A, B, C"      → Course Detail → Summary Table
"Kế hoạch lần trước?"      → Memory → Search
```

## 💾 Memory Entity Patterns

### Student Profile
```typescript
{
  name: "Student_123456",
  entityType: "student",
  observations: [
    "name: Nguyen Van A",
    "semester: 3",
    "completed: [BS6001, IT6001]"
  ]
}
```

### Semester Plan
```typescript
{
  name: "Plan_Semester4_Student123456",
  entityType: "semester_plan",
  observations: [
    "semester: 4",
    "courses: [IT6002, IT6015]",
    "credits: 18"
  ]
}
```

### Exam Prep
```typescript
{
  name: "ExamPrep_IT6002_Student123456",
  entityType: "assessment_preparation",
  observations: [
    "course: IT6002",
    "start_date: 2025-10-01",
    "completed_hours: 15"
  ]
}
```

## 🔗 Common Relation Types

```
Student → completed → Course
Student → has_plan → Semester_Plan
Student → preparing_for → Assessment_Prep
Semester_Plan → includes_course → Course
Assessment_Prep → using_resource → Learning_Resource
Course → prerequisite_of → Course
```

## 📊 Workflow Templates

### 1. Semester Planning
```
1. Memory.search_nodes("Student_XXX")
2. CourseScheduler.suggest_courses(completed, sem, max_credits)
3. Memory.create_entities([plan])
4. Response: Recommendations + rationale
```

### 2. Exam Preparation
```
1. CourseDetail.get_course_detail(course, completed)
2. CourseDetail.get_assessment_blueprint(course)
3. CourseDetail.search_learning_resources(course)
4. Memory.create_entities([exam_prep])
5. Response: Blueprint + resources + timeline
```

### 3. Progress Tracking
```
1. Memory.search_nodes("Student_XXX")
2. Extract completed courses
3. CourseScheduler.calculate_remaining_credits(completed)
4. Response: Progress report + insights
```

### 4. Multi-Course Comparison
```
1. Memory.get student completed courses
2. CourseDetail.generate_course_summary_table(courses, completed)
3. Response: Comparison table + recommendations
```

## ⚡ Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Single-agent query | <3s | Simple tool call |
| Multi-agent workflow | <5s | Coordination overhead |
| Memory operations | <500ms | JSON file I/O |
| Response synthesis | <1s | Text processing |

## 🐛 Quick Troubleshooting

### Agent Not Responding
```bash
# Check process
ps aux | grep python | grep mcp

# Restart
pkill -f server_fastmcp.py
python d:\HaUI-Agent\mcp_course_scheduler\server_fastmcp.py
```

### Memory Not Persisting
```bash
# Check file
ls -la d:\HaUI-Agent\student_memory.json

# Verify path
echo $MEMORY_FILE_PATH
```

### Encoding Errors (Windows)
```bash
# Set UTF-8
set PYTHONIOENCODING=utf-8

# In PowerShell
$env:PYTHONIOENCODING="utf-8"
```

### Course Data Not Loading
```bash
# Verify file
ls -la d:\HaUI-Agent\khung*.json

# Test load
python -c "import json; print(len(json.load(open('khung ctrinh cntt.json'))))"
```

## 📝 Response Format Template

```markdown
## 🎯 Summary
[1-2 sentences of what was found/done]

## 📋 Details
[Tables, lists, or structured content]

## 💡 Insights
[Analysis and recommendations]

## ⏭️ Next Steps
[Actionable items]

## 🤝 How I Can Help Further
[Related services offered]
```

## 🎨 Visual Indicators

| Icon | Meaning |
|------|---------|
| ✅ | Ready / Completed / Available |
| ❌ | Not Ready / Missing / Blocked |
| ⚠️ | Warning / Attention Required |
| 🎯 | Goal / Target / Focus |
| 📚 | Study / Learning |
| 📝 | Assessment / Exam |
| 🔍 | Information / Details |
| 💡 | Insight / Tip |
| ⏱️ | Time / Schedule |
| 📊 | Progress / Statistics |

## 🔑 Key Parameters

### Credit Limits
- **Minimum**: 11 credits/semester
- **Maximum**: 27 credits/semester
- **Recommended**: 15-20 credits/semester

### Planning Strategies
- **CATCH-UP**: Maximize credits (behind schedule)
- **PRIORITY**: Focus on specific courses
- **ON-TRACK**: Balanced standard load (default)
- **ADVANCED**: Challenge mode (ahead of schedule)

### Assessment Blueprint Structure
- **Foundation**: 10-20% (Prerequisites review)
- **Core Concepts**: 40-50% (Main theory)
- **Applied Skills**: 30-50% (Practice)

### Resource Credibility Scale
- **1.0**: Official university sources
- **0.9-0.95**: Academic textbooks
- **0.7-0.8**: Educational videos
- **0.6-0.7**: Community content

## 📞 Quick Help

| Issue | Solution |
|-------|----------|
| "Tool not found" | Call initialize first |
| "Prerequisites missing" | Show bridging path |
| "Credit limit exceeded" | Apply strict_credit_limit |
| "Course not found" | Use fuzzy matching |
| "Memory empty" | Create student entity |

## 📚 Documentation Links

- **Full Guide**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **Orchestrator**: [ORCHESTRATOR_PROMPT.md](ORCHESTRATOR_PROMPT.md)
- **Tools**: [AGENT_DESCRIPTIONS.md](AGENT_DESCRIPTIONS.md)
- **Scheduler**: [mcp_course_scheduler/prompt.md](mcp_course_scheduler/prompt.md)
- **Detail**: [mcp_course_detail/prompt.md](mcp_course_detail/prompt.md)

---

**Print this card and keep it handy! 📄**

**Version**: 1.0.0 | **Last Updated**: 2025-10-14
