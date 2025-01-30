import sys
import cv2
import numpy as np
import asyncio
import websockets
import re
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow
from mss import mss
import pytesseract

NGROK_ENDPOINT = "ws://0.tcp.in.ngrok.io:17063"

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

# Define screen capture region
screen_region = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}  # Full screen

# Column boundaries with Y min/max bounds for each column
column_boundaries = [
    (300, 450, 300, 400),
    (500, 600, 300, 400),
    (610, 710, 300, 400),
    (720, 820, 300, 400),
    (825, 925, 300, 400),
]

# Row boundaries with Y min/max bounds for each row
row_boundaries = [
    (320, 360),  # Row 3
]

# Main Window for the Transparent Overlay
class OverlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, screen_region['width'], screen_region['height'])

        self.sct = mss()
        self.columns = {i: {'number': float('inf'), 'number_box': None} for i in range(len(column_boundaries))}
        self.rows = {i: {'number': float('inf'), 'number_box': None} for i in range(len(row_boundaries))}

        # Set up QTimer for capturing screen
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_overlay)
        self.timer.start(3000)  # Refresh every 3 seconds

    def update_overlay(self):
        asyncio.create_task(self.capture_and_process())  # Run the async function

    async def capture_and_process(self):
        final_op = []

        # Reset column values
        for col_index in self.columns:
            self.columns[col_index] = {'number': float('inf'), 'number_box': None}

        # Capture the screen
        screenshot = self.sct.grab(screen_region)
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        # Perform OCR
        ocr_result = pytesseract.image_to_data(frame, output_type=pytesseract.Output.DICT, lang='eng')

        for i in range(len(ocr_result['text'])):
            text = ocr_result['text'][i].strip()
            print(f"ORIGINAL TEXT: {text}")

            text = re.sub(r"\D", "", text)  # Extract only numbers
            print(f"CLEAN TEXT: {text}")

            if text:
                x, y, w, h = (ocr_result['left'][i], ocr_result['top'][i], ocr_result['width'][i], ocr_result['height'][i])

                for row_index, (row_min_y, row_max_y) in enumerate(row_boundaries):
                    if row_min_y <= y <= row_max_y:
                        for col_index, (min_x, max_x, min_y, max_y) in enumerate(column_boundaries):
                            if min_x <= x + 5 <= max_x and min_y <= y + 5 <= max_y:
                                final_op.append(text)
                                self.columns[col_index]['number'] = text
                                self.columns[col_index]['number_box'] = (x, y, w, h)

        if final_op:
            await self.send_to_websocket(final_op)

        self.update()

    async def send_to_websocket(self, data):
        try:
            async with websockets.connect(NGROK_ENDPOINT) as websocket:
                print("Connected to WebSocket server.")
                message = {"message": data}
                await websocket.send(str(message))
                response = await websocket.recv()
                print(f"Received from server: {response}")
        except Exception as e:
            print(f"WebSocket Error: {e}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw column lines
        painter.setPen(QColor(255, 0, 0, 150))  # Semi-transparent red
        painter.setBrush(Qt.NoBrush)

        for col_index, (min_x, max_x, min_y, max_y) in enumerate(column_boundaries):
            painter.drawLine(min_x, 0, min_x, screen_region['height'])
            painter.drawLine(max_x, 0, max_x, screen_region['height'])

            # Draw Y-threshold lines
            painter.setPen(QColor(0, 255, 0, 150))  # Green for Y threshold lines
            painter.drawLine(min_x, min_y, max_x, min_y)
            painter.drawLine(min_x, max_y, max_x, max_y)

            # Display column number at the top
            painter.setPen(QColor(255, 255, 255))  # White text
            painter.drawText(min_x + 5, 20, f"Col {col_index + 1}")

        # Draw row thresholds
        painter.setPen(QColor(0, 0, 255, 150))  # Blue for row thresholds
        for row_index, (row_min_y, row_max_y) in enumerate(row_boundaries):
            painter.drawLine(0, row_min_y, screen_region['width'], row_min_y)
            painter.drawLine(0, row_max_y, screen_region['width'], row_max_y)
            painter.drawText(10, row_min_y + 10, f"Row {row_index + 1}")

        # Highlight lowest numbers in each column
        for col_index, column_data in self.columns.items():
            if column_data['number_box']:
                x, y, w, h = column_data['number_box']
                painter.setPen(QColor(255, 255, 0))  # Yellow box
                painter.drawRect(x, y, w, h)

        painter.end()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OverlayWindow()
    window.show()
    sys.exit(app.exec_())