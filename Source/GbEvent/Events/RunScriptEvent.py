# -*- encoding: utf-8 -*-
#
# Authors: Thomas Li Fredriksen
# License: See LICENSE file
# GitHub: https://github.com/thomafred/PyBoy
#

from GbEvent.GbEvent import GbEvent
from .. import GbEventId

import sys
import os

from GbLogger import gblogger


SCRIPT_DIR = os.path.join(os.getcwd(), 'scripts')


class RunScriptEvent(GbEvent):
    """Event to handle loading and running scripts"""

    _ID = GbEventId.RUN_SCRIPT


    def __init__(self, system, eventHandler, scriptPath):
        """
        :param system: GB System state
        :param eventHandler: Input handler
        :param scriptPath: Script name with path
        """
        super(self.__class__, self).__init__(system, eventHandler)

        self._scriptPath = scriptPath

    def do_call(self):
        """Event callback"""

        ext_module = None

        # Convert input path to absolute if necessary
        if not os.path.isabs(self._scriptPath):
            self._scriptPath = os.path.join(SCRIPT_DIR, self._scriptPath)

        # Assert file existence and validity
        if not os.path.isfile(self._scriptPath):
            gblogger.error('File does not exist: "{}"'.format(self._scriptPath))
            return
        elif self._scriptPath[-3:] != '.py':
            gblogger.error('Invalid file extension in filename: {}'.format(
                os.path.basename(self._scriptPath)))
            return

        # Append PYTHONPATH
        pythonPath = sys.path[:]
        sys.path.append(os.path.dirname(self._scriptPath[:-3]))

        # Import module by basename
        bname = os.path.basename(self._scriptPath[:-3])
        try:
            if bname in sys.modules:
                reload(bname)
                ext_module = sys.modules[bname]
            else:
                ext_module = __import__(bname)
        except ImportError:
            gblogger.error('Unable import file: {}'.format(self._scriptPath))
            gblogger.debug(sys.path)
        except Exception as e:
            gblogger.exception(e)

        # Undo import when finished
        sys.path = pythonPath[:]

        if not ext_module == None:
            del sys.modules[bname]
        else:
            gblogger.debug('Module not deleted')
