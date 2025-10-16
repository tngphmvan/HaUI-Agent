# HaUI Agent System - Agent Descriptions

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR AGENT                          │
│                  (Main Coordination Layer)                      │
└─────────────────┬───────────────────────────┬───────────────────┘
                  │                           │
      ┌───────────▼───────────┐   ┌──────────▼──────────┐
      │  Course Scheduler     │   │  Course Detail      │
      │      Agent            │   │     Agent           │
      └───────────┬───────────┘   └──────────┬──────────┘
                  │                           │
                  └───────────┬───────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Memory Server   │
                    │  (Knowledge Graph)│
                    └───────────────────┘
```

## Agent 1: Course Scheduler Agent

### Identity
**Name**: `course-scheduler-agent`  
**Version**: 1.0.0  
**Purpose**: Intelligent course planning and semester scheduling for HaUI students  
**Type**: Specialist Agent (Planning & Optimization)

### Description
A specialized AI agent that helps students create optimal semester course plans based on their academic progress, prerequisites, and goals. Uses greedy algorithms and backtracking to suggest the best course combinations while respecting credit limits, prerequisites, and student priorities.

### Core Capabilities
1. **Semester Planning** - Generate complete semester course recommendations
2. **Credit Optimization** - Balance course load within 11-27 credit range
3. **Prerequisite Validation** - Ensure students meet all requirements
4. **Strategy-Based Planning** - Support multiple planning strategies (CATCH-UP, PRIORITY, ON-TRACK, ADVANCED)
5. **Course Discovery** - Intelligent fuzzy matching for Vietnamese course names
6. **Academic Tracking** - Calculate remaining credits to graduation

### MCP Tools Exposed

#### 1. `initialize_scheduler`
**Purpose**: Load course curriculum and prepare the scheduler  
**Category**: Initialization  
**Inputs**:
- `curriculum_file` (string): Path to curriculum JSON (default: auto-detect)
- `course_number` (int, optional): Specific program/course number

**Returns**: Status with total courses loaded and programs available

**Usage Pattern**:
```json
{
  "tool": "initialize_scheduler",
  "params": {
    "curriculum_file": "D:\\HaUI-Agent\\khung ctrinh cntt.json"
  }
}
```

#### 2. `suggest_courses` (PRIMARY - 95% use cases)
**Purpose**: Get intelligent course recommendations for next semester  
**Category**: Planning & Decision Support  
**Inputs**:
- `completed_courses` (list[str]): Courses student has completed
- `current_semester` (int): Student's current semester number
- `max_credits` (int, 11-27): Maximum credits to take
- `priority_courses` (list[str], optional): Courses to prioritize
- `non_priority_courses` (list[str], optional): Courses to avoid
- `strict_credit_limit` (bool, default=True): Enforce exact credit matching
- `strategy` (str, optional): Planning strategy (CATCH-UP/PRIORITY/ON-TRACK/ADVANCED)

**Returns**: 
- Recommended courses for the semester
- Total credits
- Strategy explanation
- Warnings (if any)
- Alternative suggestions

**Usage Pattern**:
```json
{
  "tool": "suggest_courses",
  "params": {
    "completed_courses": ["BS6001", "BS6002", "IT6001"],
    "current_semester": 3,
    "max_credits": 20,
    "priority_courses": ["IT6002"],
    "strict_credit_limit": true
  }
}
```

#### 3. `fetch_student_info`
**Purpose**: Retrieve student's academic progress  
**Category**: Data Retrieval  
**Inputs**: None (uses internal state)

**Returns**: Student name, ID, program, learned courses, current semester

#### 4. `fetch_subjects_name`
**Purpose**: Get all available course names for intelligent mapping  
**Category**: Discovery  
**Inputs**: None

**Returns**: Complete list of course codes and names

**Use Cases**:
- LLM semantic search for course names
- Fuzzy matching Vietnamese course titles
- Course name validation

#### 5. `validate_prerequisites`
**Purpose**: Check if student can take a specific course  
**Category**: Validation  
**Inputs**:
- `course_code` (str): Course to validate
- `completed_courses` (list[str]): Student's completed courses

**Returns**: 
- Can take (yes/no)
- Missing prerequisites
- Missing corequisites
- Recommendations

#### 6. `get_course_info`
**Purpose**: Get detailed information about a course  
**Category**: Information Retrieval  
**Inputs**:
- `course_code` (str): Course code to look up

**Returns**: Name, credits, semester, prerequisites, corequisites, type

#### 7. `search_courses`
**Purpose**: Search courses by keyword  
**Category**: Discovery  
**Inputs**:
- `keyword` (str): Search term
- `search_type` (str, optional): "name", "code", or "all"

**Returns**: Matching courses with details

#### 8. `get_semester_courses`
**Purpose**: Get all courses typically taken in a specific semester  
**Category**: Information Retrieval  
**Inputs**:
- `semester` (int): Semester number

**Returns**: All courses for that semester

#### 9. `calculate_remaining_credits`
**Purpose**: Calculate credits needed to graduate  
**Category**: Analytics  
**Inputs**:
- `completed_courses` (list[str]): Student's completed courses

**Returns**: 
- Total credits completed
- Credits remaining
- Percentage complete

### Integration with Memory Server

The Course Scheduler Agent should store and retrieve:

**Entities**:
- `Student` (entityType: "student")
  - Observations: ["enrolled_semester_X", "completed_course_Y", "target_graduation_Z"]
- `Semester_Plan` (entityType: "plan")
  - Observations: ["planned_courses: [...]", "credits: X", "strategy: Y"]

**Relations**:
- `Student` → `completed` → `Course`
- `Student` → `planned` → `Semester_Plan`
- `Semester_Plan` → `includes` → `Course`

**Usage Example**:
```typescript
// Store student progress
create_entities([{
  name: "Student_123456",
  entityType: "student",
  observations: [
    "name: Nguyen Van A",
    "semester: 3",
    "completed: [BS6001, BS6002, IT6001]",
    "target_graduation: 2026-06"
  ]
}])

