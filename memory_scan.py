"""
memory_scanner.py
=================
Automated WRAM scanner for PyBoy ROMs.

Works like Cheat Engine: you tell it what you expect a value to be,
it keeps narrowing down the candidate list until only one address remains.

Two modes
---------
WATCH   -- tracks which addresses change when something happens in the game
           (useful when you don't know the value, just that it changed)

SEARCH  -- filters addresses whose decoded value equals a known target
           (useful when you can read the value from the screen)

Both modes support a custom decoder so you can hunt BCD, signed bytes,
little-endian 16-bit, etc., not just raw bytes.

Usage
-----
Import and call from your own script, or run directly:

    python memory_scanner.py

The bottom of this file contains a ready-made example that finds the
score, lives, and level addresses for Pac-Man automatically.
"""

from __future__ import annotations

from typing import Callable

from pyboy import PyBoy

# ---------------------------------------------------------------------------
# Core scanner
# ---------------------------------------------------------------------------


class MemoryScanner:
    """
    Narrows down a set of WRAM address candidates through repeated filtering.

    Args:
        pyboy:   A running PyBoy instance.
        start:   First address to scan (default 0xC000).
        end:     Last address to scan, exclusive (default 0xE000).
        decoder: Function that turns a raw byte into a value for comparison.
                 Defaults to identity (raw byte).  Pass ``bcd`` for BCD scores.
    """

    def __init__(
        self,
        pyboy: PyBoy,
        start: int = 0xC000,
        end: int = 0xE000,
        decoder: Callable[[int], int] = lambda b: b,
    ):
        self._pyboy = pyboy
        self._start = start
        self._end = end
        self._decode = decoder
        self._snapshot: list[int] = self._read()
        self._candidates: list[int] = list(range(start, end))

    def _read(self) -> list[int]:
        return [self._pyboy.memory[a] for a in range(self._start, self._end)]

    def _snapshot_at(self, addr: int) -> int:
        return self._snapshot[addr - self._start]

    def _current(self, addr: int) -> int:
        return self._pyboy.memory[addr]

    # -- Filtering methods --------------------------------------------------

    def search(self, value: int) -> MemoryScanner:
        """
        Keep only addresses whose *current* decoded value equals ``value``.

        Call this when you can read the true value from the screen.

        Example — score just became 240::

            scanner.search(240)
        """
        self._candidates = [a for a in self._candidates if self._decode(self._current(a)) == value]
        return self

    def changed(self) -> MemoryScanner:
        """
        Keep only addresses that changed since the last ``snapshot()``.

        Call this after something happened in the game (ate a dot, died, etc.).
        """
        self._candidates = [a for a in self._candidates if self._current(a) != self._snapshot_at(a)]
        return self

    def unchanged(self) -> MemoryScanner:
        """Keep only addresses that have NOT changed since the last snapshot."""
        self._candidates = [a for a in self._candidates if self._current(a) == self._snapshot_at(a)]
        return self

    def increased(self) -> MemoryScanner:
        """Keep only addresses whose decoded value went up."""
        self._candidates = [
            a for a in self._candidates if self._decode(self._current(a)) > self._decode(self._snapshot_at(a))
        ]
        return self

    def decreased(self) -> MemoryScanner:
        """Keep only addresses whose decoded value went down."""
        self._candidates = [
            a for a in self._candidates if self._decode(self._current(a)) < self._decode(self._snapshot_at(a))
        ]
        return self

    def snapshot(self) -> MemoryScanner:
        """
        Save the current memory state as the new baseline for the next filter.

        Call this between game events::

            scanner.snapshot()
            # ... something happens in game ...
            scanner.changed()
        """
        self._snapshot = self._read()
        return self

    # -- Inspection ---------------------------------------------------------

    @property
    def candidates(self) -> list[int]:
        """Current list of candidate addresses."""
        return list(self._candidates)

    def reset(self) -> MemoryScanner:
        """Restore the full address range as candidates."""
        self._candidates = list(range(self._start, self._end))
        self.snapshot()
        return self

    def report(self, label: str = "") -> MemoryScanner:
        """Print the current candidate list with their decoded values."""
        tag = f"[{label}] " if label else ""
        print(f"{tag}{len(self._candidates)} candidates:")
        for a in self._candidates[:40]:
            raw = self._current(a)
            decoded = self._decode(raw)
            print(f"  0x{a:04X}  raw=0x{raw:02X}  decoded={decoded}")
        if len(self._candidates) > 40:
            print(f"  ... and {len(self._candidates) - 40} more")
        return self


