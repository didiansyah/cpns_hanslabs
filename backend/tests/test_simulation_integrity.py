import os
import sys
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("JWT_SECRET", "test-secret-with-enough-length")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db import Base
from models import Question
from routers.simulation_router import calculate_scores


def make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def add_question(db, qid, section="TWK", correct=0):
    q = Question(
        id=qid,
        section=section,
        topic="Test Topic",
        difficulty="mudah",
        question_text=f"Question {qid} with enough text for testing",
        options=["A", "B", "C", "D", "E"],
        correct_answer=correct,
        explanation="Test explanation",
    )
    db.add(q)
    db.commit()
    return q


def test_calculate_scores_ignores_forged_questions_outside_fixed_package():
    db = make_db()
    add_question(db, 1, "TWK", correct=0)
    add_question(db, 999, "TWK", correct=1)

    result = calculate_scores(
        db,
        {
            "questions": [{"id": 1, "section": "TWK"}, {"id": 999, "section": "TWK"}],
            "answers": [
                {"question_id": 1, "selected": 0},
                {"question_id": 999, "selected": 1},
            ],
        },
        allowed_question_ids=[1],
    )

    assert result["twk_score"] == 5
    checked_ids = [a["question_id"] for a in result["questions_data"]["answers"]]
    assert checked_ids == [1]
    assert result["questions_data"]["sections"]["TWK"]["total"] == 1


def test_calculate_scores_uses_package_questions_even_when_client_omits_question_refs():
    db = make_db()
    add_question(db, 1, "TWK", correct=0)
    add_question(db, 2, "TWK", correct=0)

    result = calculate_scores(
        db,
        {"answers": [{"question_id": 1, "selected": 0}]},
        allowed_question_ids=[1, 2],
    )

    assert result["twk_score"] == 5
    assert result["questions_data"]["sections"]["TWK"]["total"] == 2
    assert result["questions_data"]["sections"]["TWK"]["answered"] == 1


def test_calculate_scores_deduplicates_answers_by_question_id_last_answer_wins():
    db = make_db()
    add_question(db, 1, "TWK", correct=1)

    result = calculate_scores(
        db,
        {
            "questions": [{"id": 1, "section": "TWK"}],
            "answers": [
                {"question_id": 1, "selected": 0},
                {"question_id": 1, "selected": 1},
            ],
        },
        allowed_question_ids=[1],
    )

    assert result["twk_score"] == 5
    assert result["questions_data"]["sections"]["TWK"]["answered"] == 1
    assert result["questions_data"]["answers"] == [
        {"question_id": 1, "selected": 1, "section": "TWK", "correct": True, "score": 5, "max_score": 5}
    ]
