# 🎓 HaUI Agent System

**Intelligent Multi-Agent Academic Support System for Hanoi University of Industry**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-green.svg)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

## 🌟 Overview

HaUI Agent System is a sophisticated multi-agent AI architecture that provides comprehensive academic support to students through intelligent course planning, exam preparation, and progress tracking. Built on the Model Context Protocol (MCP), it orchestrates three specialized agents with persistent memory for seamless, personalized guidance.

### Key Features

- 🎯 **Intelligent Course Planning** - Optimal semester schedules with credit balancing
- 📚 **Comprehensive Course Information** - Detailed specs with prerequisite checking
- 📝 **Exam Preparation** - Assessment blueprints with study plans and resources
- 💾 **Persistent Memory** - Knowledge graph for context across sessions
- 🤖 **Multi-Agent Coordination** - Orchestrator routes requests to specialists
- 🌐 **Bilingual Support** - Seamless Vietnamese and English

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                       │
│          (Intent Recognition & Coordination)                │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
    ┌────────▼───────┐          ┌────────▼──────────┐
    │   Course       │          │   Course Detail   │
    │  Scheduler     │          │      Agent        │
    │   Agent        │          │                   │
    │  (9 tools)     │          │    (5 tools)      │
    └────────┬───────┘          └────────┬──────────┘
             │                            │
             └──────────┬─────────────────┘
                        │
              ┌─────────▼──────────┐
              │   Memory Server    │
              │ (Knowledge Graph)  │
              │    (9 tools)       │
              └────────────────────┘
```

### Components

| Component | Role | Tools | Key Capability |
|-----------|------|-------|----------------|
| **Orchestrator** | Main coordinator | N/A | Intent routing, response synthesis |
| **Course Scheduler** | Planning specialist | 9 | Optimal course selection with algorithms |
| **Course Detail** | Information specialist | 5 | Assessment blueprints & resources |
| **Memory Server** | Data persistence | 9 | Knowledge graph with relations |

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.11+
python --version

# Node.js 18+ (for Memory Server)
node --version
```

### Installation

```bash
# Clone repository
git clone https://github.com/tngphmvan/HaUI-Agent.git
cd HaUI-Agent

# Install Course Scheduler
cd mcp_course_scheduler
pip install -r requirements.txt

# Install Course Detail
cd ../mcp_course_detail
pip install mcp pydantic

# Install Memory Server
npm install -g @modelcontextprotocol/server-memory
```

### Configuration

**For Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json` on Mac or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "course-scheduler": {
      "command": "python",
      "args": ["D:\\HaUI-Agent\\mcp_course_scheduler\\server_fastmcp.py"],
      "env": {"PYTHONIOENCODING": "utf-8"}
    },
    "course-detail": {
      "command": "python",
      "args": ["D:\\HaUI-Agent\\mcp_course_detail\\server.py"],
      "env": {"PYTHONIOENCODING": "utf-8"}
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {"MEMORY_FILE_PATH": "D:\\HaUI-Agent\\student_memory.json"}
    }
  }
}
```

### Basic Usage

**Load Orchestrator Prompt** in your AI assistant:
```
Use the content from ORCHESTRATOR_PROMPT.md as your system prompt
```

**Example Conversations**:

```
User: "Kỳ sau tôi nên đăng ký môn gì?"
→ Orchestrator routes to Course Scheduler
→ Returns optimal course recommendations

User: "Làm sao để chuẩn bị thi IT6002?"
→ Orchestrator routes to Course Detail
→ Returns assessment blueprint + resources

User: "Tôi đã học được bao nhiêu tín chỉ?"
→ Orchestrator queries Memory + Course Scheduler
→ Returns progress report with insights
```

## 📚 Documentation

- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Complete system setup and workflows
- **[ORCHESTRATOR_PROMPT.md](ORCHESTRATOR_PROMPT.md)** - Main orchestrator agent prompt
- **[AGENT_DESCRIPTIONS.md](AGENT_DESCRIPTIONS.md)** - Detailed tool catalog for all agents
- **[mcp_course_scheduler/prompt.md](mcp_course_scheduler/prompt.md)** - Scheduler agent specific prompt
- **[mcp_course_detail/prompt.md](mcp_course_detail/prompt.md)** - Detail agent specific prompt

## 🎯 Use Cases

