# -*- encoding: utf-8 -*-
#
# Authors: Mads Ynddal
# License: See LICENSE file
# GitHub: https://github.com/baekalfen/PyBoy
#

import logging

logger = logging.getLogger()

def addConsoleHandler():
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(relativeCreated)-8d %(levelname)-8s %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to Logger
    logger.addHandler(ch)
