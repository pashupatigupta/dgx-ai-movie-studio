import sqlite3
from datetime import datetime

DATABASE = "database/movie_studio.db"


class PromptService:

    def __init__(self):

        self.conn = sqlite3.connect(
            DATABASE,
            check_same_thread=False
        )

        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()
######################################################

def get_categories(self):

    self.cursor.execute(
        """
        SELECT DISTINCT category
        FROM prompts
        WHERE category IS NOT NULL
        ORDER BY category
        """
    )

    return [row[0] for row in self.cursor.fetchall()]

######################################################

def get_by_category(self, category):

    self.cursor.execute(
        """
        SELECT *
        FROM prompts
        WHERE category=?
        ORDER BY id DESC
        """,
        (category,)
    )

    return self.cursor.fetchall()

######################################################

def get_statistics(self):

    self.cursor.execute(
        """
        SELECT

        COUNT(*),

        SUM(favorite),

        SUM(use_count)

        FROM prompts
        """
    )

    return self.cursor.fetchone()
    ######################################################

    def add_prompt(

        self,

        title,

        category,

        prompt,

        negative_prompt,

        model="SDXL",

        seed=0,

        width=1024,

        height=1024,

        steps=30,

        cfg=8.0

    ):

        self.cursor.execute(

            """
            INSERT INTO prompts(

                title,

                prompt,

                negative_prompt,

                model,

                seed,

                width,

                height,

                steps,

                cfg,

                category,

                favorite

            )

            VALUES(?,?,?,?,?,?,?,?,?,?,?)

            """,

            (

                title,

                prompt,

                negative_prompt,

                model,

                seed,

                width,

                height,

                steps,

                cfg,

                category,

                0

            )

        )

        self.conn.commit()

    ######################################################

    def get_prompts(self):

        self.cursor.execute(

            """

            SELECT *

            FROM prompts

            ORDER BY id DESC

            """

        )

        return self.cursor.fetchall()

    ######################################################

    def search_prompt(

        self,

        keyword

    ):

        self.cursor.execute(

            """

            SELECT *

            FROM prompts

            WHERE

            title LIKE ?

            OR

            prompt LIKE ?

            ORDER BY id DESC

            """,

            (

                f"%{keyword}%",

                f"%{keyword}%"

            )

        )

        return self.cursor.fetchall()

    ######################################################

    def delete_prompt(

        self,

        prompt_id

    ):

        self.cursor.execute(

            """

            DELETE FROM prompts

            WHERE id=?

            """,

            (

                prompt_id,

            )

        )

        self.conn.commit()

    ######################################################

    def favorite(

        self,

        prompt_id

    ):

        self.cursor.execute(

            """

            UPDATE prompts

            SET favorite=1

            WHERE id=?

            """,

            (

                prompt_id,

            )

        )

        self.conn.commit()

    ######################################################

    def update_usage(

        self,

        prompt_id

    ):

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

                prompt_id

            )

        )

        self.conn.commit()
