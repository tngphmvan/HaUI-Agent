# Course Detail and Assessment Preparation MCP Server

## Overview
This MCP server implements the "View Course Detail and Prepare for Assessment" use case specification. It provides comprehensive course information, exam preparation guidance, and curated learning resources.

## Features

### 1. Course Detail Expression
- **Comprehensive course information**: Code, name, credits, semester, type (mandatory/elective)
- **Prerequisites & Corequisites**: With readiness checking
- **Learning outcomes**: Mapped to assessment items
- **Elective group tracking**: Warns if minimum already met

### 2. Assessment Preparation
- **Assessment Blueprint**: Topics with weights and difficulty levels
- **Knowledge Categories**:
  - Foundation (prerequisites review)
  - Core Concepts (main theoretical knowledge)
  - Applied Skills (hands-on practice)
- **Readiness Checklist**: Self-assessment items
- **Study Plan**: Time-boxed preparation schedule

### 3. Learning Resource Curation
- **Web Resources**: 
  - Official syllabi
  - Educational videos
  - Tutorial sites
  - Academic papers
- **Non-Web Resources**:
  - Textbooks (with ISBN)
  - PDF lecture notes
  - Past exam papers
  - Internal documents
- **Quality Metrics**:
  - Credibility scoring (0-1)
  - Recency checking
  - Source verification

## Available Tools

### `initialize_catalog`
Initialize the course catalog from curriculum JSON file.
```python
initialize_catalog(curriculum_file="path/to/khung_ctrinh_cntt.json")
```

### `get_course_detail`
Get comprehensive course details with readiness assessment.
```python
get_course_detail(
    course_identifier="IT6015",  # or "Kỹ thuật lập trình"
    completed_courses=["BS6001", "BS6002"]
)
```

**Returns**:
- Course metadata
- Prerequisites/corequisites (with met/unmet status)
- Readiness assessment
- Bridging path for unmet requirements
- Next steps

### `get_assessment_blueprint`
Generate exam preparation blueprint.
```python
get_assessment_blueprint(course_code="IT6015")
```

**Returns**:
- Foundation topics (10-20%)
- Core concepts (40-50%)
- Applied skills (30-50%)
- Readiness checklist
- Estimated prep hours
- Study plan

### `search_learning_resources`
Search and curate learning resources.
```python
search_learning_resources(
    course_code="IT6015",
    include_web=True,
    include_nonweb=True,
    max_results=10
)
```

**Returns**:
- Web resources with URLs and dates
- Non-web resources with locations
- Quality metrics
- Citation guide

### `generate_course_summary_table`
Generate tabular summary for multiple courses.
```python
generate_course_summary_table(
    course_codes=["IT6015", "IT6002", "BS6003"],
    completed_courses=["BS6001", "BS6002"]
)
```

**Returns**:
- Summary table (Code | Name | Credits | Semester | Type | Prereq | Coreq | Readiness)
- Statistics (total credits, mandatory/elective count, readiness count)

## Use Case Flow

### Main Success Scenario
1. Student requests info: `get_course_detail("Cấu trúc dữ liệu")`
2. System resolves course and checks prerequisites
3. System provides detailed info + readiness status
4. Student requests exam prep: `get_assessment_blueprint("IT6002")`
5. System generates blueprint with topics, weights, checklist
6. Student searches resources: `search_learning_resources("IT6002")`
7. System returns curated web and non-web sources
8. Student receives complete preparation package

### Alternative Flows
- **A1: Ambiguous name** → Returns top 5 suggestions
- **A2: Course not found** → Suggests similar courses
- **A3: Prerequisites unmet** → Provides bridging path
- **A4: Elective fulfilled** → Warns about group minimum

## Business Rules (Implemented)

- **BR-01**: Show all prerequisites; mark readiness; propose prep path
- **BR-02**: Track elective group fulfillment
- **BR-03**: Respect credit/semester constraints
- **BR-04**: Prefer official and recent sources; version all references

## Data Model

### KnowledgeTopic
```python
{
    "topic": str,
    "weight_percentage": int,
    "difficulty": str,  # Easy, Medium, Hard
    "description": str,
    "key_concepts": List[str]
}
```

### AssessmentBlueprint
```python
{
    "course_code": str,
    "course_name": str,
    "foundation_topics": List[KnowledgeTopic],
    "core_concepts": List[KnowledgeTopic],
    "applied_skills": List[KnowledgeTopic],
    "readiness_checklist": List[str],
    "estimated_prep_hours": int
}
```

### LearningSource
```python
{
    "title": str,
    "type": str,  # web, pdf, textbook, video, official_doc
    "url": Optional[str],
    "author": Optional[str],
    "date": Optional[str],
    "credibility_score": float,  # 0-1
    "location": Optional[str],
    "notes": str
}
```

## Quality Metrics

- **Accuracy**: ≥95% alignment with official syllabus
- **Freshness**: Sources ≤3 years unless canonical
- **Explainability**: Each topic mapped to learning outcome
- **Source Coverage**: ≥3 credible sources per course

## Example Usage

### Python Client
```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["d:/HaUI-Agent/mcp_course_detail/server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Initialize catalog
            result = await session.call_tool("initialize_catalog", {
                "curriculum_file": "d:/HaUI-Agent/khung ctrinh cntt.json"
            })
            
            # Get course detail
            detail = await session.call_tool("get_course_detail", {
                "course_identifier": "IT6015",
                "completed_courses": ["BS6001", "BS6002"]
            })
            
            # Get assessment blueprint
            blueprint = await session.call_tool("get_assessment_blueprint", {
                "course_code": "IT6015"
            })
            
            # Search resources
            resources = await session.call_tool("search_learning_resources", {
                "course_code": "IT6015",
                "include_web": True,
                "include_nonweb": True,
                "max_results": 10
            })
```

### CLI Usage
```bash
# Run server
python d:/HaUI-Agent/mcp_course_detail/server.py

# Or with mcp dev
cd d:/HaUI-Agent/mcp_course_detail
mcp dev server.py
```

## Integration with AI Agents

### Recommended Prompt
```
You are an academic advisor AI assistant. Use the course-detail-server tools to:

1. ALWAYS initialize_catalog first
2. For course inquiries: get_course_detail → assess readiness → provide guidance
3. For exam prep: get_assessment_blueprint → generate study plan
4. For resources: search_learning_resources → curate and cite properly
5. Format responses in tables with clear sections

When student asks about a course:
- Check prerequisites and readiness
- Provide assessment blueprint
- Suggest learning resources
- Create personalized study plan
```

## Future Enhancements

1. **Real Web Search Integration**
   - Google Scholar API
   - University library API
   - YouTube API for tutorials

2. **Personalized Assessment**
   - Learning style adaptation
   - Performance prediction
   - Weak area identification

3. **Collaborative Features**
   - Peer study groups
   - Shared resource ratings
   - Community Q&A

4. **Advanced Analytics**
   - Success rate prediction
   - Optimal course sequencing
   - Workload balancing

## License
MIT

## Author
HaUI Agent Development Team
