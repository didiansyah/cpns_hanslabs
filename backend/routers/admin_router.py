import os
import time
from datetime import timedelta
from decimal import Decimal
from typing import Any

import httpx
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from db import get_db
from models import (
    Checklist,
    EmailOTP,
    Feedback,
    PasswordResetToken,
    Progress,
    Question,
    Simulation,
    StudyLog,
    TryoutPackage,
    User,
)
from routers.user_router import require_auth
from services.progress_service import today_jakarta

router = APIRouter(redirect_slashes=False)

DEFAULT_SUPERADMIN_EMAILS = {"didihansya@gmail.com", "thisishanslabs@gmail.com"}


def _admin_emails() -> set[str]:
    configured = os.getenv("SUPERADMIN_EMAILS", "")
    emails = {item.strip().lower() for item in configured.split(",") if item.strip()}
    return emails or DEFAULT_SUPERADMIN_EMAILS


def require_superadmin(user=Depends(require_auth)):
    if not user or user.email.lower() not in _admin_emails():
        return None
    return user


def _jsonable(value: Any):
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def user_payload(user: User, db: Session):
    progress = db.query(Progress).filter(Progress.user_id == user.id).first()
    sim_count = db.query(func.count(Simulation.id)).filter(Simulation.user_id == user.id).scalar() or 0
    last_sim = db.query(func.max(Simulation.created_at)).filter(Simulation.user_id == user.id).scalar()
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "education": user.education,
        "target_instansi": user.target_instansi,
        "previous_cpns": bool(user.previous_cpns),
        "verified": bool(user.verified),
        "created_at": _jsonable(user.created_at),
        "updated_at": _jsonable(user.updated_at),
        "is_superadmin": user.email.lower() in _admin_emails(),
        "sim_count": int(sim_count),
        "last_sim_at": _jsonable(last_sim) if last_sim else None,
        "study_days": int(progress.study_days or 0) if progress else 0,
        "streak_days": int(progress.streak_days or 0) if progress else 0,
    }


class UserUpdateReq(BaseModel):
    name: str | None = None
    phone: str | None = None
    education: str | None = None
    target_instansi: str | None = None
    verified: bool | None = None
    previous_cpns: bool | None = None


class QuestionReq(BaseModel):
    section: str = Field(..., min_length=2, max_length=3)
    topic: str = Field(..., min_length=1, max_length=100)
    year: int | None = None
    difficulty: str | None = None
    question_text: str = Field(..., min_length=5)
    options: list[Any] = Field(..., min_length=2)
    correct_answer: int | None = None
    explanation: str | None = None


class FeedbackStatusReq(BaseModel):
    status: str = Field(..., pattern="^(open|reviewed|resolved)$")


def feedback_payload(item: Feedback):
    user = getattr(item, "user", None)
    return {
        "id": item.id,
        "user_id": item.user_id,
        "user_name": user.name if user else None,
        "user_email": user.email if user else None,
        "category": item.category,
        "rating": item.rating,
        "message": item.message,
        "path": item.path,
        "status": item.status,
        "created_at": _jsonable(item.created_at),
        "updated_at": _jsonable(item.updated_at),
    }


def question_payload(q: Question):
    return {
        "id": q.id,
        "section": q.section,
        "topic": q.topic,
        "year": q.year,
        "difficulty": q.difficulty,
        "question_text": q.question_text,
        "options": q.options,
        "correct_answer": q.correct_answer,
        "explanation": q.explanation,
        "created_at": _jsonable(q.created_at),
    }


def fetch_umami_summary():
    base_url = os.getenv("UMAMI_URL", "http://127.0.0.1:3070").rstrip("/")
    username = os.getenv("UMAMI_USERNAME", "admin")
    password = os.getenv("UMAMI_PASSWORD", "umami")
    website_id = os.getenv("UMAMI_CPNS_WEBSITE_ID", "4f24bfee-341b-4779-82ce-7f6115291a2b")
    fallback = {
        "script_url": "/umami/script.js",
        "website_id": website_id,
        "collect_url": "/umami/api/send",
        "status": "tracking_enabled",
        "stats": {"pageviews": 0, "visitors": 0, "visits": 0, "bounces": 0, "totaltime": 0},
        "pageviews": [],
        "sessions": [],
    }
    try:
        end_at = int(time.time() * 1000)
        start_at = end_at - (7 * 24 * 60 * 60 * 1000)
        with httpx.Client(timeout=5.0) as client:
            login = client.post(f"{base_url}/api/auth/login", json={"username": username, "password": password})
            login.raise_for_status()
            token = login.json().get("token")
            headers = {"Authorization": f"Bearer {token}"}
            stats = client.get(f"{base_url}/api/websites/{website_id}/stats", params={"startAt": start_at, "endAt": end_at}, headers=headers)
            pageviews = client.get(f"{base_url}/api/websites/{website_id}/pageviews", params={"startAt": start_at, "endAt": end_at, "unit": "day", "timezone": "Asia/Jakarta"}, headers=headers)
            fallback["stats"] = stats.json() if stats.status_code == 200 else fallback["stats"]
            if pageviews.status_code == 200:
                payload = pageviews.json()
                fallback["pageviews"] = payload.get("pageviews", [])
                fallback["sessions"] = payload.get("sessions", [])
            fallback["status"] = "connected"
    except Exception:
        fallback["status"] = "tracking_enabled_stats_pending"
    return fallback


