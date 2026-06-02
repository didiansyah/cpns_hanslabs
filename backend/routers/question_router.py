from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db import get_db
from models import Question

router = APIRouter(redirect_slashes=False)

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
def list_questions(section: str = None, topic: str = None, year: int = None, difficulty: str = None, limit: int = Query(20, le=100), db: Session = Depends(get_db)):
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
def list_topics(section: str = None, db: Session = Depends(get_db)):
    from sqlalchemy import func
    q = db.query(Question.topic, func.count(Question.id).label("count"))
    if section:
        q = q.filter(Question.section == section.upper())
    q = q.group_by(Question.topic).order_by(func.count(Question.id).desc())
    return {"ok": True, "data": [{"topic": r.topic, "count": r.count} for r in q.all()]}

@router.get("/random")
def random_questions(section: str = None, topic: str = None, count: int = Query(10, le=50), db: Session = Depends(get_db)):
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
def get_question(question_id: int, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        return {"ok": False, "error": "Soal tidak ditemukan"}
    return {"ok": True, "data": {
        "id": q.id, "section": q.section, "topic": q.topic, "year": q.year,
        "difficulty": q.difficulty, "question_text": q.question_text,
        "options": public_options(q.options)
        # correct_answer and explanation NOT exposed — must use /check endpoint
    }}

@router.post("/check", include_in_schema=False)
@router.post("/check/")
def check_answer(data: dict, db: Session = Depends(get_db)):
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
    # Only reveal scoring details AFTER user submits
    return {
        "ok": True,
        "correct": is_correct,
        "correct_answer": q.correct_answer,
        "selected_score": selected_score,
        "max_score": max_score,
        "explanation": q.explanation,
    }
