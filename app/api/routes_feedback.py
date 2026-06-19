"""POST /feedback — officer/supervisor feedback feeds the eval set (docs/06)."""
from __future__ import annotations

import json
import os
import time

from fastapi import APIRouter, Header

from app.middleware.auth import authenticate
from app.schemas import FeedbackRequest

router = APIRouter()
_PATH = os.environ.get("FEEDBACK_PATH", "data/feedback/feedback.jsonl")


@router.post("/feedback")
def feedback(req: FeedbackRequest, authorization: str | None = Header(default=None)) -> dict:
    principal = authenticate(authorization)
    os.makedirs(os.path.dirname(_PATH), exist_ok=True)
    with open(_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "request_id": req.request_id, "helpful": req.helpful,
            "note": req.note, "user": principal.user, "ts": time.time(),
        }) + "\n")
    return {"recorded": True}