@router.get("/me")
def admin_me(admin=Depends(require_superadmin)):
    if not admin:
        return {"ok": False, "error": "Forbidden"}
    return {"ok": True, "data": {"id": admin.id, "email": admin.email, "name": admin.name}}


@router.get("/summary")
def summary(admin=Depends(require_superadmin), db: Session = Depends(get_db)):
    if not admin:
        return {"ok": False, "error": "Forbidden"}
    today = today_jakarta()
    seven_days_ago = today - timedelta(days=6)

    total_users = db.query(func.count(User.id)).scalar() or 0
    verified_users = db.query(func.count(User.id)).filter(User.verified == True).scalar() or 0  # noqa: E712
    total_questions = db.query(func.count(Question.id)).scalar() or 0
    total_simulations = db.query(func.count(Simulation.id)).scalar() or 0
    completed_simulations = db.query(func.count(Simulation.id)).filter(Simulation.submitted_at.isnot(None)).scalar() or 0
    study_logs = db.query(func.count(StudyLog.id)).scalar() or 0

    signups = db.execute(text("""
        SELECT DATE(created_at) AS day, COUNT(*) AS count
        FROM users
        WHERE DATE(created_at) >= :start
        GROUP BY DATE(created_at)
        ORDER BY day ASC
    """), {"start": seven_days_ago}).mappings().all()
    signup_map = {str(row["day"]): int(row["count"]) for row in signups}
    daily_signups = [
        {"date": str(seven_days_ago + timedelta(days=i)), "count": signup_map.get(str(seven_days_ago + timedelta(days=i)), 0)}
        for i in range(7)
    ]

    question_sections = db.query(Question.section, func.count(Question.id)).group_by(Question.section).all()
    recent_users = db.query(User).order_by(User.created_at.desc()).limit(8).all()
    recent_sims = db.query(Simulation).order_by(Simulation.created_at.desc()).limit(8).all()

    return {"ok": True, "data": {
        "stats": {
            "total_users": int(total_users),
            "verified_users": int(verified_users),
            "total_questions": int(total_questions),
            "total_simulations": int(total_simulations),
            "completed_simulations": int(completed_simulations),
            "study_logs": int(study_logs),
        },
        "daily_signups": daily_signups,
        "question_sections": [{"section": s or "-", "count": int(c)} for s, c in question_sections],
        "recent_users": [user_payload(u, db) for u in recent_users],
        "recent_simulations": [{
            "id": s.id,
            "user_id": s.user_id,
            "sim_type": s.sim_type,
            "total_score": s.total_score,
            "passed": bool(s.passed) if s.passed is not None else None,
            "created_at": _jsonable(s.created_at),
            "submitted_at": _jsonable(s.submitted_at) if s.submitted_at else None,
        } for s in recent_sims],
        "umami": fetch_umami_summary()
    }}


@router.get("/users")
def list_users(admin=Depends(require_superadmin), search: str = "", limit: int = Query(50, le=200), offset: int = 0, db: Session = Depends(get_db)):
    if not admin:
        return {"ok": False, "error": "Forbidden"}
    q = db.query(User)
    if search:
        needle = f"%{search.strip()}%"
        q = q.filter((User.name.like(needle)) | (User.email.like(needle)) | (User.phone.like(needle)))
    total = q.count()
    users = q.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    return {"ok": True, "data": {"total": total, "users": [user_payload(u, db) for u in users]}}


