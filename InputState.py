"""Input state as plain data, decoupled from pygame's event system — this
means Game.update() can be driven by real keyboard input in main.py, or by
directly-constructed InputState objects in tests, with identical logic either way.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InputState:
    thrust: bool = False
    rotate_left: bool = False
    rotate_right: bool = False
    shoot: bool = False

    @property
    def rotate_direction(self) -> int:
        """-1 for left, +1 for right, 0 if neither/both are pressed."""
        if self.rotate_left and not self.rotate_right:
            return -1
        if self.rotate_right and not self.rotate_left:
            return 1
        return 0