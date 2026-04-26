from __future__ import annotations

from typing import List, Dict, Optional

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except Exception:  # pragma: no cover - allows the game to run even if psycopg2 is missing
    psycopg2 = None
    RealDictCursor = None


# Change these values for your PostgreSQL installation.
DB_CONFIG = {
    "host": "localhost",
    "dbname": "Snake",
    "user": "postgres",
    "password": "RAFANADAL14!",
    "port": "5432"
}

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    score INTEGER NOT NULL,
    level_reached INTEGER NOT NULL,
    played_at TIMESTAMP DEFAULT NOW()
);
"""


class DatabaseManager:
    """Small helper around psycopg2 for saving scores and reading the leaderboard."""

    def __init__(self):
        self.available = psycopg2 is not None
        self.error_message = None
        if self.available:
            try:
                self.initialize_schema()
            except Exception as exc:
                self.available = False
                self.error_message = str(exc)

    def _connect(self):
        if psycopg2 is None:
            raise RuntimeError('psycopg2 is not installed.')
        return psycopg2.connect(**DB_CONFIG)

    def initialize_schema(self):
        """Create required tables if they do not exist yet."""
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(SCHEMA_SQL)
            conn.commit()

    def get_or_create_player(self, username: str) -> Optional[int]:
        """Return player id for a username. Create the player if needed."""
        if not self.available or not username:
            return None

        username = username.strip()[:50]
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO players (username)
                    VALUES (%s)
                    ON CONFLICT (username) DO NOTHING;
                    """,
                    (username,),
                )
                cur.execute("SELECT id FROM players WHERE username = %s;", (username,))
                row = cur.fetchone()
            conn.commit()
        return row[0] if row else None

    def save_session(self, username: str, score: int, level_reached: int) -> bool:
        """Save one finished game in the database."""
        if not self.available or not username:
            return False

        try:
            player_id = self.get_or_create_player(username)
            if player_id is None:
                return False

            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO game_sessions (player_id, score, level_reached)
                        VALUES (%s, %s, %s);
                        """,
                        (player_id, int(score), int(level_reached)),
                    )
                conn.commit()
            return True
        except Exception as exc:
            self.error_message = str(exc)
            return False

    def get_personal_best(self, username: str) -> Optional[int]:
        """Return best score for one player."""
        if not self.available or not username:
            return None

        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT MAX(gs.score)
                        FROM game_sessions gs
                        JOIN players p ON p.id = gs.player_id
                        WHERE p.username = %s;
                        """,
                        (username.strip()[:50],),
                    )
                    row = cur.fetchone()
            return row[0] if row and row[0] is not None else None
        except Exception as exc:
            self.error_message = str(exc)
            return None

    def get_top_scores(self, limit: int = 10) -> List[Dict]:
        """Return top scores for the leaderboard screen."""
        if not self.available:
            return []

        try:
            with self._connect() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT p.username,
                               gs.score,
                               gs.level_reached,
                               gs.played_at
                        FROM game_sessions gs
                        JOIN players p ON p.id = gs.player_id
                        ORDER BY gs.score DESC, gs.level_reached DESC, gs.played_at ASC
                        LIMIT %s;
                        """,
                        (int(limit),),
                    )
                    rows = cur.fetchall()
            return [dict(row) for row in rows]
        except Exception as exc:
            self.error_message = str(exc)
            return []
