"""
Enterprise Prompt Library Service
DGX AI Movie Studio
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DATABASE = Path("database/movie_studio.db")


class PromptService:

    def __init__(self):

        self.conn = sqlite3.connect(DATABASE)

        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()

    ############################################################

    def close(self):

        self.conn.close()

    ############################################################

    def add_prompt(
        self,
        title,
        category,
        prompt,
        negative_prompt="",
        model="SDXL",
        width=1024,
        height=1024,
        steps=30,
        cfg=8.0,
        seed=0,
    ):

        self.cursor.execute(
            """
            INSERT INTO prompts
            (
                title,
                category,
                prompt,
                negative_prompt,
                model,
                width,
                height,
                steps,
                cfg,
                seed
            )
            VALUES
            (
                ?,?,?,?,?,?,?,?,?,?
            )
            """,
            (
                title,
                category,
                prompt,
                negative_prompt,
                model,
                width,
                height,
                steps,
                cfg,
                seed,
            ),
        )

        self.conn.commit()

        return self.cursor.lastrowid

    ############################################################

    def list_prompts(self):

        self.cursor.execute(
            """
            SELECT *
            FROM prompts
            ORDER BY id DESC
            """
        )

        return self.cursor.fetchall()

    ############################################################

    def search(self, keyword):

        keyword = f"%{keyword}%"

        self.cursor.execute(
            """
            SELECT *
            FROM prompts
            WHERE
                title LIKE ?
                OR prompt LIKE ?
                OR category LIKE ?
            ORDER BY id DESC
            """,
            (
                keyword,
                keyword,
                keyword,
            ),
        )

        return self.cursor.fetchall()

    ############################################################

    def get_categories(self):

        self.cursor.execute(
            """
            SELECT DISTINCT category
            FROM prompts
            ORDER BY category
            """
        )

        rows = self.cursor.fetchall()

        return [r["category"] for r in rows if r["category"]]

    ############################################################

    def get_by_category(self, category):

        self.cursor.execute(
            """
            SELECT *
            FROM prompts
            WHERE category=?
            ORDER BY id DESC
            """,
            (category,),
        )

        return self.cursor.fetchall()

    ############################################################

    def favorite(self, prompt_id):

        self.cursor.execute(
            """
            UPDATE prompts
            SET favorite=1
            WHERE id=?
            """,
            (prompt_id,),
        )

        self.conn.commit()

    ############################################################

    def unfavorite(self, prompt_id):

        self.cursor.execute(
            """
            UPDATE prompts
            SET favorite=0
            WHERE id=?
            """,
            (prompt_id,),
        )

        self.conn.commit()

    ############################################################

    def get_favorites(self):

        self.cursor.execute(
            """
            SELECT *
            FROM prompts
            WHERE favorite=1
            ORDER BY id DESC
            """
        )

        return self.cursor.fetchall()

    ############################################################

    def update_usage(self, prompt_id):

        self.cursor.execute(
            """
            UPDATE prompts

            SET

            last_used=?,

            use_count=use_count+1

            WHERE id=?
            """,
            (
                datetime.now(),
                prompt_id,
            ),
        )

        self.conn.commit()

    ############################################################

    def most_used(self, limit=10):

        self.cursor.execute(
            """
            SELECT *
            FROM prompts
            ORDER BY use_count DESC,id DESC
            LIMIT ?
            """,
            (limit,),
        )

        return self.cursor.fetchall()

    ############################################################

    def recent(self, limit=10):

        self.cursor.execute(
            """
            SELECT *
            FROM prompts
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        )

        return self.cursor.fetchall()

    ############################################################

    def delete_prompt(self, prompt_id):

        self.cursor.execute(
            """
            DELETE
            FROM prompts
            WHERE id=?
            """,
            (prompt_id,),
        )

        self.conn.commit()

    ############################################################

    def get_statistics(self):

        self.cursor.execute(
            """
            SELECT

                COUNT(*) total,

                SUM(favorite) favorites,

                SUM(use_count) total_used

            FROM prompts
            """
        )

        row = self.cursor.fetchone()

        return {

            "total": row["total"] or 0,

            "favorites": row["favorites"] or 0,

            "used": row["total_used"] or 0,

            "categories": len(self.get_categories())

        }

    ############################################################

    def export(self):

        self.cursor.execute(
            """
            SELECT *
            FROM prompts
            ORDER BY id DESC
            """
        )

        return [dict(r) for r in self.cursor.fetchall()]

    ############################################################

    def get(self, prompt_id):

        self.cursor.execute(
            """
            SELECT *
            FROM prompts
            WHERE id=?
            """,
            (prompt_id,),
        )

        return self.cursor.fetchone()
