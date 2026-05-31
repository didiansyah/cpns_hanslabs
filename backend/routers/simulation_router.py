from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import get_db
from services.auth_service import decode_jwt
from models import User, Simulation, Progress

router = APIRouter()

def require_auth(request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "): return None
    data = decode_jwt(auth[7:])
    if not data: return None
    return db.query(User).filter(User.id == data["user_id"]).first()

class CreateSimReq(BaseModel):
    sim_type: str
    questions_data: dict | None = None

class SubmitSimReq(BaseModel):
    twk_score: int | None = None
    tiu_score: int | None = None
    tkp_score: int | None = None
    duration_seconds: int | None = None
    questions_data: dict | None = None

@router.post("/")
def create_sim(req: CreateSimReq, user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user: return {"ok": False, "error": "Unauthorized"}
    sim = Simulation(user_id=user.id, sim_type=req.sim_type, questions_data=req.questions_data)
    db.add(sim)
    db.commit()
    db.refresh(sim)
    return {"ok": True, "data": {"id": sim.id, "sim_type": sim.sim_type}}

@router.get("/")
def list_sims(user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user: return {"ok": False, "error": "Unauthorized"}
    sims = db.query(Simulation).filter(Simulation.user_id == user.id).order_by(Simulation.created_at.desc()).limit(50).all()
    return {"ok": True, "data": [{
        "id": s.id, "sim_type": s.sim_type, "twk_score": s.twk_score, "tiu_score": s.tiu_score,
        "tkp_score": s.tkp_score, "total_score": s.total_score, "passed": s.passed,
        "duration_seconds": s.duration_seconds, "created_at": str(s.created_at)
    } for s in sims]}

@router.post("/{sim_id}/submit")
def submit_sim(sim_id: int, req: SubmitSimReq, user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user: return {"ok": False, "error": "Unauthorized"}
    sim = db.query(Simulation).filter(Simulation.id == sim_id, Simulation.user_id == user.id).first()
    if not sim: return {"ok": False, "error": "Simulasi tidak ditemukan"}
    sim.twk_score = req.twk_score
    sim.tiu_score = req.tiu_score
    sim.tkp_score = req.tkp_score
    sim.duration_seconds = req.duration_seconds
    sim.questions_data = req.questions_data
    total = (req.twk_score or 0) + (req.tiu_score or 0) + (req.tkp_score or 0)
    sim.total_score = total
    # Check passing based on simulation type
    if sim.sim_type == "full":
        sim.passed = (req.twk_score or 0) >= 65 and (req.tiu_score or 0) >= 80 and (req.tkp_score or 0) >= 143
    elif sim.sim_type == "twk":
        sim.passed = (req.twk_score or 0) >= 65
    elif sim.sim_type == "tiu":
        sim.passed = (req.tiu_score or 0) >= 80
    elif sim.sim_type == "tkp":
        sim.passed = (req.tkp_score or 0) >= 143
    else:
        sim.passed = total >= 288  # combined minimum
    db.commit()

    # Update progress
    p = db.query(Progress).filter(Progress.user_id == user.id).first()
    if p:
        p.sim_count = (p.sim_count or 0) + 1
        if req.twk_score: p.twk_score = req.twk_score
        if req.tiu_score: p.tiu_score = req.tiu_score
        if req.tkp_score: p.tkp_score = req.tkp_score
        db.commit()

    return {"ok": True, "data": {"total_score": total, "passed": sim.passed}}
