import os
import sys
from sqlalchemy import text

sys.path.insert(0, "/root/cpns/backend")
from db import engine

with engine.begin() as conn:
    cols = [row[0] for row in conn.execute(text("SHOW COLUMNS FROM simulations"))]
    if "submitted_at" not in cols:
        conn.execute(text("ALTER TABLE simulations ADD COLUMN submitted_at DATETIME NULL AFTER questions_data"))
        print("added simulations.submitted_at")
    else:
        print("simulations.submitted_at already exists")