# ---------------------------------------------------------------------------
# Decoder helpers
# ---------------------------------------------------------------------------


def bcd(b: int) -> int:
    """Packed-BCD byte → integer.  0x50 → 50, 0x99 → 99."""
    return (b >> 4) * 10 + (b & 0x0F)


def bcd_pair(lo: int, hi: int) -> int:
    """Two packed-BCD bytes → integer.  lo=0x40 hi=0x02 → 240."""
    return bcd(hi) * 100 + bcd(lo)


# ---------------------------------------------------------------------------
# Automated finder — runs the game, plays itself, narrows candidates
# ---------------------------------------------------------------------------


def _tick(pyboy: PyBoy, n: int, render: bool = False) -> None:
    for _ in range(n):
        pyboy.tick(1, render)


def find_addresses(rom_path: str) -> None:
    """
    Boot Pac-Man, let it run, and automatically narrow down:
      - score address   (BCD, increases when dots are eaten)
      - lives address   (decreases when Pac-Man dies)
      - level address   (increases when all dots are cleared)

    No human interaction required.
    """
    pyboy = PyBoy(rom_path, window="null")
    pyboy.set_emulation_speed(0)

    # Boot to title + start game
    _tick(pyboy, 700)
    pyboy.button("start")
    _tick(pyboy, 1)
    _tick(pyboy, 1000)

    print("=" * 60)
    print("Pac-Man WRAM scanner")
    print("=" * 60)

    # ----------------------------------------------------------------
    # SCORE  (BCD, increases when dots are eaten)
    # ----------------------------------------------------------------
    # Strategy:
    #   1. Snapshot memory.
    #   2. Move Pac-Man upward for a while so it eats dots.
    #   3. Filter to addresses whose BCD value increased.
    #   4. We know the on-screen score so we can call search() to confirm.

    score_scanner = MemoryScanner(pyboy, decoder=bcd)
    score_scanner.snapshot()

    # Eat dots by holding UP
    for _ in range(250):
        pyboy.button_press("up")
        pyboy.tick(1, False)
    pyboy.button_release("up")
    _tick(pyboy, 20)

    score_scanner.increased()
    score_scanner.report("score candidates after eating dots (BCD increased)")

    # ----------------------------------------------------------------
    # LIVES  (binary, decreases when Pac-Man dies)
    # ----------------------------------------------------------------
    # Strategy:
    #   1. Snapshot ALL memory right now.
    #   2. Wait for the game to kill Pac-Man on its own (ghosts will
    #      catch him within a few thousand frames with no input).
    #   3. Filter to addresses whose raw value decreased.

    lives_scanner = MemoryScanner(pyboy)
    lives_scanner.snapshot()

    # Run until a life is lost (lives at D641 goes from 2→1 or 1→0)
    # We don't know the address yet — that's what we're finding —
    # so just run for enough frames that a death is likely.
    print("\nWaiting for a death to find lives address...")
    for _ in range(6000):
        pyboy.tick(1, False)

    lives_scanner.decreased()
    # Further narrow: the value should be small (0-3 range for lives)
    lives_scanner._candidates = [a for a in lives_scanner.candidates if pyboy.memory[a] <= 3]
    lives_scanner.report("lives candidates after death (value decreased, ≤ 3)")

    # ----------------------------------------------------------------
    # LEVEL  (binary, stable — confirm with unchanged filter)
    # ----------------------------------------------------------------
    # Strategy:
    #   snapshot now, run more frames, keep only addresses that did NOT
    #   change AND whose current value is 1 (we're on level 1).

    level_scanner = MemoryScanner(pyboy)
    level_scanner.snapshot()
    _tick(pyboy, 500)
    level_scanner.unchanged()
    level_scanner._candidates = [a for a in level_scanner.candidates if pyboy.memory[a] == 1]
    level_scanner.report("level candidates (unchanged, value == 1)")

    pyboy.stop()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    rom = "pacman.gb"
    find_addresses(rom)


