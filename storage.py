"""Human review audit log (SQLite)."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB = Path('data/reviews.sqlite3')

def initialize(path=DB):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, district TEXT NOT NULL, workflow_sha256 TEXT NOT NULL, reviewer TEXT NOT NULL, decision TEXT NOT NULL, notes TEXT NOT NULL)')
    return path

def save_review(district, digest, reviewer, decision, notes, path=DB):
    if decision not in ('approved', 'needs_evidence', 'rejected'):
        raise ValueError('Invalid decision')
    if not reviewer.strip() or not notes.strip():
        raise ValueError('Reviewer and justification are required')
    path = initialize(path)
    with sqlite3.connect(path) as db:
        cursor = db.execute('INSERT INTO reviews(created_at,district,workflow_sha256,reviewer,decision,notes) VALUES(?,?,?,?,?,?)', (datetime.now(timezone.utc).isoformat(), district, digest, reviewer.strip(), decision, notes.strip()))
        return cursor.lastrowid

def get_reviews(path=DB):
    path = initialize(path)
    with sqlite3.connect(path) as db:
        db.row_factory = sqlite3.Row
        return [dict(x) for x in db.execute('SELECT * FROM reviews ORDER BY id DESC')]