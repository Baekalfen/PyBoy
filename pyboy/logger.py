#
# License: See LICENSE.md file
# GitHub: https://github.com/baekalfen/PyBoy
#

import logging

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
logging.basicConfig(format="%(relativeCreated)-8d %(name)-30s %(levelname)-8s %(message)s")


def log_level(level):
    if level == "DISABLE":
        logging.disable(level=logging.CRITICAL)
    else:
        logger.setLevel(getattr(logging, level))
