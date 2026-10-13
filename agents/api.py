"""
FastAPI REST API Server for Tnm8 Breast Staging Calculator.
"""
import os
import hmac
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor
from staging import anatomic_stage

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Tnm8 Breast Staging Calculator API",
    description="Anatomic staging reference plus legacy experimental auditing endpoints",
    version="1.0.0",
)

# Security: restrict trusted hosts (configurable via env)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[s.strip() for s in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",") if s.strip()],
)


class StageRequest(BaseModel):
    t: str = Field(..., min_length=2, max_length=10)
    n: str = Field(..., min_length=2, max_length=10)
    m: str = Field(..., min_length=2, max_length=10)


@app.post("/api/stage")
def api_stage(request: StageRequest):
    try:
        return anatomic_stage(request.t, request.n, request.m)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Supervisory query string")


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "tnm8-breast-staging-calculator", "domain": "Clinical & Biomedical AI", "standard": "CAP / CLSI / ISO Standards", "version": "1.0.0"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "AVAILABLE"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
        return dossier.to_dict()
    except SecurityException as e:
        raise HTTPException(status_code=400, detail=f"Security violation: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException as e:
        raise HTTPException(status_code=400, detail=f"Security violation: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/audit/logs")
def api_audit_logs(x_admin_token: str | None = Header(default=None)):
    expected = os.getenv("API_ADMIN_TOKEN")
    if not expected or not x_admin_token or not hmac.compare_digest(x_admin_token, expected):
        raise HTTPException(status_code=403, detail="Audit logs require an API admin token")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
