"""
Enterprise Model Repository
DGX AI Movie Studio
"""

from config.database import get_connection


class ModelRepository:

    def __init__(self):

        self.conn = get_connection()

        self.cursor = self.conn.cursor()

    ##################################################

    def close(self):

        self.conn.close()

    ##################################################

    def get_all(self):

        self.cursor.execute(
            """
            SELECT *
            FROM models
            ORDER BY
                model_type,
                name
            """
        )

        return [
            dict(row)
            for row in self.cursor.fetchall()
        ]

    ##################################################

    def get_enabled(self):

        self.cursor.execute(
            """
            SELECT *
            FROM models
            WHERE enabled=1
            ORDER BY
                model_type,
                name
            """
        )

        return [
            dict(row)
            for row in self.cursor.fetchall()
        ]

    ##################################################

    def get_default(self):

        self.cursor.execute(
            """
            SELECT *
            FROM models
            WHERE default_model=1
            LIMIT 1
            """
        )

        row = self.cursor.fetchone()

        if row:

            return dict(row)

        return None

    ##################################################

    def search(

        self,

        keyword

    ):

        self.cursor.execute(
            """
            SELECT *
            FROM models

            WHERE

                name LIKE ?

                OR

                model_type LIKE ?

                OR

                tags LIKE ?

                OR

                description LIKE ?

            ORDER BY name
            """,

            (

                f"%{keyword}%",

                f"%{keyword}%",

                f"%{keyword}%",

                f"%{keyword}%"

            )

        )

        return [

            dict(r)

            for r in self.cursor.fetchall()

        ]

    ##################################################

    def get_by_type(

        self,

        model_type

    ):

        self.cursor.execute(

            """
            SELECT *

            FROM models

            WHERE model_type=?

            ORDER BY name
            """,

            (

                model_type,

            )

        )

        return [

            dict(r)

            for r in self.cursor.fetchall()

        ]

    ##################################################

    def enable(

        self,

        model_id

    ):

        self.cursor.execute(

            """

            UPDATE models

            SET enabled=1

            WHERE id=?

            """,

            (

                model_id,

            )

        )

        self.conn.commit()

    ##################################################

    def disable(

        self,

        model_id

    ):

        self.cursor.execute(

            """

            UPDATE models

            SET enabled=0

            WHERE id=?

            """,

            (

                model_id,

            )

        )

        self.conn.commit()

    ##################################################

    def set_default(

        self,

        model_id

    ):

        self.cursor.execute(

            """

            UPDATE models

            SET default_model=0

            """

        )

        self.cursor.execute(

            """

            UPDATE models

            SET default_model=1

            WHERE id=?

            """,

            (

                model_id,

            )

        )

        self.conn.commit()

    ##################################################

    def update_metadata(

        self,

        model_id,

        tags,

        description

    ):

        self.cursor.execute(

            """

            UPDATE models

            SET

                tags=?,

                description=?

            WHERE id=?

            """,

            (

                tags,

                description,

                model_id

            )

        )

        self.conn.commit()

    ##################################################

    def statistics(self):

        self.cursor.execute(

            """

            SELECT

                COUNT(*) total,

                SUM(enabled) enabled,

                SUM(size_mb) total_size

            FROM models

            """

        )

        row = dict(

            self.cursor.fetchone()

        )

        self.cursor.execute(

            """

            SELECT

                model_type,

                COUNT(*) count

            FROM models

            GROUP BY model_type

            """

        )

        row["types"] = [

            dict(r)

            for r in self.cursor.fetchall()

        ]

        return row