### 1. Semester Planning
**Goal**: Get optimal course recommendations for next semester

**Workflow**:
```
1. System retrieves completed courses from Memory
2. Course Scheduler suggests courses based on:
   - Prerequisites satisfaction
   - Credit limits (11-27)
   - Student priorities
   - Planning strategy (CATCH-UP/ON-TRACK/ADVANCED)
3. System stores plan in Memory
4. Presents recommendations with rationale
```

**Example Output**:
```markdown
## 📚 Semester 4 Recommendations (18 credits)

| Code   | Name                        | Credits | Prerequisites | Ready |
|--------|-----------------------------|---------|---------------|-------|
| IT6002 | Data Structures             | 3       | IT6001        | ✅    |
| IT6015 | Programming Techniques      | 3       | IT6001        | ✅    |
| BS6003 | Discrete Mathematics        | 3       | BS6001        | ✅    |
| ...    | ...                         | ...     | ...           | ...   |

**Strategy**: ON-TRACK (balanced load for timely graduation)
**Total**: 18 credits (3 mandatory, 1 elective)
```

### 2. Exam Preparation
**Goal**: Get comprehensive exam study plan with resources

**Workflow**:
```
1. Course Detail generates assessment blueprint:
   - Foundation topics (15%)
   - Core concepts (50%)
   - Applied skills (35%)
2. Curates learning resources (web + non-web)
3. Creates time-boxed study plan
4. Stores exam prep tracking in Memory
```

**Example Output**:
```markdown
## 📝 IT6002 Exam Preparation Plan

### Assessment Blueprint

**Core Concepts (50%)** - Medium to Hard difficulty
- Trees & Heaps (20%)
- Graphs (20%)
- Sorting Algorithms (10%)

**Study Plan** (30 hours estimated)
- Week 1-2: Foundation review (6h)
- Week 3-5: Core concepts (15h)
- Week 6-8: Practice problems (9h)

### 📖 Learning Resources

**Official Sources** (Credibility: 1.0)
- Course Syllabus - [Link]
- Lecture Slides - LMS

**Textbooks** (Credibility: 0.95)
- Introduction to Algorithms - Cormen et al.
```

### 3. Progress Tracking
**Goal**: Monitor academic progress and graduation timeline

**Workflow**:
```
1. Memory retrieves all completed courses
2. Course Scheduler calculates remaining credits
3. Analyzes pace vs. standard timeline
4. Provides insights and projections
```

**Example Output**:
```markdown
## 📊 Academic Progress Report

✅ **Completed**: 45 / 120 credits (37.5%)
📈 **Pace**: On track (15 credits/semester avg)
🎯 **Current**: Semester 3 / 8
🎓 **Projected Graduation**: June 2026

### Pace Analysis
- Standard pace: 15 TC/semester
- Your pace: 15 TC/semester
- Status: **Right on track!** ✅
```

## 🛠️ Advanced Features

### Fuzzy Course Name Matching
Supports Vietnamese course names with typos or variations:
```
"Cau truc du lieu" → "Cấu trúc dữ liệu và giải thuật" (IT6002)
```

### Multiple Planning Strategies
- **CATCH-UP**: Maximize credits to catch up
- **PRIORITY**: Focus on specific courses
- **ON-TRACK**: Balanced standard load
- **ADVANCED**: Challenge mode for high achievers

### Strict Credit Enforcement
Iteratively adds/removes courses to meet exact credit targets within 11-27 range.

### Prerequisite Validation
Automatic checking and bridging path generation for unmet requirements.

### Credibility Scoring
Learning resources rated 0-1 scale:
- 1.0: Official university sources
- 0.9-0.95: Academic textbooks
- 0.7-0.8: Educational videos
- 0.6-0.7: Community content

## 📊 System Specifications

### Performance Targets
- Single-agent query: <3s
- Multi-agent workflow: <5s
- Memory operations: <500ms

### Resource Usage
- Course Scheduler: ~100MB RAM
- Course Detail: ~50MB RAM
- Memory Server: ~30MB RAM
- **Total**: ~200MB RAM

### Data Storage
- Memory: JSON file (~1MB for 100 students)
- Curriculum: JSON (~500KB)
- Logs: Optional (configurable)

## 🧪 Testing

