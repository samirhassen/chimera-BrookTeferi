from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import httpx
from registry import AgentRegistry
from planner import plan_from_instruction


app = FastAPI(title="Project Chimera - MCP Orchestrator")
REG = AgentRegistry()


class AgentInfo(BaseModel):
    agent_name: str
    endpoint: str
    tools: list


class Instruction(BaseModel):
    instruction: str


@app.post("/register")
async def register_agent(agent: AgentInfo):
    REG.register(agent.agent_name, agent.dict())
    return {"status":"registered", "agent": agent.agent_name}


@app.get("/agents")
async def list_agents():
    return REG.all()


def format_agent_result(agent_name: str, result: Dict[str, Any]) -> str:
    """Format individual agent result into readable text."""
    agent_display_names = {
        "sanitizer": "Agent 1 (Sanitizer)",
        "log_analyst": "Agent 2 (Log Analyst)",
        "report_gen": "Agent 3 (Report Generator)"
    }
    display_name = agent_display_names.get(agent_name, agent_name)
    
    if "error" in result:
        return f"{display_name} → Error: {result['error']}"
    
    if agent_name == "sanitizer":
        replaced = result.get("replaced_identifiers", 0)
        return f"{display_name} → Sanitized logs: replaced {replaced} personal identifiers"
    
    elif agent_name == "log_analyst":
        sanitized_info = result.get("sanitized_info", {})
        replaced = sanitized_info.get("replaced_identifiers", 0)
        warnings = result.get("warnings", 0)
        critical = result.get("critical", 0)
        return f"{display_name} → Called Agent 1, analyzed sanitized logs: {warnings} warnings, {critical} critical error"
    
    elif agent_name == "report_gen":
        summary = result.get("summary", "No summary available")
        visual = result.get("visual_asset", "")
        return f"{display_name} → Generated executive summary and visual asset from analysis\n   Summary: {summary}\n   Visual: {visual}"
    
    return f"{display_name} → {result}"


@app.post("/plan-and-run")
async def plan_and_run(payload: Instruction):
    instruction = payload.instruction
    flow = plan_from_instruction(instruction)

    if not flow:
        raise HTTPException(status_code=400, detail="No matching agents found for instruction")


    results = {}
    async with httpx.AsyncClient() as client:
        for agent_name in flow:
            meta = REG.get(agent_name)
            if not meta:
                results[agent_name] = {"error":"agent-not-registered"}
                continue

            tool_path = {
                "sanitizer": "/tool/sanitize",
                "log_analyst": "/tool/analyze",
                "report_gen": "/tool/report"
                }.get(agent_name, "/tool")


            url = f"{meta['endpoint'].rstrip('/')}{tool_path}"
            try:
                r = await client.post(url, json={"instruction": instruction}, timeout=10.0)
                r.raise_for_status()
                results[agent_name] = r.json()
            except Exception as exc:
                results[agent_name] = {"error": str(exc)}


    # Format readable output
    formatted_output = ["=== Project Chimera Results ==="]
    for agent_name in flow:
        if agent_name in results:
            formatted_output.append(format_agent_result(agent_name, results[agent_name]))
    
    readable_output = "\n".join(formatted_output)
    
    aggregated = {
        "instruction": instruction,
        "flow": flow,
        "results": results,
        "formatted_output": readable_output
    }
    return aggregated