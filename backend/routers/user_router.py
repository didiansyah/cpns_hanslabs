from fastapi import APIRouter, Depends, Request
import os
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import get_db
from services.auth_service import decode_jwt
from models import User
from services.progress_service import get_or_create_progress, progress_payload

router = APIRouter()

DEFAULT_SUPERADMIN_EMAILS = {"didihansya@gmail.com", "thisishanslabs@gmail.com"}

def is_superadmin_email(email: str) -> bool:
    configured = os.getenv("SUPERADMIN_EMAILS", "")
    emails = {item.strip().lower() for item in configured.split(",") if item.strip()} or DEFAULT_SUPERADMIN_EMAILS
    return email.lower() in emails

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
        "verified": user.verified, "is_superadmin": is_superadmin_email(user.email), "created_at": str(user.created_at)
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
    p = get_or_create_progress(db, user.id)
    db.commit()
    db.refresh(p)
    return {"ok": True, "data": progress_payload(p)}
