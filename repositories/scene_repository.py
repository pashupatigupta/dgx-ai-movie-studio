"""
Scene Repository
DGX AI Movie Studio

Data-access layer for the `scenes` table.
One fresh connection per method (Streamlit-safe), same as StoryRepository.
"""

from config.database import get_connection


class SceneRepository:

    def create(self, story_id, scene_number, title, description,
               status="draft"):
        conn = get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO scenes
                    (story_id, scene_number, title, description, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (story_id, scene_number, title, description, status),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get(self, scene_id):
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM scenes WHERE id = ?",
                (scene_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def list_by_story(self, story_id):
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT * FROM scenes
                WHERE story_id = ?
                ORDER BY scene_number ASC, id ASC
                """,
                (story_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def update_content(self, scene_id, title, description):
        conn = get_connection()
        try:
            conn.execute(
                "UPDATE scenes SET title = ?, description = ? WHERE id = ?",
                (title, description, scene_id),
            )
            conn.commit()
        finally:
            conn.close()

    def update_image(self, scene_id, image_path, status="image_ready"):
        conn = get_connection()
        try:
            conn.execute(
                "UPDATE scenes SET image_path = ?, status = ? WHERE id = ?",
                (image_path, status, scene_id),
            )
            conn.commit()
        finally:
            conn.close()

    def delete_by_story(self, story_id):
        conn = get_connection()
        try:
            conn.execute(
                "DELETE FROM scenes WHERE story_id = ?", (story_id,)
            )
            conn.commit()
        finally:
            conn.close()
