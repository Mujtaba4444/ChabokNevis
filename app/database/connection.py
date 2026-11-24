from __future__ import annotations

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS Users(id INTEGER PRIMARY KEY, username TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS Lessons(id TEXT PRIMARY KEY, title TEXT, level INTEGER, language TEXT, difficulty INTEGER, content TEXT);
CREATE TABLE IF NOT EXISTS LessonProgress(id INTEGER PRIMARY KEY, lesson_id TEXT UNIQUE NOT NULL, completed INTEGER DEFAULT 0,
  best_wpm REAL DEFAULT 0, best_accuracy REAL DEFAULT 0, completed_at TEXT);
CREATE TABLE IF NOT EXISTS TypingSessions(id INTEGER PRIMARY KEY, session_type TEXT NOT NULL, language TEXT, wpm REAL, accuracy REAL,
  correct_characters INTEGER, incorrect_characters INTEGER, duration REAL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS DailyProgress(id INTEGER PRIMARY KEY, date TEXT UNIQUE NOT NULL, practice_duration REAL DEFAULT 0,
  completed_lessons INTEGER DEFAULT 0, total_characters INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS Settings(setting_key TEXT PRIMARY KEY, setting_value TEXT);
"""


class Database:
    """Thin SQLite wrapper. Every write is committed immediately (safe on crash)."""

    def __init__(self, path):
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def execute(self, sql, params=()):
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur

    def query(self, sql, params=()):
        return self.conn.execute(sql, params).fetchall()

    def close(self):
        self.conn.close()