### Unit Tests
```bash
# Test Course Scheduler
cd mcp_course_scheduler
python test_mcp_server.py

# Test Course Detail
cd mcp_course_detail
python test_standalone.py
```

### Integration Test
```bash
python test_integration.py
```

### Manual Testing with MCP Inspector
```bash
# Test Course Scheduler
npx @modelcontextprotocol/inspector python mcp_course_scheduler/server_fastmcp.py

# Test Course Detail
npx @modelcontextprotocol/inspector python mcp_course_detail/server.py

# Test Memory
npx @modelcontextprotocol/inspector npx -y @modelcontextprotocol/server-memory
```

## 🔧 Development

### Project Structure
```
HaUI-Agent/
├── mcp_course_scheduler/         # Course planning agent
│   ├── server_fastmcp.py         # MCP server
│   ├── course_scheduler.py       # Algorithm logic
│   ├── models.py                 # Data models
│   ├── prompt.md                 # Agent prompt
│   └── requirements.txt
├── mcp_course_detail/            # Course information agent
│   ├── server.py                 # MCP server
│   ├── prompt.md                 # Agent prompt
│   ├── test_standalone.py        # Tests
│   └── README.md
├── ORCHESTRATOR_PROMPT.md        # Main orchestrator
├── AGENT_DESCRIPTIONS.md         # Tool catalog
├── INTEGRATION_GUIDE.md          # Setup guide
├── README.md                     # This file
├── student_memory.json           # Persistent storage
└── khung ctrinh cntt.json        # Curriculum data
```

### Adding New Features

1. **New Tool in Existing Agent**:
   - Add tool function in agent's `server.py`
   - Update `AGENT_DESCRIPTIONS.md`
   - Update `ORCHESTRATOR_PROMPT.md` workflows
   - Add tests

2. **New Agent**:
   - Create new folder `mcp_new_agent/`
   - Implement MCP server
   - Add to `AGENT_DESCRIPTIONS.md`
   - Update `ORCHESTRATOR_PROMPT.md`
   - Update configuration files

3. **New Workflow**:
   - Define in `ORCHESTRATOR_PROMPT.md`
   - Add examples
   - Document in `INTEGRATION_GUIDE.md`

## 📈 Roadmap

### ✅ Phase 1: Core Features (Completed)
- Course Scheduler with 9 tools
- Course Detail with 5 tools
- Memory Server integration
- Orchestrator coordination
- Comprehensive documentation

### 🔄 Phase 2: Enhancements (In Progress)
- Multi-program support (not just IT)
- Real-time course availability
- LLM-powered semantic search
- Web search API integration

### 📋 Phase 3: Advanced (Planned)
- Course conflict detection (time clashes)
- GPA prediction
- Personalized learning paths
- Study group formation
- Professor ratings

### 🎯 Phase 4: Production (Future)
- REST API gateway
- User authentication
- Multi-tenant support
- Analytics dashboard
- Mobile app

## 🤝 Contributing

We welcome contributions! Please see our guidelines:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Standards
- Python: PEP 8
- Docstrings: Google style
- Type hints: Required
- Tests: Required for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

**HaUI Agent Development Team**
- Lead Developer: [Your Name]
- Contributors: See [CONTRIBUTORS.md](CONTRIBUTORS.md)

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io) - For the MCP framework
- [Anthropic](https://anthropic.com) - For Claude and MCP specification
- [Hanoi University of Industry](https://haui.edu.vn) - For academic support and data
- Community contributors - For feedback and improvements

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/tngphmvan/HaUI-Agent/issues)
- **Email**: support@haui-agent.edu.vn
- **Documentation**: [Full Docs](docs/)
- **Discord**: [Join our community](https://discord.gg/haui-agent)

## 📊 Statistics

![GitHub stars](https://img.shields.io/github/stars/tngphmvan/HaUI-Agent?style=social)
![GitHub forks](https://img.shields.io/github/forks/tngphmvan/HaUI-Agent?style=social)
![GitHub issues](https://img.shields.io/github/issues/tngphmvan/HaUI-Agent)
![GitHub pull requests](https://img.shields.io/github/issues-pr/tngphmvan/HaUI-Agent)

---

**Made with ❤️ for HaUI students | Version 1.0.0 | Last Updated: 2025-10-14**
"# Luyen-AIO" 