// Store semester plan
create_entities([{
  name: "Plan_Semester4_Student123456",
  entityType: "semester_plan",
  observations: [
    "semester: 4",
    "courses: [IT6002, IT6015, BS6003]",
    "total_credits: 18",
    "strategy: ON-TRACK",
    "created_date: 2025-10-14"
  ]
}])

// Create relations
create_relations([
  {from: "Student_123456", to: "Plan_Semester4_Student123456", relationType: "has_plan"},
  {from: "Plan_Semester4_Student123456", to: "IT6002", relationType: "includes_course"}
])
```

### Decision Logic
- **Always** call `initialize_scheduler` first
- **Prefer** `suggest_courses` for general planning (95% of cases)
- Use other tools only when student asks for specific information
- Apply `strict_credit_limit=True` by default for exact credit matching
- Suggest alternative courses if target cannot be met

### Strengths
- ✅ Optimal course selection with multiple strategies
- ✅ Credit balancing within university regulations
- ✅ Prerequisite validation
- ✅ Handles Vietnamese course names with fuzzy matching

### Limitations
- ❌ Currently only supports IT program (single program limitation)
- ❌ No real-time course availability data
- ❌ Cannot handle course conflicts (time clashes)
- ❌ Limited to curriculum data structure

---

## Agent 2: Course Detail & Assessment Agent

### Identity
**Name**: `course-detail-agent`  
**Version**: 1.0.0  
**Purpose**: Comprehensive course information and exam preparation support  
**Type**: Specialist Agent (Information & Assessment)

### Description
A specialized AI agent that provides in-depth course information, generates exam preparation blueprints, curates learning resources, and assesses student readiness for courses. Focuses on helping students understand course requirements and prepare effectively for assessments.

### Core Capabilities
1. **Course Intelligence** - Detailed course specs with readiness assessment
2. **Exam Preparation** - Assessment blueprints with topics, weights, difficulty
3. **Resource Curation** - Web and non-web learning materials
4. **Prerequisite Checking** - Validate if student can take a course
5. **Study Planning** - Time-boxed preparation schedules
6. **Multi-Course Comparison** - Side-by-side analysis tables

### MCP Tools Exposed

#### 1. `initialize_catalog`
**Purpose**: Load course curriculum data  
**Category**: Initialization  
**Inputs**:
- `curriculum_file` (string): Path to curriculum JSON

**Returns**: Success status, total courses, program info

**Usage Pattern**:
```json
{
  "tool": "initialize_catalog",
  "params": {
    "curriculum_file": "D:\\HaUI-Agent\\khung ctrinh cntt.json"
  }
}
```

#### 2. `get_course_detail`
**Purpose**: Get comprehensive course information with readiness check  
**Category**: Information Retrieval & Validation  
**Inputs**:
- `course_identifier` (str): Course code or name (supports fuzzy matching)
- `completed_courses` (list[str]): Student's completed courses

**Returns**:
- Full course details (code, name, credits, semester, type)
- Prerequisites and corequisites with completion status
- Readiness assessment (Ready/Not Ready)
- Bridging path if prerequisites missing
- Next actionable steps

**Usage Pattern**:
```json
{
  "tool": "get_course_detail",
  "params": {
    "course_identifier": "Cấu trúc dữ liệu",  // Fuzzy matching works!
    "completed_courses": ["BS6001", "IT6001"]
  }
}
```

#### 3. `get_assessment_blueprint` (EXAM PREP PRIMARY)
**Purpose**: Generate exam preparation blueprint with study plan  
**Category**: Assessment Preparation  
**Inputs**:
- `course_code` (str): Course code (e.g., "IT6002")

**Returns**:
- **Foundation Topics** (10-20%) - Prerequisites review
  - Topic, weight, difficulty, key concepts
- **Core Concepts** (40-50%) - Main theoretical content
  - Topic, weight, difficulty, key concepts
- **Applied Skills** (30-50%) - Practical implementation
  - Topic, weight, difficulty, key concepts
- Readiness checklist
- Estimated preparation hours
- Weekly study plan breakdown

**Usage Pattern**:
```json
{
  "tool": "get_assessment_blueprint",
  "params": {
    "course_code": "IT6002"
  }
}
```

**Example Output Structure**:
```json
{
  "foundation_topics": [
    {
      "topic": "Arrays & Linked Lists",
      "weight_percentage": 15,
      "difficulty": "Medium",
      "key_concepts": ["Arrays", "Linked Lists", "Iterators"]
    }
  ],
  "core_concepts": [...],
  "applied_skills": [...],
  "readiness_checklist": [
    "Understand all core concepts",
    "Can implement key algorithms",
    "Solve practice problems"
  ],
  "estimated_prep_hours": 30
}
```

#### 4. `search_learning_resources`
**Purpose**: Find curated learning materials  
**Category**: Resource Discovery  
**Inputs**:
- `course_code` (str): Course code
- `include_web` (bool, default=True): Include online resources
- `include_nonweb` (bool, default=True): Include textbooks, PDFs
- `max_results` (int, default=10): Maximum results per category

**Returns**:
- **Web Resources**:
  - Official syllabi (credibility: 1.0)
  - Educational videos (credibility: 0.7-0.8)
  - Tutorial sites (credibility: 0.6-0.9)
- **Non-Web Resources**:
  - Textbooks (credibility: 0.95)
  - PDF lecture notes (credibility: 1.0)
  - Past exam papers (credibility: 0.9)
- Quality metrics (average credibility, official sources count)
- Citation guide for academic use

**Usage Pattern**:
```json
{
  "tool": "search_learning_resources",
  "params": {
    "course_code": "IT6015",
    "include_web": true,
    "include_nonweb": true,
    "max_results": 5
  }
}
```

#### 5. `generate_course_summary_table`
**Purpose**: Create comparison table for multiple courses  
**Category**: Multi-Course Analysis  
**Inputs**:
- `course_codes` (list[str]): List of course codes
- `completed_courses` (list[str]): Student's completed courses

**Returns**:
- Tabular summary (code, name, credits, semester, type, prerequisites, readiness)
- Statistics (total credits, mandatory/elective count, ready/not ready)
- Visual readiness indicators (✓/✗)

**Usage Pattern**:
```json
{
  "tool": "generate_course_summary_table",
  "params": {
    "course_codes": ["IT6002", "IT6015", "IT6003"],
    "completed_courses": ["BS6001", "IT6001"]
  }
}
```

### Integration with Memory Server

The Course Detail Agent should store and retrieve:

**Entities**:
- `Course_Study_Session` (entityType: "study_session")
  - Observations: ["course: IT6002", "date: 2025-10-14", "topics_covered: [...]", "hours_spent: X"]
- `Assessment_Preparation` (entityType: "exam_prep")
  - Observations: ["course: IT6002", "start_date: 2025-10-01", "target_date: 2025-10-30", "progress: 60%"]
- `Learning_Resource` (entityType: "resource")
  - Observations: ["title: Data Structures Textbook", "type: textbook", "credibility: 0.95", "status: reading"]

**Relations**:
- `Student` → `preparing_for` → `Assessment_Preparation`
- `Assessment_Preparation` → `uses_resource` → `Learning_Resource`
- `Student` → `studied` → `Course_Study_Session`
- `Course_Study_Session` → `covered_topic` → `Topic`

**Usage Example**:
```typescript
// Store exam preparation
create_entities([{
  name: "ExamPrep_IT6002_Student123456",
  entityType: "assessment_preparation",
  observations: [
    "course: IT6002 - Cấu trúc dữ liệu",
    "start_date: 2025-10-01",
    "exam_date: 2025-10-30",
    "total_prep_hours: 30",
    "completed_hours: 18",
    "progress: 60%",
    "weak_topics: [Trees, Graphs]",
    "strong_topics: [Arrays, Stacks]"
  ]
}])

