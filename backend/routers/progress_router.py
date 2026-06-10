from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import get_db
from services.auth_service import decode_jwt
from models import User, StudyLog
from services.progress_service import get_or_create_progress, mark_study_activity, progress_payload

router = APIRouter(redirect_slashes=False)

def require_auth(request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "): return None
    data = decode_jwt(auth[7:])
    if not data: return None
    return db.query(User).filter(User.id == data["user_id"]).first()

@router.get("", include_in_schema=False)
@router.get("/")
def get_progress(user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user: return {"ok": False, "error": "Unauthorized"}
    p = get_or_create_progress(db, user.id)
    db.commit()
    db.refresh(p)
    return {"ok": True, "data": progress_payload(p)}

class StudyLogReq(BaseModel):
    duration_minutes: int
    topic: str | None = None
    section: str | None = None
    notes: str | None = None

@router.post("/study-log")
def log_study(req: StudyLogReq, user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user: return {"ok": False, "error": "Unauthorized"}
    log = StudyLog(user_id=user.id, duration_minutes=req.duration_minutes, topic=req.topic, section=req.section, notes=req.notes)
    db.add(log)

    p = mark_study_activity(db, user.id, duration_minutes=req.duration_minutes)
    db.commit()
    db.refresh(p)
    return {"ok": True, "message": "Study log ditambahkan", "progress": progress_payload(p)}

@router.get("/charts")
def charts(user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user: return {"ok": False, "error": "Unauthorized"}
    from sqlalchemy import func
    logs = db.query(
        func.date(StudyLog.created_at).label("day"),
        func.sum(StudyLog.duration_minutes).label("minutes")
    ).filter(StudyLog.user_id == user.id).group_by(func.date(StudyLog.created_at)).order_by(func.date(StudyLog.created_at).desc()).limit(14).all()
    return {"ok": True, "data": [{"date": str(l.day), "minutes": int(l.minutes or 0)} for l in reversed(logs)]}
