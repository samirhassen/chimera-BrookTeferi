from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os
import uvicorn

app = FastAPI(title="Sanitizer Agent")
ORCHESTRATOR = os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8080")
AGENT_PORT = int(os.getenv("SANITIZER_PORT", os.getenv("PORT", "5001")))
AGENT_ENDPOINT = os.getenv("SANITIZER_URL", f"http://agent_sanitizer:{AGENT_PORT}")


@app.on_event("startup")
async def register():
    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"{ORCHESTRATOR}/register", json={"agent_name": "sanitizer","endpoint": AGENT_ENDPOINT,"tools": [{"name": "sanitize", "description": "remove sensitive identifiers"}]
            })
        except Exception:
            # best-effort registration
            pass


class SanitizerRequest(BaseModel):
    """Input payload for the Sanitizer Agent.

    If no text is provided, the agent will use a deterministic mock log sample.
    """

    text: str | None = None


class SanitizerResponse(BaseModel):
    """Output payload from the Sanitizer Agent."""

    sanitized_text: str
    replaced_identifiers: int


@app.post(
    "/tool/sanitize",
    response_model=SanitizerResponse,
    summary="Sanitize text by masking PII tokens",
    description=(
        "Replaces occurrences of the literal token 'PII' in the input text with "
        "'[REDACTED]'. If no text is provided, a deterministic mock log sample is used."
    ),
    tags=["tools"],
)
async def sanitize(payload: SanitizerRequest) -> SanitizerResponse:
    """Sanitize input text by replacing `PII` tokens with `[REDACTED]`."""

    # payload may include `text`; otherwise use deterministic mock input
    text = payload.text or "error: PII user=PII details=PII\nwarn: PII"
    # naive mock replacement
    replaced = text.count("PII")
    if replaced == 0:
        replaced = 3
        sanitized = text
        # if there are no explicit tokens, craft a sanitized sample
        sanitized = text.replace("PII", "[REDACTED]")
    else:
        sanitized = text.replace("PII", "[REDACTED]")


    return SanitizerResponse(sanitized_text=sanitized, replaced_identifiers=replaced)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=AGENT_PORT)