// Store learning resources used
create_entities([{
  name: "Resource_DataStructures_Textbook",
  entityType: "learning_resource",
  observations: [
    "title: Introduction to Data Structures",
    "type: textbook",
    "author: Cormen et al.",
    "credibility: 0.95",
    "location: Library Section C",
    "chapters_read: [1,2,3,4]",
    "useful_for: [IT6002, IT6015]"
  ]
}])

// Create relations
create_relations([
  {from: "Student_123456", to: "ExamPrep_IT6002_Student123456", relationType: "preparing_for"},
  {from: "ExamPrep_IT6002_Student123456", to: "Resource_DataStructures_Textbook", relationType: "using_resource"},
  {from: "Student_123456", to: "IT6002", relationType: "studying"}
])

// Track study sessions
add_observations({
  entityName: "ExamPrep_IT6002_Student123456",
  contents: [
    "session_2025-10-14: Studied Trees (3 hours)",
    "session_2025-10-15: Practice problems on Graphs (2 hours)",
    "milestone: Completed foundation topics"
  ]
})
```

### Decision Logic
- **Always** call `initialize_catalog` first
- For course info: `get_course_detail` (with fuzzy matching support)
- For exam prep: `get_assessment_blueprint` → `search_learning_resources`
- For comparison: `generate_course_summary_table`
- Prioritize official sources (credibility >= 0.9)

### Strengths
- ✅ Comprehensive course information with readiness checking
- ✅ Structured exam preparation with weighted topics
- ✅ Curated resources with credibility scoring
- ✅ Fuzzy matching for Vietnamese course names
- ✅ Study plan generation with time estimates

### Limitations
- ❌ Mock assessment blueprints (need real syllabus integration)
- ❌ Mock resource data (need real web search APIs)
- ❌ No personalized learning style adaptation
- ❌ No real-time resource availability

---

## Agent 3: Memory Server (Knowledge Graph)

### Identity
**Name**: `memory-server`  
**Version**: 0.6.3  
**Purpose**: Persistent knowledge graph for long-term memory across conversations  
**Type**: Infrastructure Agent (Data Persistence)

### Description
Official Model Context Protocol knowledge graph memory server. Stores entities, relations, and observations in a graph structure, enabling AI agents to remember information about users, plans, and context across multiple conversations and sessions.

### Core Capabilities
1. **Entity Management** - Create, read, update, delete entities
2. **Relation Management** - Define connections between entities
3. **Observation Tracking** - Add/remove observations to entities
4. **Graph Operations** - Read entire graph, search nodes, open specific nodes
5. **Persistent Storage** - JSON file-based storage (configurable path)

### MCP Tools Exposed

#### 1. `create_entities`
**Purpose**: Create multiple new entities in the knowledge graph  
**Category**: Entity Management  
**Inputs**:
- `entities` (array of objects):
  - `name` (string): Entity identifier
  - `entityType` (string): Type classification
  - `observations` (string[]): Associated observations

**Returns**: Success message

**Usage Pattern**:
```json
{
  "tool": "create_entities",
  "params": {
    "entities": [
      {
        "name": "Student_123456",
        "entityType": "student",
        "observations": [
          "name: Nguyen Van A",
          "semester: 3",
          "program: Information Technology"
        ]
      }
    ]
  }
}
```

#### 2. `create_relations`
**Purpose**: Create directed relations between entities  
**Category**: Relation Management  
**Inputs**:
- `relations` (array of objects):
  - `from` (string): Source entity name
  - `to` (string): Target entity name
  - `relationType` (string): Relationship type (active voice)

**Returns**: Success message

**Usage Pattern**:
```json
{
  "tool": "create_relations",
  "params": {
    "relations": [
      {
        "from": "Student_123456",
        "to": "IT6002",
        "relationType": "completed"
      }
    ]
  }
}
```

#### 3. `add_observations`
**Purpose**: Add new observations to existing entities  
**Category**: Observation Management  
**Inputs**:
- `observations` (array of objects):
  - `entityName` (string): Target entity
  - `contents` (string[]): New observations

**Returns**: Added observations per entity

#### 4. `delete_observations`
**Purpose**: Remove specific observations from entities  
**Category**: Observation Management  
**Inputs**:
- `deletions` (array of objects):
  - `entityName` (string): Target entity
  - `observations` (string[]): Observations to delete

**Returns**: Success message

#### 5. `delete_entities`
**Purpose**: Delete entities and their relations  
**Category**: Entity Management  
**Inputs**:
- `entityNames` (string[]): Array of entity names to delete

**Returns**: Success message

#### 6. `delete_relations`
**Purpose**: Delete specific relations from graph  
**Category**: Relation Management  
**Inputs**:
- `relations` (array of objects): Relations to delete

**Returns**: Success message

#### 7. `read_graph`
**Purpose**: Retrieve the entire knowledge graph  
**Category**: Graph Operations  
**Inputs**: None

**Returns**: Complete graph structure with all entities and relations

#### 8. `search_nodes`
**Purpose**: Search for nodes based on query  
**Category**: Graph Operations  
**Inputs**:
- `query` (string): Search query (matches names, types, observations)

**Returns**: Matching entities and their relations

#### 9. `open_nodes`
**Purpose**: Retrieve specific nodes by name  
**Category**: Graph Operations  
**Inputs**:
- `names` (string[]): Entity names to retrieve

**Returns**: Requested entities and relations between them

### Data Model

**Entity Structure**:
```typescript
interface Entity {
  name: string;           // Unique identifier
  entityType: string;     // Classification (student, course, plan, etc.)
  observations: string[]; // Facts/observations about the entity
}
```

**Relation Structure**:
```typescript
interface Relation {
  from: string;        // Source entity name
  to: string;          // Target entity name
  relationType: string; // Active voice relationship
}
```

### Storage
- **Default Path**: `memory.json` in server directory
- **Configurable**: Set `MEMORY_FILE_PATH` environment variable
- **Format**: JSON file with entities and relations arrays
- **Persistence**: Automatic save on every modification

### Configuration Example
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "D:\\HaUI-Agent\\student_memory.json"
      }
    }
  }
}
```

