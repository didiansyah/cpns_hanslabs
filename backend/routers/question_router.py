from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db import get_db
from models import Question

router = APIRouter()

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
    questions = q.limit(limit).all()
    return {"ok": True, "data": [{
        "id": q.id, "section": q.section, "topic": q.topic, "year": q.year,
        "difficulty": q.difficulty, "question_text": q.question_text,
        "options": q.options
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
    questions = q.limit(count).all()
    return {"ok": True, "data": [{
        "id": q.id, "section": q.section, "topic": q.topic, "year": q.year,
        "difficulty": q.difficulty, "question_text": q.question_text,
        "options": q.options
    } for q in questions]}

@router.get("/{question_id}")
def get_question(question_id: int, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        return {"ok": False, "error": "Soal tidak ditemukan"}
    return {"ok": True, "data": {
        "id": q.id, "section": q.section, "topic": q.topic, "year": q.year,
        "difficulty": q.difficulty, "question_text": q.question_text,
        "options": q.options
        # correct_answer and explanation NOT exposed — must use /check endpoint
    }}

@router.post("/check")
def check_answer(data: dict, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == data.get("question_id")).first()
    if not q:
        return {"ok": False, "error": "Soal tidak ditemukan"}
    user_answer = data.get("answer")
    if user_answer is None:
        return {"ok": False, "error": "Jawaban tidak boleh kosong"}
    is_correct = user_answer == q.correct_answer
    # Only reveal correct_answer + explanation AFTER user submits
    return {"ok": True, "correct": is_correct, "correct_answer": q.correct_answer, "explanation": q.explanation}
