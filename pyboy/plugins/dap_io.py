#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""Low-level Debug Adapter Protocol (DAP) message framing over a binary stream.

DAP messages are JSON objects sent over stdio (or a socket) using the same
`Content-Length` header framing as the Language Server Protocol:

    Content-Length: <n>\r\n
    \r\n
    <n bytes of UTF-8 encoded JSON>

This module only deals with reading/writing these frames. Protocol-level
semantics (requests/responses/events) live in `pyboy_dap.adapter`.
"""

import json
import threading


class DAPReader:
    """Reads DAP-framed JSON messages from a binary input stream."""

    def __init__(self, stream):
        self._stream = stream

    def read_message(self):
        """Reads a single DAP message, or returns None on EOF."""
        headers = {}
        while True:
            line = self._stream.readline()
            if not line:
                return None  # EOF
            line = line.decode("utf-8", errors="replace").strip("\r\n")
            if line == "":
                break
            if ":" in line:
                key, _, value = line.partition(":")
                headers[key.strip().lower()] = value.strip()

        length = int(headers.get("content-length", 0))
        if length <= 0:
            return {}

        body = self._read_exact(length)
        return json.loads(body.decode("utf-8"))

    def _read_exact(self, n):
        chunks = []
        remaining = n
        while remaining > 0:
            chunk = self._stream.read(remaining)
            if not chunk:
                raise EOFError("Unexpected EOF while reading DAP message body")
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)


class DAPWriter:
    """Writes DAP-framed JSON messages to a binary output stream.

    Thread-safe: multiple threads (e.g. the request-handling thread and the
    emulator thread reporting a `stopped` event) may write concurrently.
    """

    def __init__(self, stream):
        self._stream = stream
        self._lock = threading.Lock()

    def write_message(self, message):
        body = json.dumps(message).encode("utf-8")
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
        with self._lock:
            self._stream.write(header)
            self._stream.write(body)
            self._stream.flush()
