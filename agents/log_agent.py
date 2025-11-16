from fastapi import FastAPI
import httpx
import os


app = FastAPI(title="Log Analyst Agent")
ORCHESTRATOR = os.getenv("ORCHESTRATOR_URL", "http://localhost:5000")
SANITIZER_URL = os.getenv("SANITIZER_URL", "http://localhost:6001")


@app.on_event("startup")
async def register():
    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"{ORCHESTRATOR}/register", json={"agent_name": "log_analyst","endpoint": "http://localhost:6002",
                                                            "tools": [{"name": "analyze", "description": "analyze sanitized logs"}]
                                                            })
        except Exception:
            pass


@app.post("/tool/analyze")
async def analyze(payload: dict):
    raw_logs = payload.get("text", "error: PII user=PII details=PII\nwarn: PII")
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(f"{SANITIZER_URL}/tool/sanitize", json={"text": raw_logs}, timeout=10.0)
            sanitized = r.json()
        except Exception:
            sanitized = {"sanitized_text": raw_logs, "replaced_identifiers": 0}


        sanitized_text = sanitized.get("sanitized_text", "")
        warnings = sanitized_text.lower().count("warn")
        critical = sanitized_text.lower().count("error")


        return {
            "sanitized_info": sanitized,
            "warnings": warnings,
            "critical": critical
            }