from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import get_db
from services.auth_service import decode_jwt
from models import User, Progress

router = APIRouter()

def require_auth(request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    data = decode_jwt(auth[7:])
    if not data:
        return None
    return db.query(User).filter(User.id == data["user_id"]).first()

class UpdateProfileReq(BaseModel):
    name: str | None = None
    phone: str | None = None
    education: str | None = None
    target_instansi: str | None = None
    previous_cpns: bool | None = None

@router.get("/me")
def get_me(user=Depends(require_auth)):
    if not user:
        return {"ok": False, "error": "Unauthorized"}
    return {"ok": True, "data": {
        "id": user.id, "name": user.name, "email": user.email,
        "phone": user.phone, "education": user.education,
        "target_instansi": user.target_instansi, "previous_cpns": user.previous_cpns,
        "verified": user.verified, "created_at": str(user.created_at)
    }}

@router.put("/me")
def update_me(req: UpdateProfileReq, user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user:
        return {"ok": False, "error": "Unauthorized"}
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(user, k, v)
    db.commit()
    return {"ok": True, "message": "Profil diperbarui"}

@router.get("/me/progress")
def get_progress(user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user:
        return {"ok": False, "error": "Unauthorized"}
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
