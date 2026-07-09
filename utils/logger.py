import logging

from config.settings import LOG_DIR

LOG_DIR.mkdir(
    exist_ok=True
)

logging.basicConfig(

    filename=LOG_DIR/"movie_studio.log",

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("DGX")