### Best Practices for HaUI Agent System

1. **Entity Naming Convention**:
   - Students: `Student_{student_id}`
   - Courses: `{course_code}` (e.g., "IT6002")
   - Plans: `Plan_Semester{X}_Student{id}`
   - Exam Prep: `ExamPrep_{course_code}_Student{id}`
   - Resources: `Resource_{descriptive_name}`

2. **Entity Types**:
   - `student` - Student profiles
   - `course` - Course information
   - `semester_plan` - Semester planning
   - `assessment_preparation` - Exam prep tracking
   - `learning_resource` - Study materials
   - `study_session` - Individual study records

3. **Relation Types** (Active Voice):
   - `completed` - Student completed course
   - `planned` - Student planned course
   - `has_plan` - Student has semester plan
   - `includes_course` - Plan includes course
   - `preparing_for` - Student preparing for exam
   - `using_resource` - Prep session using resource
   - `prerequisite_of` - Course is prerequisite of another
   - `studied` - Student studied in session

4. **Observation Format**:
   - Use key-value format: `"key: value"`
   - Use ISO dates: `"date: 2025-10-14"`
   - Use arrays: `"courses: [IT6001, IT6002]"`
   - Add timestamps: `"updated: 2025-10-14T10:30:00"`

### Integration Strategy

