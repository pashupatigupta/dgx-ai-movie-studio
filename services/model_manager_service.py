"""
Enterprise Model Manager Service
DGX AI Movie Studio
"""

from repositories.model_repository import ModelRepository
from services.model_service import ModelService


class ModelManagerService:

    def __init__(self):

        self.repository = ModelRepository()
        self.scanner = ModelService()


########################################################
# Refresh Models
########################################################

def refresh_models(self):

    models = self.scanner.scan()

    conn = self.repository.conn
    cursor = conn.cursor()

    cursor.execute("DELETE FROM models")

    sql = """
    INSERT INTO models(

        name,

        model_type,

        folder,

        path,

        size_mb,

        last_modified,

        family,

        purpose,

        vendor,

        version,

        framework,

        recommended,

        discovered_by

    )

    VALUES(

        ?,?,?,?,?,?,

        ?,?,?,?,?,?,?

    )
    """

    for model in models:

        cursor.execute(

            sql,

            (

                model["name"],

                model["type"],

                model["folder"],

                model["path"],

                model["size"],

                "",

                model["family"],

                model["purpose"],

                model["vendor"],

                model["version"],

                model["framework"],

                model["recommended"],

                model["discovered_by"]

            )

        )

    conn.commit()

    return len(models)
    ########################################################
    # Read Operations
    ########################################################

    def get_models(self):

        return self.repository.get_all()

    def get_enabled_models(self):

        return self.repository.get_enabled()

    def get_default_model(self):

        return self.repository.get_default()

    def get(self, model_id):

        return self.repository.get(model_id)

    def search(self, keyword):

        return self.repository.search(keyword)

    def filter(self, model_type):

        return self.repository.get_by_type(model_type)

    ########################################################
    # Update Operations
    ########################################################

    def enable(self, model_id):

        self.repository.enable(model_id)

    def disable(self, model_id):

        self.repository.disable(model_id)

    def set_default(self, model_id):

        self.repository.set_default(model_id)

    def update_tags(self, model_id, tags):

        self.repository.update_tags(
            model_id,
            tags
        )

    def update_description(
        self,
        model_id,
        description
    ):

        self.repository.update_description(
            model_id,
            description
        )

    def update_metadata(
        self,
        model_id,
        tags,
        description
    ):

        self.repository.update_metadata(
            model_id,
            tags,
            description
        )

    ########################################################
    # Statistics
    ########################################################

    def statistics(self):

        return self.repository.statistics()

    ########################################################
    # Cleanup
    ########################################################

    def close(self):

        self.repository.close()
