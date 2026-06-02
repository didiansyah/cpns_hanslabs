from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import get_db
from services.auth_service import decode_jwt
from models import User, Simulation, Progress, Question, TryoutPackage

router = APIRouter(redirect_slashes=False)

PASSING = {"TWK": 65, "TIU": 80, "TKP": 166}


def api_error(message: str, status_code: int):
    return JSONResponse(status_code=status_code, content={"ok": False, "error": message})


def require_auth(request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "): return None
    data = decode_jwt(auth[7:])
    if not data: return None
    return db.query(User).filter(User.id == data["user_id"]).first()


class CreateSimReq(BaseModel):
    sim_type: str = "full"
    package_id: int | None = None
    questions_data: dict | None = None


class SubmitSimReq(BaseModel):
    twk_score: int | None = None
    tiu_score: int | None = None
    tkp_score: int | None = None
    duration_seconds: int | None = None
    questions_data: dict | None = None


def public_options(options):
    if not isinstance(options, list):
        return []
    return [o.get("text", "") if isinstance(o, dict) else o for o in options]


def public_question(q: Question):
    return {
        "id": q.id, "section": q.section, "topic": q.topic, "year": q.year,
        "difficulty": q.difficulty, "question_text": q.question_text,
        "options": public_options(q.options),
    }


def package_counts(package: TryoutPackage):
    ids = package.question_ids or {}
    return {
        "twk": len(ids.get("TWK", [])),
        "tiu": len(ids.get("TIU", [])),
        "tkp": len(ids.get("TKP", [])),
        "total": sum(len(ids.get(sec, [])) for sec in ("TWK", "TIU", "TKP")),
    }


def score_answer(question: Question, selected: int) -> tuple[bool, int, int]:
    options = question.options if isinstance(question.options, list) else []
    if selected < 0 or selected >= len(options):
        return False, 0, 5
    if question.section == "TKP" and isinstance(options[selected], dict):
        score = int(options[selected].get("score", 0))
        max_score = max([int(o.get("score", 0)) for o in options if isinstance(o, dict)] or [5])
        return score == max_score, score, max_score
    correct = selected == question.correct_answer
    return correct, 5 if correct else 0, 5


def flatten_package_question_ids(question_ids_by_section: dict | None) -> list[int]:
    if not isinstance(question_ids_by_section, dict):
        return []
    ordered_ids: list[int] = []
    for sec in ("TWK", "TIU", "TKP"):
        ordered_ids.extend([int(qid) for qid in question_ids_by_section.get(sec, [])])
    return ordered_ids


def calculate_scores(db: Session, questions_data: dict | None, allowed_question_ids: list[int] | None = None):
    if not questions_data:
        return None
    answers = questions_data.get("answers") or []
    question_refs = questions_data.get("questions") or []

    if allowed_question_ids is not None:
        ordered_ids = [int(qid) for qid in allowed_question_ids]
        allowed_set = set(ordered_ids)
        question_ids = set(ordered_ids)
    else:
        ordered_ids = [int(q.get("id")) for q in question_refs if q.get("id") is not None]
        allowed_set = None
        question_ids = {int(a.get("question_id")) for a in answers if a.get("question_id") is not None}
        question_ids.update(ordered_ids)
    if not question_ids:
        return None

    questions = {q.id: q for q in db.query(Question).filter(Question.id.in_(question_ids)).all()}
    if allowed_question_ids is not None:
        question_refs = [{"id": qid, "section": questions[qid].section} for qid in ordered_ids if qid in questions]

    sections = {}
    for ref in question_refs:
        q = questions.get(int(ref.get("id", 0)))
        if not q:
            continue
        sections.setdefault(q.section, {"total": 0, "answered": 0, "correct": 0, "wrong": 0, "score": 0, "max_score": 0})
        sections[q.section]["total"] += 1
        sections[q.section]["max_score"] += 5

    deduped_answers = {}
    for answer in answers:
        if answer.get("question_id") is None:
            continue
        qid = int(answer.get("question_id"))
        if allowed_set is not None and qid not in allowed_set:
            continue
        deduped_answers[qid] = answer

    checked = []
    for qid, answer in deduped_answers.items():
        q = questions.get(qid)
        if not q:
            continue
        selected = int(answer.get("selected", -1))
        correct, score, max_score = score_answer(q, selected)
        stats = sections.setdefault(q.section, {"total": 0, "answered": 0, "correct": 0, "wrong": 0, "score": 0, "max_score": 0})
        if stats["total"] == 0:
            stats["total"] += 1
            stats["max_score"] += max_score
        stats["answered"] += 1
        stats["score"] += score
        if correct:
            stats["correct"] += 1
        checked.append({"question_id": q.id, "selected": selected, "section": q.section, "correct": correct, "score": score, "max_score": max_score})

    for stats in sections.values():
        stats["wrong"] = max(0, stats["total"] - stats["correct"])

    safe_questions_data = {**questions_data, "questions": question_refs, "answers": checked, "sections": sections}
    if allowed_question_ids is not None:
        safe_questions_data.pop("question_ids", None)
    return {
        "twk_score": sections.get("TWK", {}).get("score"),
        "tiu_score": sections.get("TIU", {}).get("score"),
        "tkp_score": sections.get("TKP", {}).get("score"),
        "questions_data": safe_questions_data,
    }


@router.get("/packages")
def list_packages(user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user: return api_error("Unauthorized", 401)
    packages = db.query(TryoutPackage).filter(TryoutPackage.is_active == True).order_by(TryoutPackage.part_number.asc()).all()
    attempts = db.query(Simulation).filter(Simulation.user_id == user.id, Simulation.package_id.isnot(None), Simulation.total_score.isnot(None)).order_by(Simulation.created_at.asc()).all()
    by_package = {}
    for sim in attempts:
        item = by_package.setdefault(sim.package_id, {"attempts": 0, "best_score": None, "latest_score": None, "latest_passed": None})
        item["attempts"] += 1
        item["latest_score"] = sim.total_score
        item["latest_passed"] = sim.passed
        item["best_score"] = max(item["best_score"] or 0, sim.total_score or 0)
    return {"ok": True, "data": [{
        "id": p.id,
        "part_number": p.part_number,
        "title": p.title,
        "sim_type": p.sim_type,
        "counts": package_counts(p),
        "attempts": by_package.get(p.id, {}).get("attempts", 0),
        "best_score": by_package.get(p.id, {}).get("best_score"),
        "latest_score": by_package.get(p.id, {}).get("latest_score"),
        "latest_passed": by_package.get(p.id, {}).get("latest_passed"),
    } for p in packages]}


@router.post("", include_in_schema=False)
@router.post("/")
def create_sim(req: CreateSimReq, user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user: return api_error("Unauthorized", 401)
    package = None
    questions_data = req.questions_data
    if req.package_id:
        package = db.query(TryoutPackage).filter(TryoutPackage.id == req.package_id, TryoutPackage.is_active == True).first()
        if not package: return api_error("Paket try out tidak ditemukan", 404)
        questions_data = {"package_id": package.id, "part_number": package.part_number, "question_ids": package.question_ids}
    sim = Simulation(
        user_id=user.id,
        sim_type=package.sim_type if package else req.sim_type,
        package_id=package.id if package else None,
        questions_data=questions_data,
    )
    db.add(sim)
    db.commit()
    db.refresh(sim)
    return {"ok": True, "data": {"id": sim.id, "sim_type": sim.sim_type, "package_id": sim.package_id}}


@router.get("", include_in_schema=False)
@router.get("/")
def list_sims(user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user: return api_error("Unauthorized", 401)
    sims = db.query(Simulation).filter(Simulation.user_id == user.id).order_by(Simulation.created_at.desc()).limit(50).all()
    return {"ok": True, "data": [{
        "id": s.id,
        "sim_type": s.sim_type,
        "package_id": s.package_id,
        "part_number": (s.questions_data or {}).get("part_number") if isinstance(s.questions_data, dict) else None,
        "twk_score": s.twk_score,
        "tiu_score": s.tiu_score,
        "tkp_score": s.tkp_score,
        "total_score": s.total_score,
        "passed": s.passed,
        "duration_seconds": s.duration_seconds,
        "created_at": str(s.created_at),
    } for s in sims]}


@router.get("/{sim_id}/questions")
def get_sim_questions(sim_id: int, user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user: return api_error("Unauthorized", 401)
    sim = db.query(Simulation).filter(Simulation.id == sim_id, Simulation.user_id == user.id).first()
    if not sim: return api_error("Simulasi tidak ditemukan", 404)
    data = sim.questions_data if isinstance(sim.questions_data, dict) else {}
    question_ids_by_section = data.get("question_ids")
    if not question_ids_by_section and sim.package_id:
        package = db.query(TryoutPackage).filter(TryoutPackage.id == sim.package_id).first()
        question_ids_by_section = package.question_ids if package else None
    if not question_ids_by_section:
        return api_error("Paket soal tidak ditemukan", 404)
    ordered_ids = flatten_package_question_ids(question_ids_by_section)
    questions = {q.id: q for q in db.query(Question).filter(Question.id.in_(ordered_ids)).all()}
    return {"ok": True, "data": [public_question(questions[qid]) for qid in ordered_ids if qid in questions]}


@router.post("/{sim_id}/submit")
def submit_sim(sim_id: int, req: SubmitSimReq, user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user: return api_error("Unauthorized", 401)
    sim = db.query(Simulation).filter(Simulation.id == sim_id, Simulation.user_id == user.id).first()
    if not sim: return api_error("Simulasi tidak ditemukan", 404)
    if sim.submitted_at or sim.total_score is not None:
        return api_error("Simulasi ini sudah pernah disubmit", 409)

    base_data = sim.questions_data if isinstance(sim.questions_data, dict) else {}
    incoming_data = req.questions_data or {}
    allowed_question_ids = None
    if sim.package_id:
        question_ids_by_section = base_data.get("question_ids")
        if not question_ids_by_section:
            package = db.query(TryoutPackage).filter(TryoutPackage.id == sim.package_id).first()
            question_ids_by_section = package.question_ids if package else None
        allowed_question_ids = flatten_package_question_ids(question_ids_by_section)
        if not allowed_question_ids:
            return api_error("Paket soal tidak ditemukan", 404)
        scored_input = {**base_data, "answers": incoming_data.get("answers") or []}
    else:
        scored_input = {**base_data, **incoming_data}

    scored = calculate_scores(db, scored_input, allowed_question_ids=allowed_question_ids)
    twk_score = scored["twk_score"] if scored and scored["twk_score"] is not None else req.twk_score
    tiu_score = scored["tiu_score"] if scored and scored["tiu_score"] is not None else req.tiu_score
    tkp_score = scored["tkp_score"] if scored and scored["tkp_score"] is not None else req.tkp_score
    sim.twk_score = twk_score
    sim.tiu_score = tiu_score
    sim.tkp_score = tkp_score
    sim.duration_seconds = req.duration_seconds
    sim.submitted_at = datetime.utcnow()
    sim.questions_data = scored["questions_data"] if scored else scored_input
    total = (twk_score or 0) + (tiu_score or 0) + (tkp_score or 0)
    sim.total_score = total
    if sim.sim_type == "full":
        sim.passed = (twk_score or 0) >= PASSING["TWK"] and (tiu_score or 0) >= PASSING["TIU"] and (tkp_score or 0) >= PASSING["TKP"]
    elif sim.sim_type == "twk":
        sim.passed = (twk_score or 0) >= PASSING["TWK"]
    elif sim.sim_type == "tiu":
        sim.passed = (tiu_score or 0) >= PASSING["TIU"]
    elif sim.sim_type == "tkp":
        sim.passed = (tkp_score or 0) >= PASSING["TKP"]
    else:
        sim.passed = total >= sum(PASSING.values())
    db.commit()

    p = db.query(Progress).filter(Progress.user_id == user.id).first()
    if p:
        p.sim_count = (p.sim_count or 0) + 1
        if twk_score is not None: p.twk_score = twk_score
        if tiu_score is not None: p.tiu_score = tiu_score
        if tkp_score is not None: p.tkp_score = tkp_score
        db.commit()

    return {"ok": True, "data": {"total_score": total, "passed": sim.passed}}


@router.get("/{sim_id}")
def get_sim(sim_id: int, user=Depends(require_auth), db: Session = Depends(get_db)):
    if not user: return api_error("Unauthorized", 401)
    sim = db.query(Simulation).filter(Simulation.id == sim_id, Simulation.user_id == user.id).first()
    if not sim: return api_error("Simulasi tidak ditemukan", 404)

    rank_query = db.query(Simulation).filter(Simulation.total_score.isnot(None))
    if sim.package_id:
        rank_query = rank_query.filter(Simulation.package_id == sim.package_id)
    else:
        rank_query = rank_query.filter(Simulation.sim_type == sim.sim_type)
    total_participants = rank_query.count()
    better_count = rank_query.filter(Simulation.total_score > sim.total_score).count()
    ranking = better_count + 1 if sim.total_score else total_participants
    data = sim.questions_data if isinstance(sim.questions_data, dict) else {}

    return {"ok": True, "data": {
        "id": sim.id,
        "sim_type": sim.sim_type,
        "package_id": sim.package_id,
        "part_number": data.get("part_number"),
        "twk_score": sim.twk_score,
        "tiu_score": sim.tiu_score,
        "tkp_score": sim.tkp_score,
        "total_score": sim.total_score,
        "passed": sim.passed,
        "duration_seconds": sim.duration_seconds,
        "questions_data": sim.questions_data,
        "created_at": str(sim.created_at),
        "ranking": ranking,
        "total_participants": total_participants,
    }}
