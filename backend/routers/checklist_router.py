from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import get_db
from services.auth_service import decode_jwt
from models import User, Checklist
from services.progress_service import mark_study_activity, progress_payload, today_jakarta

router = APIRouter()

def require_auth(request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "): return None
    data = decode_jwt(auth[7:])
    if not data: return None
    return db.query(User).filter(User.id == data["user_id"]).first()

@router.get("/today")
def get_today(user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user: return {"ok": False, "error": "Unauthorized"}
    today = today_jakarta()
    chk = db.query(Checklist).filter(Checklist.user_id == user.id, Checklist.date == today).first()
    if not chk:
        chk = Checklist(user_id=user.id, date=today)
        db.add(chk)
        db.commit()
        db.refresh(chk)
    return {"ok": True, "data": {
        "date": str(chk.date), "chk1": chk.chk1, "chk2": chk.chk2,
        "chk3": chk.chk3, "chk4": chk.chk4, "chk5": chk.chk5
    }}

class UpdateChecklistReq(BaseModel):
    chk1: bool | None = None
    chk2: bool | None = None
    chk3: bool | None = None
    chk4: bool | None = None
    chk5: bool | None = None

@router.put("/today")
def update_today(req: UpdateChecklistReq, user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user: return {"ok": False, "error": "Unauthorized"}
    today = today_jakarta()
    chk = db.query(Checklist).filter(Checklist.user_id == user.id, Checklist.date == today).first()
    if not chk:
        chk = Checklist(user_id=user.id, date=today)
        db.add(chk)
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(chk, k, v)
    progress = None
    if any(v is True for v in req.model_dump(exclude_unset=True).values()):
        progress = mark_study_activity(db, user.id)
    db.commit()
    if progress:
        db.refresh(progress)
    return {
        "ok": True,
        "message": "Checklist diperbarui",
        "progress": progress_payload(progress) if progress else None,
    }

@router.get("/history")
def history(user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user: return {"ok": False, "error": "Unauthorized"}
    chks = db.query(Checklist).filter(Checklist.user_id == user.id).order_by(Checklist.date.desc()).limit(30).all()
    return {"ok": True, "data": [{
        "date": str(c.date), "chk1": c.chk1, "chk2": c.chk2,
        "chk3": c.chk3, "chk4": c.chk4, "chk5": c.chk5
    } for c in chks]}
