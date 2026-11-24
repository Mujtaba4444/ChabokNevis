from __future__ import annotations

from datetime import date

from ..database.repositories import DailyRepo, LessonRepo, SessionRepo


class ProgressService:
    def __init__(self, db):
        self.sessions, self.lessons, self.daily = SessionRepo(db), LessonRepo(db), DailyRepo(db)

    def record_session(self, session_type, language, res, lesson_key=None, lesson_completed=False) -> bool:
        """Persist a finished session. Returns True if a lesson was newly completed."""
        self.sessions.add(session_type, language, res)
        newly = False
        if lesson_key:
            newly = self.lessons.record(lesson_key, res["wpm"], res["accuracy"], lesson_completed)
        self.daily.add(date.today().isoformat(), res["duration"], int(newly), res["total_characters"])
        return newly

    def summary(self) -> dict:
        t = self.sessions.totals()
        today = self.daily.last_days(1)[0][1]
        return {"sessions": t["n"], "total_seconds": t["t"], "avg_wpm": t["avg_wpm"], "best_wpm": t["best_wpm"],
                "avg_accuracy": t["avg_acc"], "today_seconds": today}

    def completed_keys(self) -> set[str]:
        return {k for k, r in self.lessons.progress().items() if r["completed"]}
