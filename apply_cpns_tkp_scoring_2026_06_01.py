#!/usr/bin/env python3
"""Backfill CPNS-style TKP weighted scoring.

Real SKD scoring model:
- TWK/TIU: benar = 5, salah/kosong = 0.
- TKP: every option has value 1..5, no zero; best ASN behavior = 5.

This script preserves public option text, wraps legacy TKP options as
{"text": ..., "score": N}, keeps correct_answer as the 5-point option, and assigns
unique remaining scores 1..4 using deterministic ASN-behavior heuristics.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable

sys.path.insert(0, "/root/cpns/backend")

from sqlalchemy.orm.attributes import flag_modified  # noqa: E402
from db import SessionLocal  # noqa: E402
from models import Question  # noqa: E402

BACKUP_DIR = Path("/root/cpns/backups")
REPORT_PATH = Path("/root/cpns/cpns_tkp_scoring_report_2026_06_01.json")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_PATH = BACKUP_DIR / f"tkp_weighted_scoring_backup_{TIMESTAMP}.json"

GOOD_PATTERNS: list[tuple[str, int]] = [
    (r"\b(profesional|integritas|jujur|transparan|akuntabel|bertanggung jawab)\b", 80),
    (r"\b(koordinasi|berkoordinasi|diskusi|berdiskusi|komunikasi|mengomunikasikan|konsultasi|melapor|laporkan)\b", 70),
    (r"\b(atasan|pimpinan|tim|rekan kerja|stakeholder|pihak terkait)\b", 35),
    (r"\b(sesuai (aturan|prosedur|sop|ketentuan)|aturan|prosedur|sop|ketentuan|kode etik)\b", 70),
    (r"\b(melayani|pelayanan|membantu|mengarahkan|mendampingi|memfasilitasi|solusi|menyelesaikan)\b", 65),
    (r"\b(sabar|tenang|ramah|sopan|empati|menghargai|menghormati|toleran)\b", 55),
    (r"\b(inisiatif|proaktif|aktif|belajar|mempelajari|adaptasi|menyesuaikan|evaluasi|perbaikan)\b", 55),
    (r"\b(prioritas|mendahulukan|efektif|efisien|tepat waktu|target|kinerja|produktif)\b", 45),
    (r"\b(kepentingan (publik|masyarakat|organisasi)|masyarakat|publik|organisasi|instansi|kantor)\b", 45),
    (r"\b(data|bukti|fakta|klarifikasi|verifikasi|mencari tahu|memastikan)\b", 40),
]

BAD_PATTERNS: list[tuple[str, int]] = [
    (r"\b(marah|emosi|tersinggung|membentak|menyalahkan|bertengkar|konflik)\b", 85),
    (r"\b(mengabaikan|diam saja|membiarkan|tidak peduli|masa bodoh|acuh|cuek)\b", 85),
    (r"\b(menolak|menunda|menghindar|kabur|pergi|pulang|keluar|mengundurkan diri)\b", 75),
    (r"\b(bohong|berbohong|memalsukan|suap|gratifikasi|titipan|nepotisme|curang|melanggar)\b", 95),
    (r"\b(tanpa izin|sembarangan|asal|sesuka hati|seenaknya|langsung mengambil keputusan sendiri)\b", 70),
    (r"\b(menyuruh saja|menyerahkan sepenuhnya|bukan urusan|bukan tanggung jawab)\b", 65),
    (r"\b(hanya|cukup)\s+(diam|menunggu|melihat|menonton)\b", 60),
    (r"\b(pribadi|keluarga|teman)\b.*\b(diutamakan|lebih penting|dahulu|dulu)\b", 65),
]

MODERATE_PATTERNS: list[tuple[str, int]] = [
    (r"\b(mencoba|berusaha|bertanya|meminta bantuan|meminta saran)\b", 25),
    (r"\b(jika diminta|bila perlu|seperlunya|sesempatnya)\b", -15),
    (r"\b(sendiri|sendirian)\b", -10),
]


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def regex_score(text: str, patterns: Iterable[tuple[str, int]]) -> int:
    return sum(weight for pattern, weight in patterns if re.search(pattern, text))


def behavior_quality(text: str) -> int:
    t = norm(text)
    score = 100
    score += regex_score(t, GOOD_PATTERNS)
    score += regex_score(t, MODERATE_PATTERNS)
    score -= regex_score(t, BAD_PATTERNS)

    # Prefer complete answers that combine action + coordination/rules/service.
    if len(t.split()) >= 8:
        score += 8
    if len(t.split()) <= 3:
        score -= 20
    if "tetapi" in t or "namun" in t:
        score += 5
    if t.startswith(("tidak", "menolak", "mengabaikan", "membiarkan")):
        score -= 35
    return score


def clean_option(option) -> str:
    if isinstance(option, dict):
        return str(option.get("text", "")).strip()
    return str(option).strip()


def assign_tkp_scores(options: list, correct_answer: int) -> list[dict[str, int | str]]:
    texts = [clean_option(o) for o in options]
    if len(texts) != 5:
        raise ValueError(f"TKP question must have 5 options, got {len(texts)}")
    if not 0 <= correct_answer < 5:
        raise ValueError(f"Invalid correct_answer: {correct_answer}")

    # Best existing key gets 5. Remaining unique scores 1..4 by behavior quality.
    remaining = [i for i in range(5) if i != correct_answer]
    ranked = sorted(remaining, key=lambda i: (behavior_quality(texts[i]), -i), reverse=True)
    scores = {correct_answer: 5}
    for value, idx in zip([4, 3, 2, 1], ranked):
        scores[idx] = value

    return [{"text": texts[i], "score": int(scores[i])} for i in range(5)]


def is_weighted_tkp(q: Question) -> bool:
    opts = q.options if isinstance(q.options, list) else []
    return (
        q.section == "TKP"
        and len(opts) == 5
        and all(isinstance(o, dict) and "text" in o and "score" in o for o in opts)
        and sorted(int(o.get("score", 0)) for o in opts) == [1, 2, 3, 4, 5]
    )


def main() -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    db = SessionLocal()
    try:
        tkp = db.query(Question).filter(Question.section == "TKP").order_by(Question.id).all()
        backup_rows = []
        changed = []
        skipped = []

        for q in tkp:
            backup_rows.append({
                "id": q.id,
                "section": q.section,
                "topic": q.topic,
                "question_text": q.question_text,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "explanation": q.explanation,
            })

            if is_weighted_tkp(q):
                continue

            opts = q.options if isinstance(q.options, list) else []
            if len(opts) != 5 or q.correct_answer is None or not (0 <= int(q.correct_answer) < 5):
                skipped.append({"id": q.id, "reason": "invalid_options_or_key", "len": len(opts), "correct_answer": q.correct_answer})
                continue

            new_options = assign_tkp_scores(opts, int(q.correct_answer))
            q.options = new_options
            flag_modified(q, "options")
            changed.append({
                "id": q.id,
                "correct_answer": int(q.correct_answer),
                "scores": [o["score"] for o in new_options],
                "option_quality": [behavior_quality(str(o["text"])) for o in new_options],
            })

        with BACKUP_PATH.open("w", encoding="utf-8") as f:
            json.dump(backup_rows, f, ensure_ascii=False, indent=2)

        if skipped:
            db.rollback()
            raise RuntimeError(f"Skipped invalid TKP rows; rollback. Details: {skipped[:10]}")

        db.commit()

        # Verify after commit.
        bad = []
        for q in db.query(Question).filter(Question.section == "TKP").all():
            opts = q.options if isinstance(q.options, list) else []
            if not (
                len(opts) == 5
                and all(isinstance(o, dict) and isinstance(o.get("text"), str) and o.get("text", "").strip() for o in opts)
                and sorted(int(o.get("score", 0)) for o in opts) == [1, 2, 3, 4, 5]
                and 0 <= int(q.correct_answer) < 5
                and int(opts[int(q.correct_answer)]["score"]) == 5
            ):
                bad.append(q.id)

        report = {
            "backup": str(BACKUP_PATH),
            "tkp_total": len(tkp),
            "converted": len(changed),
            "already_weighted": len(tkp) - len(changed),
            "skipped": skipped,
            "verification_bad_ids": bad,
            "sample_converted": changed[:20],
        }
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(json.dumps(report, ensure_ascii=False, indent=2))
        if bad:
            raise SystemExit(2)
    finally:
        db.close()


if __name__ == "__main__":
    main()
