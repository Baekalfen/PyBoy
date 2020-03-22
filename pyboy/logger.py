#
# License: See LICENSE file
# GitHub: https://github.com/baekalfen/PyBoy
#

import logging

logger = logging.getLogger()


already_loaded = False

log_level = logging.INFO


def addconsolehandler():
    global already_loaded
    if not already_loaded:
        already_loaded = True
        logger.setLevel(log_level)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(log_level)

        # create formatter
        formatter = logging.Formatter('%(relativeCreated)-8d %(name)-30s %(levelname)-8s %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to Logger
        logger.addHandler(ch)
