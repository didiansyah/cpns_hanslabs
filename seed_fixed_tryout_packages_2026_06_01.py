#!/usr/bin/env python3
"""Create fixed SKD tryout packages (Part 1..10)."""
from __future__ import annotations

import random
import sys
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

load_dotenv('/root/cpns/backend/.env')
sys.path.insert(0, '/root/cpns/backend')

from db import engine, SessionLocal, Base  # noqa: E402
from models import Question, TryoutPackage  # noqa: E402


def ensure_schema():
    Base.metadata.create_all(bind=engine, tables=[TryoutPackage.__table__])
    with engine.begin() as conn:
        cols = [row[0] for row in conn.exec_driver_sql('SHOW COLUMNS FROM simulations').fetchall()]
        if 'package_id' not in cols:
            conn.exec_driver_sql('ALTER TABLE simulations ADD COLUMN package_id INT NULL AFTER sim_type')
            conn.exec_driver_sql('CREATE INDEX ix_simulations_package_id ON simulations (package_id)')


def usable(q: Question) -> bool:
    opts = q.options if isinstance(q.options, list) else []
    if len(opts) != 5 or q.correct_answer is None:
        return False
    if q.section == 'TKP':
        return all(isinstance(o, dict) and 'text' in o and 'score' in o for o in opts)
    return all(isinstance(o, str) and o.strip() for o in opts)


def main():
    ensure_schema()
    db = SessionLocal()
    try:
        existing = db.query(TryoutPackage).count()
        if existing >= 10:
            print(f'tryout_packages already seeded: {existing}')
            return

        by_section = defaultdict(list)
        for q in db.query(Question).order_by(Question.id.asc()).all():
            if q.section in ('TWK', 'TIU', 'TKP') and usable(q):
                by_section[q.section].append(q.id)

        needed = {'TWK': 30 * 10, 'TIU': 35 * 10, 'TKP': 45 * 10}
        for sec, n in needed.items():
            if len(by_section[sec]) < n:
                raise RuntimeError(f'Not enough {sec}: have {len(by_section[sec])}, need {n}')
            random.Random(20260601 + len(sec)).shuffle(by_section[sec])

        db.query(TryoutPackage).delete()
        for part in range(1, 11):
            offset = part - 1
            question_ids = {
                'TWK': by_section['TWK'][offset * 30:(offset + 1) * 30],
                'TIU': by_section['TIU'][offset * 35:(offset + 1) * 35],
                'TKP': by_section['TKP'][offset * 45:(offset + 1) * 45],
            }
            db.add(TryoutPackage(
                part_number=part,
                title=f'Try Out SKD CASN 2026 – Part {part}',
                sim_type='full',
                question_ids=question_ids,
                is_active=True,
            ))
        db.commit()
        print('seeded 10 fixed SKD packages')
        print({sec: len(ids) for sec, ids in by_section.items()})
    finally:
        db.close()


if __name__ == '__main__':
    main()