@router.put("/users/{user_id}")
def update_user(user_id: int, req: UserUpdateReq, admin=Depends(require_superadmin), db: Session = Depends(get_db)):
    if not admin:
        return {"ok": False, "error": "Forbidden"}
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"ok": False, "error": "User tidak ditemukan"}
    for key, value in req.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return {"ok": True, "data": user_payload(user, db)}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, admin=Depends(require_superadmin), db: Session = Depends(get_db)):
    if not admin:
        return {"ok": False, "error": "Forbidden"}
    if admin.id == user_id:
        return {"ok": False, "error": "Tidak bisa hapus akun superadmin yang sedang login"}
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"ok": False, "error": "User tidak ditemukan"}
    db.query(EmailOTP).filter(EmailOTP.email == user.email).delete(synchronize_session=False)
    db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user_id).delete(synchronize_session=False)
    db.query(Checklist).filter(Checklist.user_id == user_id).delete(synchronize_session=False)
    db.query(StudyLog).filter(StudyLog.user_id == user_id).delete(synchronize_session=False)
    db.query(Feedback).filter(Feedback.user_id == user_id).delete(synchronize_session=False)
    db.query(Progress).filter(Progress.user_id == user_id).delete(synchronize_session=False)
    db.query(Simulation).filter(Simulation.user_id == user_id).delete(synchronize_session=False)
    db.delete(user)
    db.commit()
    return {"ok": True, "message": "User dihapus"}


@router.get("/feedback")
@router.get("/feedback/")
def list_feedback(admin=Depends(require_superadmin), status: str = "", category: str = "", limit: int = Query(50, le=200), offset: int = 0, db: Session = Depends(get_db)):
    if not admin:
        return {"ok": False, "error": "Forbidden"}
    q = db.query(Feedback, User).join(User, Feedback.user_id == User.id)
    if status:
        q = q.filter(Feedback.status == status)
    if category:
        q = q.filter(Feedback.category == category)
    total = q.count()
    rows = q.order_by(Feedback.created_at.desc()).offset(offset).limit(limit).all()
    items = []
    for item, user in rows:
        payload = feedback_payload(item)
        payload["user_name"] = user.name
        payload["user_email"] = user.email
        items.append(payload)
    counts = dict(db.query(Feedback.status, func.count(Feedback.id)).group_by(Feedback.status).all())
    return {"ok": True, "data": {"total": total, "feedback": items, "counts": {k: int(v) for k, v in counts.items()}}}


@router.patch("/feedback/{feedback_id}")
@router.patch("/feedback/{feedback_id}/")
def update_feedback_status(feedback_id: int, req: FeedbackStatusReq, admin=Depends(require_superadmin), db: Session = Depends(get_db)):
    if not admin:
        return {"ok": False, "error": "Forbidden"}
    item = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not item:
        return {"ok": False, "error": "Feedback tidak ditemukan"}
    item.status = req.status
    db.commit()
    db.refresh(item)
    return {"ok": True, "data": feedback_payload(item)}


@router.get("/questions")
def admin_questions(admin=Depends(require_superadmin), search: str = "", section: str = "", limit: int = Query(50, le=200), offset: int = 0, db: Session = Depends(get_db)):
    if not admin:
        return {"ok": False, "error": "Forbidden"}
    q = db.query(Question)
    if section:
        q = q.filter(Question.section == section.upper())
    if search:
        needle = f"%{search.strip()}%"
        q = q.filter((Question.question_text.like(needle)) | (Question.topic.like(needle)) | (Question.explanation.like(needle)))
    total = q.count()
    items = q.order_by(Question.id.desc()).offset(offset).limit(limit).all()
    return {"ok": True, "data": {"total": total, "questions": [question_payload(item) for item in items]}}


@router.post("/questions")
def create_question(req: QuestionReq, admin=Depends(require_superadmin), db: Session = Depends(get_db)):
    if not admin:
        return {"ok": False, "error": "Forbidden"}
    q = Question(**req.model_dump())
    q.section = q.section.upper()
    db.add(q)
    db.commit()
    db.refresh(q)
    return {"ok": True, "data": question_payload(q)}


@router.put("/questions/{question_id}")
def update_question(question_id: int, req: QuestionReq, admin=Depends(require_superadmin), db: Session = Depends(get_db)):
    if not admin:
        return {"ok": False, "error": "Forbidden"}
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        return {"ok": False, "error": "Soal tidak ditemukan"}
    for key, value in req.model_dump().items():
        setattr(q, key, value)
    q.section = q.section.upper()
    db.commit()
    db.refresh(q)
    return {"ok": True, "data": question_payload(q)}


@router.delete("/questions/{question_id}")
def delete_question(question_id: int, admin=Depends(require_superadmin), db: Session = Depends(get_db)):
    if not admin:
        return {"ok": False, "error": "Forbidden"}
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        return {"ok": False, "error": "Soal tidak ditemukan"}
    package_count = db.query(func.count(TryoutPackage.id)).filter(func.json_contains(TryoutPackage.question_ids, str(question_id)) == 1).scalar() or 0
    if package_count:
        return {"ok": False, "error": "Soal masih dipakai di paket try out"}
    db.delete(q)
    db.commit()
    return {"ok": True, "message": "Soal dihapus"}
