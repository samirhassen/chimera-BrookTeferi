import os
import uvicorn
from orchestrator import app

if __name__ == "__main__":
    port = int(os.getenv("ORCHESTRATOR_PORT", os.getenv("PORT", "8080")))
    uvicorn.run(app, host="0.0.0.0", port=port)

