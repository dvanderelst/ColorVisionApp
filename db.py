import asyncio
import psycopg2
from env import DATABASE_URL


def _setup():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    id           SERIAL PRIMARY KEY,
                    team_name    TEXT        NOT NULL,
                    score        INTEGER     NOT NULL,
                    max_score    INTEGER     NOT NULL,
                    difficulty   TEXT        NOT NULL DEFAULT 'medium',
                    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
        conn.commit()


def _submit(team_name: str, score: int, max_score: int, difficulty: str):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO scores (team_name, score, max_score, difficulty) VALUES (%s, %s, %s, %s)",
                (team_name, score, max_score, difficulty),
            )
        conn.commit()


async def setup():
    await asyncio.to_thread(_setup)


async def submit(team_name: str, score: int, max_score: int, difficulty: str):
    await asyncio.to_thread(_submit, team_name, score, max_score, difficulty)


def _get_scores(start, end):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT team_name, score, max_score, difficulty, submitted_at
                FROM scores
                WHERE submitted_at >= %s AND submitted_at < %s
                ORDER BY score DESC
            """, (start, end))
            return cur.fetchall()


async def get_scores(start, end):
    return await asyncio.to_thread(_get_scores, start, end)
