"""
Minimal file-based persistence layer.
Good enough for a student prototype; swap for a real database
(Postgres/MongoDB via SQLAlchemy/PyMongo) by re-implementing
these four functions.
"""
import json
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "entries.json")


def read_all():
    try:
        if not os.path.exists(DB_FILE):
            return []
        with open(DB_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            return json.loads(content) if content else []
    except Exception as e:
        print("store.read_all failed:", e)
        return []


def write_all(entries):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
        return True
    except Exception as e:
        print("store.write_all failed:", e)
        return False


def add_entry(entry):
    entries = read_all()
    entries.append(entry)
    write_all(entries)
    return entry


def clear_all():
    write_all([])
