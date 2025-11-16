from fastapi import FastAPI
import httpx
import os


app = FastAPI(title="Report Generator Agent")
ORCHESTRATOR = os.getenv("ORCHESTRATOR_URL", "http://localhost:5000")
LOG_ANALYST_URL = os.getenv("LOG_ANALYST_URL", "http://localhost:6002")


@app.on_event("startup")
async def register():
    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"{ORCHESTRATOR}/register", json={"agent_name": "report_gen","endpoint": "http://localhost:6003","tools": [{"name": "report", "description": "generate executive summary and visual"}]
                                                                })
        except Exception:
            pass


@app.post("/tool/report")
async def report(payload: dict):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(f"{LOG_ANALYST_URL}/tool/analyze", json={}, timeout=10.0)
            analysis = r.json()
        except Exception:
            analysis = {"warnings": 0, "critical": 0}


    warnings = analysis.get("warnings", 0)
    critical = analysis.get("critical", 0)
    summary = f"Executive summary: {critical} critical, {warnings} warnings"
    visual = "(" + ("█" * (critical + 1)) + ("▇" * (warnings + 1)) + ")"
    return {"summary": summary, "visual_asset": visual, "analysis": analysis}