from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date, datetime
from db import get_db
from services.auth_service import decode_jwt
from models import User, Progress, StudyLog

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
    p = db.query(Progress).filter(Progress.user_id == user.id).first()
    if not p:
        p = Progress(user_id=user.id)
        db.add(p)
        db.commit()
        db.refresh(p)
    return {"ok": True, "data": {
        "study_days": p.study_days, "study_hours": float(p.study_hours or 0),
        "sim_count": p.sim_count, "current_week": p.current_week,
        "twk_score": float(p.twk_score or 0), "tiu_score": float(p.tiu_score or 0),
        "tkp_score": float(p.tkp_score or 0), "streak_days": p.streak_days,
        "last_study_date": str(p.last_study_date) if p.last_study_date else None
    }}

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

    p = db.query(Progress).filter(Progress.user_id == user.id).first()
    if p:
        p.study_hours = float(p.study_hours or 0) + req.duration_minutes / 60
        today = date.today()
        if p.last_study_date != today:
            p.study_days = (p.study_days or 0) + 1
            if p.last_study_date and (today - p.last_study_date).days == 1:
                p.streak_days = (p.streak_days or 0) + 1
            elif p.last_study_date and (today - p.last_study_date).days > 1:
                p.streak_days = 1
            p.last_study_date = today
    db.commit()
    return {"ok": True, "message": "Study log ditambahkan"}

@router.get("/charts")
def charts(user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user: return {"ok": False, "error": "Unauthorized"}
    from sqlalchemy import func
    logs = db.query(
        func.date(StudyLog.created_at).label("day"),
        func.sum(StudyLog.duration_minutes).label("minutes")
    ).filter(StudyLog.user_id == user.id).group_by(func.date(StudyLog.created_at)).order_by(func.date(StudyLog.created_at).desc()).limit(14).all()
    return {"ok": True, "data": [{"date": str(l.day), "minutes": int(l.minutes or 0)} for l in reversed(logs)]}
