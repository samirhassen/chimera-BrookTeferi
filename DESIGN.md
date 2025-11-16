# Project Chimera - Design Document

## Architecture Overview

Project Chimera implements a multi-agent orchestration system inspired by the Model Context Protocol (MCP). The system consists of a central orchestrator that coordinates multiple autonomous agents, each with specialized capabilities.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Orchestrator                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Planner    │  │   Registry   │  │  Aggregator │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                │                    │            │
└─────────┼────────────────┼────────────────────┼────────────┘
          │                │                    │
          │                │                    │
    ┌─────▼─────┐    ┌─────▼─────┐      ┌─────▼─────┐
    │ Sanitizer │    │   Log     │      │  Report   │
    │   Agent   │◄───│  Analyst  │◄─────│ Generator │
    │           │    │   Agent   │      │   Agent   │
    └───────────┘    └───────────┘      └───────────┘
```


system design :- 
   - https://app.eraser.io/workspace/dYxFpl59t9ieFPRfWVyZ?origin=share


## Component Details

### 1. MCP Orchestrator

**Purpose**: Central coordination hub that plans, dispatches, and aggregates agent work.

**Components**:
- **Planner**: Interprets natural-language instructions and determines which agents to invoke
- **Registry**: Maintains a thread-safe registry of available agents and their capabilities
- **Aggregator**: Collects results from agents and formats them into a cohesive output

**Key Features**:
- RESTful API for receiving instructions
- Agent self-registration endpoint
- Sequential task execution with error handling
- Human-readable output formatting

**Technology**: FastAPI (Python), httpx for agent communication

### 2. Agent Services

#### Sanitizer Agent
- **Role**: Data sanitization and PII removal
- **Tool**: `sanitize` - Removes sensitive identifiers from text
- **Port**: 5001
- **Dependencies**: None (base agent)

#### Log Analyst Agent
- **Role**: Log analysis and error detection
- **Tool**: `analyze` - Analyzes sanitized logs for warnings and critical errors
- **Port**: 5002
- **Dependencies**: Calls Sanitizer Agent directly to clean logs before analysis
- **Environment**: `SANITIZER_URL` - URL of sanitizer service

#### Report Generator Agent
- **Role**: Executive summary and visualization
- **Tool**: `report` - Generates summaries and visual assets from analysis
- **Port**: 5003
- **Dependencies**: Calls Log Analyst Agent directly to get analysis data
- **Environment**: `ANALYZER_URL` - URL of analyzer service

## Communication Strategy

### Agent-to-Orchestrator Communication

1. **Registration**: Agents POST to `/register` on startup with their metadata:
   ```json
   {
     "agent_name": "sanitizer",
     "endpoint": "http://agent_sanitizer:5001",
     "tools": [{"name": "sanitize", "description": "..."}]
   }
   ```

2. **Task Execution**: Orchestrator POSTs to agent endpoints (`/tool/{tool_name}`) with task payloads

### Agent-to-Agent Communication

Agents communicate directly with each other using HTTP REST calls:
- **Log Analyst → Sanitizer**: Calls `/tool/sanitize` to clean logs before analysis
- **Report Generator → Log Analyst**: Calls `/tool/analyze` to get analysis results

This demonstrates **inter-agent collaboration** without requiring the orchestrator to pass data between agents.

### Communication Protocol

- **Protocol**: HTTP REST
- **Format**: JSON
- **Service Discovery**: Docker service names (in containerized environment) or localhost (local dev)
- **Error Handling**: Best-effort with graceful degradation

## Orchestration Flow

### Example: "Generate a project intelligence brief..."

1. **Instruction Received**
   ```
   User → POST /plan-and-run
   {
     "instruction": "Generate a project intelligence brief: analyze system logs for errors, 
                     but ensure all sensitive identifiers are sanitized before analysis, 
                     and then produce a summarized report with a visual asset"
   }
   ```

2. **Planning Phase**
   - Planner analyzes instruction keywords
   - Detects: "sanitized", "analyze", "report", "summary", "visual"
   - Determines flow: `["sanitizer", "log_analyst", "report_gen"]`

3. **Execution Phase**
   ```
   Orchestrator → Sanitizer Agent
   ├─ Sanitizer processes raw logs
   └─ Returns: {"sanitized_text": "...", "replaced_identifiers": 3}
   
   Orchestrator → Log Analyst Agent
   ├─ Log Analyst internally calls Sanitizer Agent
   ├─ Receives sanitized logs
   ├─ Analyzes for errors/warnings
   └─ Returns: {"warnings": 1, "critical": 1, "sanitized_info": {...}}
   
   Orchestrator → Report Generator Agent
   ├─ Report Generator internally calls Log Analyst Agent
   ├─ Receives analysis results
   ├─ Generates summary and visual
   └─ Returns: {"summary": "...", "visual_asset": "..."}
   ```

4. **Aggregation Phase**
   - Orchestrator collects all results
   - Formats into human-readable output
   - Returns structured JSON with both raw and formatted results

## Scaling Considerations

### Horizontal Scaling

- **Stateless Agents**: Each agent is stateless and can be horizontally scaled
- **Load Balancing**: Agents can be deployed behind load balancers
- **Service Discovery**: Use service mesh (e.g., Consul, Kubernetes services) for dynamic discovery

### Reliability

- **Retry Logic**: Implement exponential backoff for agent calls
- **Circuit Breakers**: Prevent cascading failures
- **Health Checks**: Monitor agent availability
- **Graceful Degradation**: Continue with available agents when some fail

### Performance

- **Parallel Execution**: When agents are independent, execute in parallel
- **Caching**: Cache agent results for idempotent operations
- **Async Processing**: Use message queues (RabbitMQ, Kafka) for long-running tasks

## Extension to Real AI Models

### LLM Integration

1. **Planner Enhancement**:
   - Replace rule-based planner with LLM (GPT-4, Claude, etc.)
   - Use function calling to determine agent selection
   - Generate execution plans based on agent capabilities

2. **Agent Enhancement**:
   - Each agent can use LLMs for their specific domain
   - Sanitizer: Use LLM to identify PII patterns
   - Log Analyst: Use LLM for intelligent log analysis
   - Report Generator: Use LLM for natural language summaries

3. **MCP Protocol**:
   - Implement full MCP specification
   - Support tool discovery and schema validation
   - Enable streaming responses for long-running tasks

### Architecture Evolution

```
Current: Rule-based → Future: LLM-powered
Current: REST APIs → Future: MCP Protocol + WebSockets
Current: Sequential → Future: Parallel + Dependency Graph
Current: In-memory Registry → Future: Distributed Service Discovery
```

## Technology Choices

### Why FastAPI?
- Modern async Python framework
- Automatic API documentation
- Type validation with Pydantic
- High performance

### Why Docker Compose?
- Easy local development
- Service isolation
- Network management
- Reproducible environments

### Why REST over gRPC/WebSockets?
- Simplicity for prototype
- Easy debugging
- Language agnostic
- Can evolve to WebSockets for streaming

## Security Considerations

### Current Prototype
- No authentication (development only)
- No encryption (internal network)
- Basic error handling

### Production Considerations
- **Authentication**: API keys, OAuth2, mTLS
- **Encryption**: TLS for all communications
- **Input Validation**: Strict schema validation
- **Rate Limiting**: Prevent abuse
- **Audit Logging**: Track all agent interactions

## Future Enhancements

1. **Advanced Planning**: LLM-based planning with dependency resolution
2. **Streaming**: Real-time result streaming as agents complete
3. **Agent Marketplace**: Dynamic agent discovery and capability negotiation
4. **Workflow Persistence**: Save and replay orchestration flows
5. **Monitoring**: Comprehensive observability (metrics, traces, logs)
6. **Multi-tenancy**: Support multiple users/organizations
7. **Agent Versioning**: Support multiple versions of agents
8. **Result Caching**: Cache intermediate results for efficiency

## Conclusion

Project Chimera demonstrates a working multi-agent orchestration system that:
- ✅ Coordinates multiple autonomous agents
- ✅ Plans based on natural language
- ✅ Enables inter-agent collaboration
- ✅ Aggregates results coherently
- ✅ Provides a foundation for scaling to production AI systems

The architecture is designed to be simple yet extensible, making it easy to replace components (e.g., rule-based planner → LLM) as requirements evolve.

