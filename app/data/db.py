import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "cardking.sqlite3")

_SCHEMA = '''
CREATE TABLE IF NOT EXISTS comps_cache (
  card_key TEXT PRIMARY KEY,
  fetched_at_utc TEXT NOT NULL,
  comps_json TEXT NOT NULL,
  stats_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decision_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at_utc TEXT NOT NULL,
  request_json TEXT NOT NULL,
  response_json TEXT NOT NULL
);
'''

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.executescript(_SCHEMA)
    return conn
