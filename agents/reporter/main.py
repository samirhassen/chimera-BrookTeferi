from fastapi import FastAPI
import httpx
import os
import uvicorn

app = FastAPI(title="Report Generator Agent")
ORCHESTRATOR = os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8080")
ANALYZER_URL = os.getenv("ANALYZER_URL", "http://agent_analyzer:5002")
AGENT_PORT = int(os.getenv("REPORTER_PORT", os.getenv("PORT", "5003")))
AGENT_ENDPOINT = os.getenv("REPORTER_URL", f"http://agent_reporter:{AGENT_PORT}")


@app.on_event("startup")
async def register():
    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"{ORCHESTRATOR}/register", json={"agent_name": "report_gen","endpoint": AGENT_ENDPOINT,"tools": [{"name": "report", "description": "generate executive summary and visual"}]
                                                                })
        except Exception:
            pass


@app.post("/tool/report")
async def report(payload: dict):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(f"{ANALYZER_URL}/tool/analyze", json={}, timeout=10.0)
            analysis = r.json()
        except Exception:
            analysis = {"warnings": 0, "critical": 0}


    warnings = analysis.get("warnings", 0)
    critical = analysis.get("critical", 0)
    summary = f"Executive summary: {critical} critical, {warnings} warnings"
    visual = "(" + ("█" * (critical + 1)) + ("▇" * (warnings + 1)) + ")"
    return {"summary": summary, "visual_asset": visual, "analysis": analysis}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=AGENT_PORT)

