import hashlib
import re
import time
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from blockchain_service import (
    fetch_access_logs,
    get_evidence_details,
    log_access_to_blockchain,
    store_watermark_evidence,
)
from config import CORS_ORIGINS
from forensic_service import trace_officer_from_watermark


app = FastAPI(
    title="Police Evidence API",
    description="API for a blockchain-backed police digital evidence system.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{3,128}$")

# TODO: Replace with a persistent encrypted database/proxy table.
ACCESS_SESSION_MAP: dict[str, dict] = {}


class AccessRequest(BaseModel):
    officer_id: str = Field(..., min_length=3, max_length=128)
    purpose: str | None = Field(default=None, max_length=500)


def _validate_identifier(value: str, field_name: str) -> None:
    if not ID_PATTERN.fullmatch(value):
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} must be 3-128 chars using letters, numbers, _, ., :, or -.",
        )


def generate_access_hash(
    evidence_id: str,
    officer_id: str,
    access_session_id: str,
    timestamp: int,
) -> str:
    payload = f"{evidence_id}:{officer_id}:{access_session_id}:{timestamp}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@app.post("/api/v1/evidence/record")
async def record_evidence(
    evidence_id: str = Form(...),
    officer_id: str = Form(...),
    evidence_file: UploadFile = File(...),
):
    _validate_identifier(evidence_id, "evidence_id")
    _validate_identifier(officer_id, "officer_id")

    image_bytes = await evidence_file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="evidence_file is empty.")

    watermark_hash = hashlib.sha256(image_bytes).hexdigest()
    tx_hash = store_watermark_evidence(evidence_id, watermark_hash)
    if not tx_hash:
        raise HTTPException(status_code=400, detail="Unable to record evidence on blockchain.")

    # TODO: Store officer_id, evidence metadata, and tx_hash in backend database only.
    return {
        "status": "success",
        "evidence_id": evidence_id,
        "watermark_hash": watermark_hash,
        "tx_hash": tx_hash,
    }


@app.get("/api/v1/evidence/verify/{evidence_id}")
async def verify_evidence(evidence_id: str):
    _validate_identifier(evidence_id, "evidence_id")
    result = get_evidence_details(evidence_id)
    if not result:
        raise HTTPException(status_code=404, detail="Evidence ID not found on blockchain.")
    return {"status": "success", "data": result}


@app.post("/api/v1/evidence/{evidence_id}/access")
async def access_evidence(evidence_id: str, request: AccessRequest):
    _validate_identifier(evidence_id, "evidence_id")
    _validate_identifier(request.officer_id, "officer_id")

    timestamp = int(time.time())
    access_session_id = str(uuid4())
    access_hash = generate_access_hash(
        evidence_id,
        request.officer_id,
        access_session_id,
        timestamp,
    )
    tx_hash = log_access_to_blockchain(evidence_id, access_hash, access_session_id)
    if not tx_hash:
        raise HTTPException(status_code=400, detail="Unable to record access log on blockchain.")

    ACCESS_SESSION_MAP[access_session_id] = {
        "officer_id": request.officer_id,
        "evidence_id": evidence_id,
        "tx_hash": tx_hash,
        "timestamp": timestamp,
        "purpose": request.purpose,
    }

    return {
        "status": "success",
        "evidence_id": evidence_id,
        "access_session_id": access_session_id,
        "access_hash": access_hash,
        "tx_hash": tx_hash,
        "data": "แสดงรูปภาพพร้อมลายน้ำ Dynamic",
    }


@app.get("/api/v1/evidence/logs/{evidence_id}")
async def get_logs(evidence_id: str):
    _validate_identifier(evidence_id, "evidence_id")
    raw_logs = fetch_access_logs(evidence_id)
    history = []
    for log in raw_logs:
        history.append(
            {
                "access_hash": log[0],
                "access_session_id": log[1],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(log[2])),
            }
        )
    return {"evidence_id": evidence_id, "history": history}


@app.get("/api/v1/forensic/trace/{tx_hash}")
async def forensic_trace(tx_hash: str):
    result = trace_officer_from_watermark(tx_hash)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.get("/")
def read_root():
    return {"message": "Welcome to Police Evidence API. Go to /docs to see the API documentation."}
