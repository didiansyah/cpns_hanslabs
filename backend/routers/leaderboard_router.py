from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import Progress, User

router = APIRouter()

@router.get("/")
def leaderboard(db: Session = Depends(get_db)):
    results = db.query(Progress, User).join(User, Progress.user_id == User.id).order_by(
        (Progress.twk_score + Progress.tiu_score + Progress.tkp_score).desc()
    ).limit(100).all()
    return {"ok": True, "data": [{
        "rank": i + 1,
        "name": u.name[0] + "***" if len(u.name) > 1 else u.name,
        "study_days": p.study_days,
        "sim_count": p.sim_count,
        "twk_score": float(p.twk_score or 0),
        "tiu_score": float(p.tiu_score or 0),
        "tkp_score": float(p.tkp_score or 0),
        "total": float((p.twk_score or 0) + (p.tiu_score or 0) + (p.tkp_score or 0))
    } for i, (p, u) in enumerate(results)]}
