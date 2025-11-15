import os
import pytest
import httpx


@pytest.mark.asyncio
async def test_agents_endpoint_available():
    orchestrator_url = os.getenv("ORCHESTRATOR_URL", "http://localhost:8080")
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{orchestrator_url}/agents")
        assert r.status_code == 200