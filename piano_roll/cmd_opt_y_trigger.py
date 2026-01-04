#!/usr/bin/env python3
"""
Simple GUI for triggering FL Studio piano roll scripts via CMD+OPT+Y keyboard shortcut.

This is useful for triggering piano roll scripts like BeginLLMInteraction
that are bound to the CMD+OPT+Y key combination in FL Studio.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from pynput.keyboard import Key, Controller
from midi_controller.focus_management import activate_fl_studio


class CMDOptYTriggerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Create the simple PyQt5 interface."""
        self.setWindowTitle("FL Studio CMD+OPT+Y Trigger")
        self.resize(300, 200)
        self.setMinimumSize(250, 150)

        # Make window always on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
        """)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Title
        title = QLabel("Piano Roll Script Trigger")
        title.setFont(QFont("Helvetica Neue", 16, QFont.Bold))
        title.setStyleSheet("color: #ffcc00; padding: 5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(10)

        # Status label
        self.status_label = QLabel("Ready to trigger script")
        self.status_label.setFont(QFont("Helvetica Neue", 11))
        self.status_label.setStyleSheet("color: #00ff88; padding: 10px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addSpacing(10)

        # Trigger button
        self.trigger_btn = QPushButton("Trigger CMD+OPT+Y")
        self.trigger_btn.setMinimumHeight(60)
        self.trigger_btn.setFont(QFont("Helvetica Neue", 18, QFont.Bold))
        self.trigger_btn.setCursor(Qt.PointingHandCursor)
        self.trigger_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a6a9a;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #5a7aaa;
            }
            QPushButton:pressed {
                background-color: #3a5a8a;
            }
        """)
        self.trigger_btn.clicked.connect(self.trigger_script)
        layout.addWidget(self.trigger_btn)

    def trigger_script(self):
        """Send CMD+OPT+Y keystroke to trigger FL Studio script."""
        try:
            # First activate FL Studio window
            activate_fl_studio()

            # Small delay to ensure focus is established
            time.sleep(0.1)

            keyboard = Controller()

            # Press CMD and OPT together, then Y
            keyboard.press(Key.cmd)
            keyboard.press(Key.alt)
            time.sleep(0.05)

            keyboard.press('y')
            keyboard.release('y')
            time.sleep(0.05)

            keyboard.release(Key.alt)
            keyboard.release(Key.cmd)

            # Wait for script to execute
            time.sleep(0.5)

            self.status_label.setText("Script triggered!")
            self.status_label.setStyleSheet("color: #00ff88; padding: 10px;")

        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setStyleSheet("color: #ff4444; padding: 10px;")


def main():
    """Main entry point."""
    app = QApplication(sys.argv)

    # Set application-wide dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)

    window = CMDOptYTriggerUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