**On Student First Contact**:
```typescript
// Create student entity
create_entities([{
  name: "Student_123456",
  entityType: "student",
  observations: [
    "name: Nguyen Van A",
    "student_id: 123456",
    "program: Information Technology",
    "enrollment_year: 2023",
    "current_semester: 3",
    "first_contact: 2025-10-14"
  ]
}])
```

**On Course Planning**:
```typescript
// Store plan
create_entities([{
  name: "Plan_Semester4_Student123456",
  entityType: "semester_plan",
  observations: [
    "created: 2025-10-14",
    "semester: 4",
    "courses: [IT6002, IT6015, BS6003]",
    "total_credits: 18",
    "strategy: ON-TRACK"
  ]
}])

// Link to student
create_relations([{
  from: "Student_123456",
  to: "Plan_Semester4_Student123456",
  relationType: "has_plan"
}])

// Record completed courses
create_relations([
  {from: "Student_123456", to: "IT6001", relationType: "completed"},
  {from: "Student_123456", to: "BS6001", relationType: "completed"}
])
```

**On Exam Preparation**:
```typescript
// Track preparation
create_entities([{
  name: "ExamPrep_IT6002_Student123456",
  entityType: "assessment_preparation",
  observations: [
    "course: IT6002",
    "start_date: 2025-10-01",
    "exam_date: 2025-10-30",
    "total_hours: 30",
    "completed_hours: 18",
    "weak_areas: [Trees, Graphs]"
  ]
}])

// Add study sessions
add_observations({
  entityName: "ExamPrep_IT6002_Student123456",
  contents: [
    "session_2025-10-14: Studied Binary Trees (3h)",
    "session_2025-10-15: Practice problems (2h)"
  ]
})
```

