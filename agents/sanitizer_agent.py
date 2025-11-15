from fastapi import FastAPI
import httpx
import os


app = FastAPI(title="Sanitizer Agent")
ORCHESTRATOR = os.getenv("ORCHESTRATOR_URL", "http://localhost:5000")


@app.on_event("startup")
async def register():
    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"{ORCHESTRATOR}/register", json={"agent_name": "sanitizer","endpoint": "http://localhost:6001","tools": [{"name": "sanitize", "description": "remove sensitive identifiers"}]
            })
        except Exception:
            # best-effort registration
            pass


@app.post("/tool/sanitize")
async def sanitize(payload: dict):
    # payload may include `text`; otherwise use deterministic mock input
    text = payload.get("text", "error: PII user=PII details=PII\nwarn: PII")
    # naive mock replacement
    replaced = text.count("PII")
    if replaced == 0:
        replaced = 3
        sanitized = text
        # if there are no explicit tokens, craft a sanitized sample
        sanitized = text.replace("PII", "[REDACTED]")
    else:
        sanitized = text.replace("PII", "[REDACTED]")


    return {"sanitized_text": sanitized, "replaced_identifiers": replaced}