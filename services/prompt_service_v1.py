import sqlite3

DATABASE = "database/movie_studio.db"


class PromptService:

    def __init__(self):

        self.connection = sqlite3.connect(
            DATABASE,
            check_same_thread=False
        )

        self.cursor = self.connection.cursor()

    def add_prompt(

        self,

        title,

        category,

        prompt,

        negative_prompt

    ):

        self.cursor.execute(

            """
            INSERT INTO prompts(

                title,

                category,

                prompt,

                negative_prompt

            )

            VALUES(?,?,?,?)

            """,

            (

                title,

                category,

                prompt,

                negative_prompt

            )

        )

        self.connection.commit()

    def get_prompts(self):

        self.cursor.execute(

            """
            SELECT *

            FROM prompts

            ORDER BY id DESC
            """

        )

        return self.cursor.fetchall()

    def delete_prompt(self, prompt_id):

        self.cursor.execute(

            """
            DELETE FROM prompts
            WHERE id=?
            """,

            (prompt_id,)

        )

        self.connection.commit()
