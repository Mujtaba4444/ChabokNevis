from __future__ import annotations

import json
from datetime import date, datetime, timedelta


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


class SettingsRepo:
    def __init__(self, db):
        self.db = db

    def load(self) -> dict:
        out = {}
        for r in self.db.query("SELECT setting_key, setting_value FROM Settings"):
            try:
                out[r["setting_key"]] = json.loads(r["setting_value"])
            except ValueError:
                pass
        return out

    def save(self, key, value):
        self.db.execute(
            "INSERT INTO Settings(setting_key, setting_value) VALUES(?,?) "
            "ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value",
            (key, json.dumps(value)))


class UserRepo:
    def __init__(self, db):
        self.db = db

    def ensure_default(self):
        if not self.db.query("SELECT id FROM Users LIMIT 1"):
            self.db.execute("INSERT INTO Users(username, created_at) VALUES(?,?)", ("default", _now()))


class SessionRepo:
    def __init__(self, db):
        self.db = db

    def add(self, session_type, language, res: dict):
        self.db.execute(
            "INSERT INTO TypingSessions(session_type,language,wpm,accuracy,correct_characters,incorrect_characters,duration,created_at)"
            " VALUES(?,?,?,?,?,?,?,?)",
            (session_type, language, res["wpm"], res["accuracy"], res["correct_characters"],
             res["incorrect_characters"], res["duration"], _now()))

    def recent(self, limit=10, session_type=None):
        if session_type:
            return self.db.query("SELECT * FROM TypingSessions WHERE session_type=? ORDER BY id DESC LIMIT ?", (session_type, limit))
        return self.db.query("SELECT * FROM TypingSessions ORDER BY id DESC LIMIT ?", (limit,))

    def totals(self):
        return self.db.query(
            "SELECT COUNT(*) n, COALESCE(SUM(duration),0) t, COALESCE(AVG(wpm),0) avg_wpm, COALESCE(MAX(wpm),0) best_wpm,"
            " COALESCE(AVG(accuracy),0) avg_acc FROM TypingSessions")[0]


class LessonRepo:
    def __init__(self, db):
        self.db = db

    def sync(self, lessons):
        for l in lessons:
            self.db.execute("INSERT OR REPLACE INTO Lessons(id,title,level,language,difficulty,content) VALUES(?,?,?,?,?,?)",
                            (l.key, l.title, l.level, l.variant, l.difficulty, l.text or l.drill))

    def progress(self) -> dict:
        return {r["lesson_id"]: r for r in self.db.query("SELECT * FROM LessonProgress")}

    def record(self, key, wpm, acc, completed) -> bool:
        """Store best results. Returns True if the lesson was completed for the first time."""
        row = self.progress().get(key)
        if row is None:
            self.db.execute("INSERT INTO LessonProgress(lesson_id,completed,best_wpm,best_accuracy,completed_at) VALUES(?,?,?,?,?)",
                            (key, int(completed), wpm, acc, _now() if completed else None))
            return completed
        first = completed and not row["completed"]
        self.db.execute("UPDATE LessonProgress SET completed=?, best_wpm=?, best_accuracy=?, completed_at=? WHERE lesson_id=?",
                        (int(completed or row["completed"]), max(wpm, row["best_wpm"]), max(acc, row["best_accuracy"]),
                         _now() if first else row["completed_at"], key))
        return first


class DailyRepo:
    def __init__(self, db):
        self.db = db

    def add(self, day: str, seconds: float, lessons: int, chars: int):
        self.db.execute(
            "INSERT INTO DailyProgress(date,practice_duration,completed_lessons,total_characters) VALUES(?,?,?,?) "
            "ON CONFLICT(date) DO UPDATE SET practice_duration=practice_duration+excluded.practice_duration,"
            " completed_lessons=completed_lessons+excluded.completed_lessons, total_characters=total_characters+excluded.total_characters",
            (day, seconds, lessons, chars))

    def last_days(self, n: int) -> list[tuple[str, float]]:
        start = date.today() - timedelta(days=n - 1)
        rows = {r["date"]: r["practice_duration"] for r in
                self.db.query("SELECT date, practice_duration FROM DailyProgress WHERE date>=?", (start.isoformat(),))}
        days = [(start + timedelta(days=i)).isoformat() for i in range(n)]
        return [(d, rows.get(d, 0.0)) for d in days]
