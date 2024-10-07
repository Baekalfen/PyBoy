import sys

from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import Qt, QSize

from OpenGL.GL import (glPixelZoom)

from pyboy import PyBoy
from pyboy.utils import WindowEvent

ROWS, COLS = 144, 160

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    print("Usage: python opengl_qt.py [ROM file]")
    exit(1)


class PyBoyOpenGL(QOpenGLWidget):
    def __init__(self, pyboy: PyBoy, parent=None):
        super().__init__(parent=parent)
        self.pyboy = pyboy
        self.setFormat(QSurfaceFormat.defaultFormat())
        self.setUpdatesEnabled(True)

        self.update()

    def paintGL(self):
        self.pyboy.tick()
        self.update()

    def resizeGL(self, width, height):
        glPixelZoom(width / COLS, height / ROWS)


class PyBoyWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.pyboy = PyBoy(filename, window="OpenGLHeadless")

        self.game_widget = PyBoyOpenGL(self.pyboy)

        self.setCentralWidget(self.game_widget)
        self.resize(800, 600)
        self.setWindowTitle("PyBoy OpenGL")

        self.show()

    def keyPressEvent(self, event):
        """Handle key press events"""
        key = event.key()
        if key == Qt.Key.Key_A:
            self.pyboy.events.append(WindowEvent(WindowEvent.PRESS_BUTTON_A))
        elif key == Qt.Key.Key_S:
            self.pyboy.events.append(WindowEvent(WindowEvent.PRESS_BUTTON_B))
        elif key == Qt.Key.Key_Up:
            self.pyboy.events.append(WindowEvent(WindowEvent.PRESS_ARROW_UP))
        elif key == Qt.Key.Key_Down:
            self.pyboy.events.append(WindowEvent(WindowEvent.PRESS_ARROW_DOWN))
        elif key == Qt.Key.Key_Left:
            self.pyboy.events.append(WindowEvent(WindowEvent.PRESS_ARROW_LEFT))
        elif key == Qt.Key.Key_Right:
            self.pyboy.events.append(WindowEvent(WindowEvent.PRESS_ARROW_RIGHT))
        elif key == Qt.Key.Key_Z:
            self.pyboy.events.append(WindowEvent(WindowEvent.STATE_SAVE))
        elif key == Qt.Key.Key_X:
            self.pyboy.events.append(WindowEvent(WindowEvent.STATE_LOAD))
        elif key == Qt.Key.Key_Return:
            self.pyboy.events.append(WindowEvent(WindowEvent.PRESS_BUTTON_START))
        elif key == Qt.Key.Key_Backspace:
            self.pyboy.events.append(WindowEvent(WindowEvent.PRESS_BUTTON_SELECT))
        elif key == Qt.Key.Key_Space:
            self.pyboy.events.append(WindowEvent(WindowEvent.PRESS_SPEED_UP))
        elif key == Qt.Key.Key_Escape:
            self.pyboy.events.append(WindowEvent(WindowEvent.QUIT))

    def keyReleaseEvent(self, event):
        """Handle key release events"""
        key = event.key()
        if key == Qt.Key.Key_A:
            self.pyboy.events.append(WindowEvent(WindowEvent.RELEASE_BUTTON_A))
        elif key == Qt.Key.Key_S:
            self.pyboy.events.append(WindowEvent(WindowEvent.RELEASE_BUTTON_B))
        elif key == Qt.Key.Key_Up:
            self.pyboy.events.append(WindowEvent(WindowEvent.RELEASE_ARROW_UP))
        elif key == Qt.Key.Key_Down:
            self.pyboy.events.append(WindowEvent(WindowEvent.RELEASE_ARROW_DOWN))
        elif key == Qt.Key.Key_Left:
            self.pyboy.events.append(WindowEvent(WindowEvent.RELEASE_ARROW_LEFT))
        elif key == Qt.Key.Key_Right:
            self.pyboy.events.append(WindowEvent(WindowEvent.RELEASE_ARROW_RIGHT))
        elif key == Qt.Key.Key_Space:
            self.pyboy.events.append(WindowEvent(WindowEvent.RELEASE_SPEED_UP))
        elif key == Qt.Key.Key_Backspace:
            self.pyboy.events.append(WindowEvent(WindowEvent.RELEASE_BUTTON_SELECT))
        elif key == Qt.Key.Key_Return:
            self.pyboy.events.append(WindowEvent(WindowEvent.RELEASE_BUTTON_START))

    def resizeEvent(self, event):
        # Resize the game widget while keeping the aspect ratio
        size = event.size()
        width, height = size.width(), size.height()
        aspect_ratio = COLS / ROWS
        if width / height > aspect_ratio:
            width = height * aspect_ratio
        else:
            height = width / aspect_ratio
        self.game_widget.resize(QSize(int(width), int(height)))
        self.game_widget.move(int((size.width() - width) / 2), int((size.height() - height) / 2))


if __name__ == "__main__":
    app = QApplication([])
    window = PyBoyWindow()
    sys.exit(app.exec())
