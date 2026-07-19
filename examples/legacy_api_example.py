"""Legacy FastAPI demo kept for migration reference only.

This file is intentionally outside the production blockchain module. The
production integration should use ``blockchain_client.BlockchainClient`` and
keep authentication, officer identity mapping, watermarking, image storage, and
database state in the backend system.
"""

from fastapi import FastAPI

app = FastAPI(title="Legacy Evidence API Example")


@app.get("/")
def read_root() -> dict[str, str]:
    """Return a legacy demo marker."""

    return {
        "message": "Legacy demo only. Use blockchain_client for production integration.",
    }
