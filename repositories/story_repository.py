"""
Story Repository
DGX AI Movie Studio

Data-access layer for the `stories` table.
All SQL for stories lives here; services and UI never touch SQLite directly.

A fresh connection is opened per method (and closed in `finally`). This is the
safest pattern under Streamlit, whose reruns can otherwise reuse a SQLite
connection across threads and raise "created in a thread" errors.
"""

from config.database import get_connection


class StoryRepository:

    def create(self, title, prompt, genre, style, scene_count,
               status="draft"):
        conn = get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO stories
                    (title, prompt, genre, style, scene_count, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (title, prompt, genre, style, scene_count, status),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get(self, story_id):
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM stories WHERE id = ?",
                (story_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def list_all(self):
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM stories ORDER BY created_at DESC, id DESC"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def update(self, story_id, title, prompt, genre, style, scene_count):
        conn = get_connection()
        try:
            conn.execute(
                """
                UPDATE stories
                SET title = ?, prompt = ?, genre = ?, style = ?,
                    scene_count = ?
                WHERE id = ?
                """,
                (title, prompt, genre, style, scene_count, story_id),
            )
            conn.commit()
        finally:
            conn.close()

    def update_status(self, story_id, status):
        conn = get_connection()
        try:
            conn.execute(
                "UPDATE stories SET status = ? WHERE id = ?",
                (status, story_id),
            )
            conn.commit()
        finally:
            conn.close()

    def delete(self, story_id):
        conn = get_connection()
        try:
            conn.execute("DELETE FROM stories WHERE id = ?", (story_id,))
            conn.commit()
        finally:
            conn.close()
