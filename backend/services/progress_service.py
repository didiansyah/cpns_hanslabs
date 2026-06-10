from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from models import Progress

JAKARTA_TZ = ZoneInfo("Asia/Jakarta")


def today_jakarta() -> date:
    return datetime.now(JAKARTA_TZ).date()


def progress_payload(progress: Progress) -> dict:
    return {
        "study_days": int(progress.study_days or 0),
        "study_hours": float(progress.study_hours or 0),
        "sim_count": int(progress.sim_count or 0),
        "current_week": int(progress.current_week or 1),
        "twk_score": float(progress.twk_score or 0),
        "tiu_score": float(progress.tiu_score or 0),
        "tkp_score": float(progress.tkp_score or 0),
        "streak_days": int(progress.streak_days or 0),
        "last_study_date": str(progress.last_study_date) if progress.last_study_date else None,
    }


def get_or_create_progress(db: Session, user_id: int) -> Progress:
    progress = db.query(Progress).filter(Progress.user_id == user_id).first()
    if not progress:
        progress = Progress(user_id=user_id)
        db.add(progress)
        db.flush()
    return progress


def mark_study_activity(
    db: Session,
    user_id: int,
    *,
    duration_minutes: int | float = 0,
    activity_date: date | None = None,
) -> Progress:
    """Record one active study day, without double-counting repeated actions on the same date."""
    progress = get_or_create_progress(db, user_id)
    active_date = activity_date or today_jakarta()

    if duration_minutes and duration_minutes > 0:
        progress.study_hours = float(progress.study_hours or 0) + float(duration_minutes) / 60

    last_date = progress.last_study_date
    if last_date != active_date:
        progress.study_days = int(progress.study_days or 0) + 1
        if last_date and (active_date - last_date).days == 1:
            progress.streak_days = int(progress.streak_days or 0) + 1
        else:
            progress.streak_days = 1
        progress.last_study_date = active_date

    return progress
