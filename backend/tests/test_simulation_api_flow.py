import os
import sys
from datetime import timedelta

os.environ.setdefault("JWT_SECRET", "test-secret-with-enough-length")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import db as db_module
from db import Base
from main import app
from models import Checklist, Progress, Question, Simulation, TryoutPackage, User
from services.auth_service import create_jwt
from services.progress_service import today_jakarta


def make_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def seed_question(session, qid: int, section: str, correct: int = 0):
    options = ["A", "B", "C", "D", "E"]
    if section == "TKP":
        options = [{"text": label, "score": idx + 1} for idx, label in enumerate(options)]
    q = Question(
        id=qid,
        section=section,
        topic="Audit",
        difficulty="mudah",
        question_text=f"Question {qid} has enough wording for endpoint flow tests",
        options=options,
        correct_answer=correct,
        explanation="Explanation",
    )
    session.add(q)
    return q


def build_client():
    session = make_session()
    user = User(id=1, name="Tester", email="tester@example.com", password_hash="x", verified=True)
    session.add(user)
    session.add(Progress(user_id=1))
    ids = {"TWK": [], "TIU": [], "TKP": []}
    next_id = 1
    for section, count in (("TWK", 30), ("TIU", 35), ("TKP", 45)):
        for _ in range(count):
            seed_question(session, next_id, section, correct=0)
            ids[section].append(next_id)
            next_id += 1
    seed_question(session, 999, "TWK", correct=0)
    session.add(TryoutPackage(id=1, part_number=1, title="Part 1", sim_type="full", question_ids=ids, is_active=True))
    session.commit()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[db_module.get_db] = override_get_db
    client = TestClient(app)
    token = create_jwt(1, "tester@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    return client, session, headers


def test_simulation_api_returns_real_http_status_codes_for_errors():
    client, _, headers = build_client()

    unauthorized = client.get("/api/simulations/packages")
    assert unauthorized.status_code == 401
    assert unauthorized.json() == {"ok": False, "error": "Unauthorized"}

    missing_package = client.post("/api/simulations/", headers=headers, json={"sim_type": "full", "package_id": 404})
    assert missing_package.status_code == 404
    assert missing_package.json() == {"ok": False, "error": "Paket try out tidak ditemukan"}

    missing_sim = client.get("/api/simulations/404/questions", headers=headers)
    assert missing_sim.status_code == 404
    assert missing_sim.json() == {"ok": False, "error": "Simulasi tidak ditemukan"}


def test_full_fixed_package_endpoint_flow_blocks_resubmit_and_ignores_forged_answers():
    client, session, headers = build_client()

    packages = client.get("/api/simulations/packages", headers=headers)
    assert packages.status_code == 200
    assert packages.json()["data"][0]["counts"] == {"twk": 30, "tiu": 35, "tkp": 45, "total": 110}

    created = client.post("/api/simulations/", headers=headers, json={"sim_type": "full", "package_id": 1})
    assert created.status_code == 200
    sim_id = created.json()["data"]["id"]

    questions = client.get(f"/api/simulations/{sim_id}/questions", headers=headers)
    assert questions.status_code == 200
    assert len(questions.json()["data"]) == 110

    submit = client.post(
        f"/api/simulations/{sim_id}/submit",
        headers=headers,
        json={
            "duration_seconds": 120,
            "questions_data": {
                "questions": [{"id": 999, "section": "TWK"}],
                "answers": [
                    {"question_id": 1, "selected": 0},
                    {"question_id": 999, "selected": 0},
                ],
            },
        },
    )
    assert submit.status_code == 200
    assert submit.json()["ok"] is True
    progress_after_submit = session.query(Progress).filter(Progress.user_id == 1).first()
    assert progress_after_submit.study_days == 1
    assert progress_after_submit.streak_days == 1
    assert float(progress_after_submit.study_hours) == 0.03

    result = client.get(f"/api/simulations/{sim_id}", headers=headers)
    assert result.status_code == 200
    data = result.json()["data"]
    checked_ids = [a["question_id"] for a in data["questions_data"]["answers"]]
    assert checked_ids == [1]
    assert data["questions_data"]["sections"]["TWK"]["total"] == 30
    assert data["questions_data"]["sections"]["TIU"]["total"] == 35
    assert data["questions_data"]["sections"]["TKP"]["total"] == 45
    assert session.query(Simulation).filter(Simulation.id == sim_id).first().submitted_at is not None

    resubmit = client.post(
        f"/api/simulations/{sim_id}/submit",
        headers=headers,
        json={"duration_seconds": 130, "questions_data": {"answers": [{"question_id": 1, "selected": 0}]}},
    )
    assert resubmit.status_code == 409
    assert resubmit.json() == {"ok": False, "error": "Simulasi ini sudah pernah disubmit"}


def test_checklist_true_marks_dashboard_active_day_once_and_returns_progress():
    client, session, headers = build_client()

    first = client.put("/api/checklists/today", headers=headers, json={"chk1": True})
    assert first.status_code == 200
    assert first.json()["ok"] is True
    assert first.json()["progress"]["study_days"] == 1
    assert first.json()["progress"]["streak_days"] == 1

    second = client.put("/api/checklists/today", headers=headers, json={"chk2": True})
    assert second.status_code == 200
    assert second.json()["progress"]["study_days"] == 1

    progress = session.query(Progress).filter(Progress.user_id == 1).first()
    checklist = session.query(Checklist).filter(Checklist.user_id == 1).first()
    assert progress.study_days == 1
    assert progress.streak_days == 1
    assert checklist.chk1 is True
    assert checklist.chk2 is True


def test_checklist_active_day_continues_existing_streak():
    client, session, headers = build_client()
    progress = session.query(Progress).filter(Progress.user_id == 1).first()
    progress.study_days = 3
    progress.streak_days = 3
    progress.last_study_date = today_jakarta() - timedelta(days=1)
    session.commit()

    res = client.put("/api/checklists/today", headers=headers, json={"chk1": True})
    assert res.status_code == 200
    assert res.json()["progress"]["study_days"] == 4
    assert res.json()["progress"]["streak_days"] == 4



def test_question_check_marks_active_day_for_authenticated_practice():
    client, session, headers = build_client()

    res = client.post("/api/questions/check", headers=headers, json={"question_id": 1, "answer": 0})
    assert res.status_code == 200
    assert res.json()["ok"] is True
    assert res.json()["progress"]["study_days"] == 1
    assert res.json()["progress"]["streak_days"] == 1
    assert res.json()["progress"]["last_study_date"] == str(today_jakarta())

    second = client.post("/api/questions/check", headers=headers, json={"question_id": 2, "answer": 0})
    assert second.status_code == 200
    assert second.json()["progress"]["study_days"] == 1

    progress = session.query(Progress).filter(Progress.user_id == 1).first()
    assert progress.study_days == 1
    assert progress.streak_days == 1