# ---------------------------------------------------------------------------
# Position finder — no known values needed
# ---------------------------------------------------------------------------


def find_positions(rom_path: str) -> None:
    """
    Find Pac-Man and ghost X/Y coordinates using only movement as the oracle.

    Strategy
    --------
    For X:  move RIGHT  → X increased  →  move LEFT  → X decreased
            intersection = X address candidates

    For Y:  move DOWN   → Y increased  →  move UP    → Y decreased
            intersection = Y address candidates

    Ghosts move on their own, so after locking down Pac-Man's address we
    repeat the same trick but hold Pac-Man still and wait for ghosts to
    move in a known direction, then filter the remaining candidates.
    """
    pyboy = PyBoy(rom_path, window="null")
    pyboy.set_emulation_speed(0)

    def tick(n, btn=None):
        for _ in range(n):
            if btn:
                pyboy.button_press(btn)
            pyboy.tick(1, False)
        if btn:
            pyboy.button_release(btn)

    # Boot to game
    tick(700)
    pyboy.button("start")
    tick(1)
    tick(1000)

    print("=" * 60)
    print("Position scanner  (no known values needed)")
    print("=" * 60)

    # ----------------------------------------------------------------
    # PAC-MAN X
    # ----------------------------------------------------------------
    x_scanner = MemoryScanner(pyboy)

    x_scanner.snapshot()
    tick(60, "right")  # move right  →  X went up
    x_scanner.increased()
    print(f"\nAfter moving RIGHT: {len(x_scanner.candidates)} candidates")

    x_scanner.snapshot()
    tick(60, "left")  # move left   →  X went down
    x_scanner.decreased()
    print(f"After moving LEFT:  {len(x_scanner.candidates)} candidates")

    # One more pass to eliminate noise
    x_scanner.snapshot()
    tick(60, "right")
    x_scanner.increased()
    x_scanner.report("Pac-Man X candidates")

    # ----------------------------------------------------------------
    # PAC-MAN Y
    # ----------------------------------------------------------------
    y_scanner = MemoryScanner(pyboy)

    y_scanner.snapshot()
    tick(60, "down")  # move down   →  Y went up
    y_scanner.increased()
    print(f"\nAfter moving DOWN: {len(y_scanner.candidates)} candidates")

    y_scanner.snapshot()
    tick(60, "up")  # move up     →  Y went down
    y_scanner.decreased()
    print(f"After moving UP:   {len(y_scanner.candidates)} candidates")

    y_scanner.snapshot()
    tick(60, "down")
    y_scanner.increased()
    y_scanner.report("Pac-Man Y candidates")

    # ----------------------------------------------------------------
    # GHOSTS
    # Ghost positions are harder because we can't control them directly.
    # Strategy: hold Pac-Man still, wait for ghosts to move horizontally
    # (watch the screen), snapshot before and after, filter changed.
    # Repeat for the other axis.
    # Then eliminate any address already identified as Pac-Man X or Y.
    # ----------------------------------------------------------------
    pacman_x_addrs = set(x_scanner.candidates)
    pacman_y_addrs = set(y_scanner.candidates)

    ghost_scanner = MemoryScanner(pyboy)

    print("\nWaiting for ghosts to move (holding Pac-Man still)...")
    ghost_scanner.snapshot()
    tick(300)  # ghosts will move on their own

    ghost_scanner.changed()
    # Remove Pac-Man's own addresses from the ghost candidates
    ghost_scanner._candidates = [
        a for a in ghost_scanner.candidates if a not in pacman_x_addrs and a not in pacman_y_addrs
    ]

    # Ghost coordinates should be small screen-space values (< 200)
    ghost_scanner._candidates = [a for a in ghost_scanner.candidates if pyboy.memory[a] < 200]

    ghost_scanner.report("Ghost position candidates (changed, value < 200, not Pac-Man)")

    pyboy.stop()


if __name__ == "__main__":
    rom = "pacman.gb"
    # find_addresses(rom)
    # print("\n")
    find_positions(rom)