**Query Student Context**:
```typescript
// Get all student info
open_nodes({names: ["Student_123456"]})

// Search for student's plans
search_nodes({query: "Plan_Semester Student123456"})

// Get exam preparations
search_nodes({query: "ExamPrep Student123456"})
```

### Strengths
- ✅ Official MCP implementation
- ✅ Persistent storage across sessions
- ✅ Graph structure for complex relationships
- ✅ Simple JSON format
- ✅ Search and query capabilities

### Limitations
- ❌ File-based (not suitable for high concurrency)
- ❌ No built-in data validation
- ❌ Manual schema management
- ❌ Limited query capabilities (no complex graph traversal)

---

## Summary Table

| Feature | Course Scheduler | Course Detail | Memory Server |
|---------|------------------|---------------|---------------|
| **Primary Function** | Semester planning | Course info & exam prep | Data persistence |
| **Tools Count** | 9 | 5 | 9 |
| **Key Tool** | suggest_courses | get_assessment_blueprint | read_graph |
| **Data Focus** | Future planning | Current learning | Historical context |
| **User Interaction** | Recommendations | Information delivery | Background storage |
| **Complexity** | High (algorithms) | Medium (curation) | Low (CRUD) |
| **Session State** | Stateless | Stateless | Stateful (persistent) |
| **Integration** | Uses Memory | Uses Memory | Used by both |

## Tool Usage Hierarchy

```
User Request
    │
    ├─→ "What courses should I take next semester?"
    │       └─→ Course Scheduler Agent
    │               ├─→ initialize_scheduler()
    │               ├─→ suggest_courses()
    │               └─→ Memory: create_entities(semester_plan)
    │
    ├─→ "How do I prepare for IT6002 exam?"
    │       └─→ Course Detail Agent
    │               ├─→ initialize_catalog()
    │               ├─→ get_course_detail()
    │               ├─→ get_assessment_blueprint()
    │               ├─→ search_learning_resources()
    │               └─→ Memory: create_entities(exam_prep)
    │
    └─→ "What did we discuss last time?"
            └─→ Memory Server
                    ├─→ search_nodes(student)
                    └─→ read_graph()
```

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-14  
**Maintained by**: HaUI Agent Development Team
