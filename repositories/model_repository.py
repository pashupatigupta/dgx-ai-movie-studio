"""
Enterprise Model Repository
DGX AI Movie Studio
"""

from config.database import get_connection


class ModelRepository:

    def __init__(self):

        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    ############################################################
    # Read Operations
    ############################################################

    def get_all(self):

        self.cursor.execute(
            """
            SELECT *
            FROM models
            ORDER BY model_type,name
            """
        )

        return [
            dict(row)
            for row in self.cursor.fetchall()
        ]

    ############################################################

    def get(self, model_id):

        self.cursor.execute(
            """
            SELECT *
            FROM models
            WHERE id=?
            """,
            (model_id,)
        )

        row = self.cursor.fetchone()

        return dict(row) if row else None

    ############################################################

    def get_enabled(self):

        self.cursor.execute(
            """
            SELECT *
            FROM models
            WHERE enabled=1
            ORDER BY name
            """
        )

        return [
            dict(row)
            for row in self.cursor.fetchall()
        ]

    ############################################################

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

        return dict(row) if row else None

    ############################################################

    def search(self, keyword):

        keyword = f"%{keyword}%"

        self.cursor.execute(
            """
            SELECT *
            FROM models
            WHERE
                name LIKE ?
                OR model_type LIKE ?
                OR tags LIKE ?
                OR description LIKE ?
            ORDER BY name
            """,
            (
                keyword,
                keyword,
                keyword,
                keyword
            )
        )

        return [
            dict(row)
            for row in self.cursor.fetchall()
        ]

    ############################################################

    def get_by_type(self, model_type):

        self.cursor.execute(
            """
            SELECT *
            FROM models
            WHERE model_type=?
            ORDER BY name
            """,
            (model_type,)
        )

        return [
            dict(row)
            for row in self.cursor.fetchall()
        ]

    ############################################################
    # Update Operations
    ############################################################

    def enable(self, model_id):

        self.cursor.execute(
            """
            UPDATE models
            SET enabled=1
            WHERE id=?
            """,
            (model_id,)
        )

        self.conn.commit()

    ############################################################

    def disable(self, model_id):

        self.cursor.execute(
            """
            UPDATE models
            SET enabled=0
            WHERE id=?
            """,
            (model_id,)
        )

        self.conn.commit()

    ############################################################

    def set_default(self, model_id):

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
            (model_id,)
        )

        self.conn.commit()

    ############################################################

    def update_tags(self, model_id, tags):

        self.cursor.execute(
            """
            UPDATE models
            SET tags=?
            WHERE id=?
            """,
            (
                tags,
                model_id
            )
        )

        self.conn.commit()

    ############################################################

    def update_description(
        self,
        model_id,
        description
    ):

        self.cursor.execute(
            """
            UPDATE models
            SET description=?
            WHERE id=?
            """,
            (
                description,
                model_id
            )
        )

        self.conn.commit()

    ############################################################

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

    ############################################################
    # Statistics
    ############################################################

    def statistics(self):

        self.cursor.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(enabled) AS enabled,
                ROUND(SUM(size_mb),2) AS total_size
            FROM models
            """
        )

        stats = dict(self.cursor.fetchone())

        if stats["enabled"] is None:
            stats["enabled"] = 0

        if stats["total_size"] is None:
            stats["total_size"] = 0

        self.cursor.execute(
            """
            SELECT
                model_type,
                COUNT(*) AS count
            FROM models
            GROUP BY model_type
            ORDER BY model_type
            """
        )

        stats["types"] = [

            dict(row)

            for row in self.cursor.fetchall()

        ]

        return stats

    ############################################################

    def close(self):

        self.conn.close()

