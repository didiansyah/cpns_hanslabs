import time

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from db import get_db
from models import Question
from main import limiter
from services.auth_service import decode_jwt
from services.progress_service import mark_study_activity, progress_payload

router = APIRouter(redirect_slashes=False)

CACHE_TTL_SECONDS = 300
_topics_cache: dict[tuple[str | None], tuple[float, list[dict]]] = {}
_question_cache: dict[int, tuple[float, dict]] = {}

def public_options(options):
    """Expose option text only. TKP option scores stay server-side until answered."""
    if not isinstance(options, list):
        return []
    return [o.get("text", "") if isinstance(o, dict) else o for o in options]

def is_tkp_weighted(question: Question) -> bool:
    options = question.options if isinstance(question.options, list) else []
    return question.section == "TKP" and len(options) == 5 and all(isinstance(o, dict) and "score" in o for o in options)

def is_public_usable(question: Question) -> bool:
    opts = public_options(question.options)
    normalized = [o.strip().lower() for o in opts if isinstance(o, str)]
    has_answer_key = question.correct_answer is not None or is_tkp_weighted(question)
    return (
        len(opts) == 5
        and all(isinstance(o, str) and o.strip() for o in opts)
        and len(set(normalized)) == 5
        and has_answer_key
    )

def option_score(question: Question, selected: int) -> tuple[bool, int, int]:
    options = question.options if isinstance(question.options, list) else []
    if selected < 0 or selected >= len(options):
        return False, 0, 5
    if question.section == "TKP" and isinstance(options[selected], dict):
        scores = [int(o.get("score", 0)) for o in options if isinstance(o, dict)]
        selected_score = int(options[selected].get("score", 0))
        max_score = max(scores) if scores else 5
        return selected_score == max_score, selected_score, max_score
    correct = selected == question.correct_answer
    return correct, 5 if correct else 0, 5


@router.get("", include_in_schema=False)
@router.get("/")
@limiter.limit("20/minute")
def list_questions(request: Request, section: str = None, topic: str = None, year: int = None, difficulty: str = None, limit: int = Query(20, le=100), db: Session = Depends(get_db)):
    q = db.query(Question)
    if section:
        q = q.filter(Question.section == section.upper())
    if topic:
        q = q.filter(Question.topic == topic)
    if year:
        q = q.filter(Question.year == year)
    if difficulty:
        q = q.filter(Question.difficulty == difficulty)
    questions = []
    for item in q.limit(min(limit * 3, 300)).all():
        if is_public_usable(item):
            questions.append(item)
        if len(questions) >= limit:
            break
    return {"ok": True, "data": [{
        "id": q.id, "section": q.section, "topic": q.topic, "year": q.year,
        "difficulty": q.difficulty, "question_text": q.question_text,
        "options": public_options(q.options)
    } for q in questions]}

@router.get("/topics")
@limiter.limit("60/minute")
def list_topics(request: Request, section: str = None, db: Session = Depends(get_db)):
    from sqlalchemy import func
    normalized_section = section.upper() if section else None
    cache_key = (normalized_section,)
    now = time.time()
    cached = _topics_cache.get(cache_key)
    if cached and now < cached[0]:
        return {"ok": True, "data": cached[1]}
    q = db.query(Question.topic, func.count(Question.id).label("count"))
    if normalized_section:
        q = q.filter(Question.section == normalized_section)
    q = q.group_by(Question.topic).order_by(func.count(Question.id).desc())
    data = [{"topic": r.topic, "count": r.count} for r in q.all()]
    _topics_cache[cache_key] = (now + CACHE_TTL_SECONDS, data)
    return {"ok": True, "data": data}

@router.get("/random")
@limiter.limit("20/minute")
def random_questions(request: Request, section: str = None, topic: str = None, count: int = Query(10, le=50), db: Session = Depends(get_db)):
    from sqlalchemy import func
    q = db.query(Question).order_by(func.rand())
    if section:
        q = q.filter(Question.section == section.upper())
    if topic:
        q = q.filter(Question.topic == topic)
    questions = []
    for item in q.limit(min(count * 3, 150)).all():
        if is_public_usable(item):
            questions.append(item)
        if len(questions) >= count:
            break
    return {"ok": True, "data": [{
        "id": q.id, "section": q.section, "topic": q.topic, "year": q.year,
        "difficulty": q.difficulty, "question_text": q.question_text,
        "options": public_options(q.options)
    } for q in questions]}

@router.get("/{question_id}")
@limiter.limit("30/minute")
def get_question(request: Request, question_id: int, db: Session = Depends(get_db)):
    now = time.time()
    cached = _question_cache.get(question_id)
    if cached and now < cached[0]:
        return {"ok": True, "data": cached[1]}
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        return {"ok": False, "error": "Soal tidak ditemukan"}
    data = {
        "id": q.id, "section": q.section, "topic": q.topic, "year": q.year,
        "difficulty": q.difficulty, "question_text": q.question_text,
        "options": public_options(q.options)
        # correct_answer and explanation NOT exposed — must use /check endpoint
    }
    _question_cache[question_id] = (now + CACHE_TTL_SECONDS, data)
    if len(_question_cache) > 512:
        oldest_key = min(_question_cache, key=lambda item: _question_cache[item][0])
        _question_cache.pop(oldest_key, None)
    return {"ok": True, "data": data}

@router.post("/check", include_in_schema=False)
@router.post("/check/")
@limiter.limit("30/minute")
def check_answer(request: Request, data: dict, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == data.get("question_id")).first()
    if not q:
        return {"ok": False, "error": "Soal tidak ditemukan"}
    user_answer = data.get("answer")
    if user_answer is None:
        return {"ok": False, "error": "Jawaban tidak boleh kosong"}
    try:
        selected = int(user_answer)
    except (TypeError, ValueError):
        return {"ok": False, "error": "Jawaban tidak valid"}
    is_correct, selected_score, max_score = option_score(q, selected)
    progress = None
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        payload = decode_jwt(auth[7:])
        if payload and payload.get("user_id"):
            progress = mark_study_activity(db, int(payload["user_id"]))
            db.commit()

    # Only reveal scoring details AFTER user submits
    response = {
        "ok": True,
        "correct": is_correct,
        "correct_answer": q.correct_answer,
        "selected_score": selected_score,
        "max_score": max_score,
        "explanation": q.explanation,
    }
    if progress:
        response["progress"] = progress_payload(progress)
    return response


