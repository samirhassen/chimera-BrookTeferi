# Project Chimera - MCP Orchestrator

A prototype multi-agent orchestration system inspired by the Model Context Protocol (MCP). This system demonstrates how a central orchestrator can coordinate multiple autonomous agents to solve complex tasks through collaboration.

## Overview

Project Chimera implements a minimal working MCP-style orchestration server that:
- Coordinates multiple specialized agent services
- Plans actions based on natural-language instructions
- Manages agent self-registration
- Handles inter-agent communication
- Aggregates and formats results

## Architecture

The system consists of:
- **Orchestrator**: Central MCP server that plans and coordinates agent tasks
- **Sanitizer Agent**: Removes sensitive identifiers (PII) from data
- **Log Analyst Agent**: Analyzes logs for errors and warnings (calls Sanitizer)
- **Report Generator Agent**: Creates executive summaries and visual assets (calls Log Analyst)

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd chimera
   ```

2. **Start all services**:
   ```bash
   docker-compose up --build
   ```

   This will start:
   - Orchestrator on `http://localhost:8080`
   - Sanitizer Agent on `http://localhost:5001`
   - Log Analyst Agent on `http://localhost:5002`
   - Report Generator Agent on `http://localhost:5003`

   **Note**: Port configuration is available in `env.example`. Copy to `.env` for local development customization.

3. **Wait for services to start** (about 10-15 seconds for all agents to register)

4. **Test the system**:
   ```bash
   curl -X POST http://localhost:8080/plan-and-run \
     -H "Content-Type: application/json" \
     -d '{"instruction": "Generate a project intelligence brief: analyze system logs for errors, but ensure all sensitive identifiers are sanitized before analysis, and then produce a summarized report with a visual asset"}'
   ```

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the orchestrator**:
   ```bash
   cd orchestrator
   python main.py
   ```

3. **Start each agent** (in separate terminals):
   ```bash
   # Terminal 2
   cd agents/sanitizer
   python main.py

   # Terminal 3
   cd agents/analyzer
   python main.py

   # Terminal 4
   cd agents/reporter
   python main.py
   ```

## API Endpoints

### Orchestrator (`http://localhost:8080`)

- `POST /register` - Agent self-registration
  ```json
  {
    "agent_name": "sanitizer",
    "endpoint": "http://agent_sanitizer:5001",
    "tools": [{"name": "sanitize", "description": "remove sensitive identifiers"}]
  }
  ```

- `GET /agents` - List all registered agents

- `POST /plan-and-run` - Execute orchestration flow
  ```json
  {
    "instruction": "analyze logs and generate a report"
  }
  ```

### Agent Endpoints

Each agent exposes:
- `POST /tool/{tool_name}` - Execute agent tool

## Example Usage

### Example Request

```bash
curl -X POST http://localhost:8080/plan-and-run \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Generate a project intelligence brief: analyze system logs for errors, but ensure all sensitive identifiers are sanitized before analysis, and then produce a summarized report with a visual asset"
  }'
```

### Example Response

```json
{
  "instruction": "Generate a project intelligence brief...",
  "flow": ["sanitizer", "log_analyst", "report_gen"],
  "results": {
    "sanitizer": {
      "sanitized_text": "error: [REDACTED] user=[REDACTED] details=[REDACTED]\nwarn: [REDACTED]",
      "replaced_identifiers": 3
    },
    "log_analyst": {
      "sanitized_info": {
        "sanitized_text": "error: [REDACTED] user=[REDACTED] details=[REDACTED]\nwarn: [REDACTED]",
        "replaced_identifiers": 3
      },
      "warnings": 1,
      "critical": 1
    },
    "report_gen": {
      "summary": "Executive summary: 1 critical, 1 warnings",
      "visual_asset": "(████▇▇)",
      "analysis": {
        "warnings": 1,
        "critical": 1
      }
    }
  },
  "formatted_output": "=== Project Chimera Results ===\nAgent 1 (Sanitizer) → Sanitized logs: replaced 3 personal identifiers\nAgent 2 (Log Analyst) → Called Agent 1, analyzed sanitized logs: 1 warnings, 1 critical error\nAgent 3 (Report Generator) → Generated executive summary and visual asset from analysis\n   Summary: Executive summary: 1 critical, 1 warnings\n   Visual: (████▇▇)"
}
```

## System Flow

1. **Agent Registration**: Each agent self-registers with the orchestrator on startup
2. **Instruction Received**: User sends natural-language instruction to `/plan-and-run`
3. **Planning**: Orchestrator's planner analyzes the instruction and determines which agents to invoke
4. **Execution**: Orchestrator calls agents in sequence:
   - Sanitizer processes raw data
   - Log Analyst calls Sanitizer, then analyzes the cleaned data
   - Report Generator calls Log Analyst, then creates summary and visual
5. **Aggregation**: Orchestrator collects all results and formats them

## Key Features

- ✅ **Agent Self-Registration**: Agents automatically register on startup
- ✅ **Natural Language Planning**: Rule-based planner interprets instructions
- ✅ **Inter-Agent Communication**: Agents can call other agents directly
- ✅ **Dependency Management**: Orchestrator ensures proper execution order
- ✅ **Formatted Output**: Human-readable aggregated results

## Project Structure

```
chimera/
├── orchestrator/
│   ├── main.py              # Orchestrator entry point
│   ├── orchestrator.py      # FastAPI app and orchestration logic
│   ├── planner.py           # Rule-based planning component
│   ├── registry.py          # Agent registry
│   ├── Dockerfile
│   └── requirements.txt
├── agents/
│   ├── sanitizer/
│   │   ├── main.py          # Sanitizer agent
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── analyzer/
│   │   ├── main.py          # Log analyst agent
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── reporter/
│       ├── main.py          # Report generator agent
│       ├── Dockerfile
│       └── requirements.txt
├── docker-compose.yml       # Docker orchestration
├── requirements.txt         # Root dependencies
└── README.md
```

## Testing

After starting all services, verify they're running:

```bash
# Check orchestrator
curl http://localhost:8080/agents

# Test individual agents
curl -X POST http://localhost:5001/tool/sanitize \
  -H "Content-Type: application/json" \
  -d '{"text": "error: PII user=PII details=PII"}'
```

## Design Document

See [DESIGN.md](DESIGN.md) for detailed architecture documentation.

## Notes

- Agents use best-effort registration (failures are silently handled)
- The planner uses simple keyword matching (can be replaced with LLM)
- All communication uses REST APIs over HTTP
- Services communicate via Docker service names when containerized

