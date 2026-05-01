import json
import sqlite3
from datetime import date, datetime
from pathlib import Path

from market_agent.models import Candidate, PricePoint, ScoredCandidate


class Repository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS watchlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tracking_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
            """)

    def save_watchlist(self, created_at: datetime, candidates: list[ScoredCandidate]) -> None:
        payload = [
            {
                "score": item.score,
                "candidate": {
                    **item.candidate.__dict__,
                    "data_timestamp": item.candidate.data_timestamp.isoformat() if item.candidate.data_timestamp else None,
                    "market_date": item.candidate.market_date.isoformat() if item.candidate.market_date else None,
                    "fetched_at": item.candidate.fetched_at.isoformat() if item.candidate.fetched_at else None,
                },
            }
            for item in candidates
        ]
        with self._connect() as conn:
            conn.execute("INSERT INTO watchlists (created_at, payload) VALUES (?, ?)", (created_at.isoformat(), json.dumps(payload)))

    def load_latest_watchlist(self) -> list[ScoredCandidate]:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM watchlists ORDER BY id DESC LIMIT 1").fetchone()
        if row is None:
            return []
        payload = json.loads(row[0])
        watchlist: list[ScoredCandidate] = []
        for item in payload:
            candidate_payload = item["candidate"]
            if candidate_payload.get("data_timestamp"):
                candidate_payload["data_timestamp"] = datetime.fromisoformat(candidate_payload["data_timestamp"])
            if candidate_payload.get("market_date"):
                candidate_payload["market_date"] = date.fromisoformat(candidate_payload["market_date"])
            if candidate_payload.get("fetched_at"):
                candidate_payload["fetched_at"] = datetime.fromisoformat(candidate_payload["fetched_at"])
            watchlist.append(ScoredCandidate(Candidate(**candidate_payload), item["score"]))
        return watchlist

    def save_tracking_snapshot(self, created_at: datetime, prices: list[PricePoint]) -> None:
        payload = [
            {
                **point.__dict__,
                "data_timestamp": point.data_timestamp.isoformat(),
                "market_date": point.market_date.isoformat() if point.market_date else None,
            }
            for point in prices
        ]
        with self._connect() as conn:
            conn.execute("INSERT INTO tracking_snapshots (created_at, payload) VALUES (?, ?)", (created_at.isoformat(), json.dumps(payload)))
