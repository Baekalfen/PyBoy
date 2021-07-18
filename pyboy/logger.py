#
# License: See LICENSE.md file
# GitHub: https://github.com/baekalfen/PyBoy
#

import logging
import os

LOGLEVEL = os.environ.get("PYBOY_LOGLEVEL", "INFO")

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(relativeCreated)-8d %(name)-30s %(levelname)-8s %(message)s"))

logger = logging.getLogger("pyboy")
logger.setLevel(LOGLEVEL)
logger.addHandler(handler)


def log_level(level):
    if level == "DISABLE":
        logging.disable(level=logging.CRITICAL)
    else:
        logger.setLevel(level)
