import sys
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QImage, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow
from mss import mss
import pytesseract
import re

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Define screen capture region
screen_region = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}  # Full screen

# # Column boundaries with Y min/max bounds for each column
# column_boundaries = [
#     (105, 220, 100, 1200),  # (min_x, max_x, min_y, max_y)
#     (281, 401, 100, 1200),
#     (458, 595, 100, 1200),
#     (638, 775, 100, 1200),
#     (810, 935, 100, 1200),
#     (985, 1115, 100, 1200),
#     (1160, 1295, 100, 1200),
#     (1335, 1480, 100, 1200),
#     (1515, 1655, 100, 1200),
#     (1696, 1830, 100, 1200)
# ]

# # Row boundaries with Y min/max bounds for each row (add your row boundaries)
# row_boundaries = [
#     (100, 250),  # Row 1
#     (250, 400),  # Row 2
#     (400, 550),  # Row 3
#     (550, 700),  # Row 4
#     (700, 850),  # Row 5
#     (850, 1000),  # Row 6
#     (1000, 1150),  # Row 7
#     (1150, 1300),  # Row 8
#     (1300, 1450),  # Row 9
#     (1450, 1600)   # Row 10
# ]
# Column boundaries with Y min/max bounds for each column
column_boundaries = [

    (300, 450, 300, 400),
    (500, 600, 300, 400),
    (610, 710, 300, 400),
    (720, 820, 300, 400),
    (825, 925, 300, 400),
    # (588, 638, 300, 400)
    # (638, 688, 300, 400),
    # (688, 738, 300, 400),
    # (738, 788, 300, 400),
    # (788, 838, 300, 400),
    # (838, 888, 300, 400),
    # (938, 988, 300, 400),  # (min_x, max_x, min_y, max_y)
    # (1038, 1088, 300, 400),
]

# Row boundaries with Y min/max bounds for each row (add your row boundaries)
row_boundaries = [
    # (100, 250),  # Row 1
    # (250, 400),  # Row 2
    (320, 360),  # Row 3
    # (550, 700),  # Row 4
    # (700, 850),  # Row 5
    # (850, 1000),  # Row 6
    # (1000, 1150),  # Row 7
    # (1150, 1300),  # Row 8
    # (1300, 1450),  # Row 9
    # (1450, 1600)   # Row 10
]





# Main Window for the Transparent Overlay
class OverlayWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.counter = 0
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, screen_region['width'], screen_region['height'])

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_overlay)
        self.timer.start(3000)  # Refresh every 5secs

        self.sct = mss()
        self.columns = {i: {'number': float('inf'), 'number_box': None} for i in range(len(column_boundaries))}
        self.rows = {i: {'number': float('inf'), 'number_box': None} for i in range(len(row_boundaries))}

    def update_overlay(self):
        # Reset columns and rows at the beginning of each update
        for col_index in self.columns:
            self.columns[col_index] = {'number': float('inf'), 'number_box': None}

        for row_index in self.rows:
            self.rows[row_index] = {'number': float('inf'), 'number_box': None}

        # Capture the defined region
        screenshot = self.sct.grab(screen_region)
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        # Proceed with OCR processing
        ocr_result = pytesseract.image_to_data(frame, output_type=pytesseract.Output.DICT, lang='eng')
        self.counter = self.counter + 1

        for i in range(len(ocr_result['text'])):
            text = ocr_result['text'][i].strip()
            print(f"ORIGINAL TEXT: {text}")
            text = re.sub(r"\D", "", text)
            print(f"CLEAN TEXT: {text}")
            if text:
                x, y, w, h = (ocr_result['left'][i], ocr_result['top'][i], ocr_result['width'][i], ocr_result['height'][i])

                # Check for both column and row boundaries in the same loop
                for row_index, (row_min_y, row_max_y) in enumerate(row_boundaries):
                    if  row_min_y <= y <= row_max_y:
                    # Now check for row boundaries (inside the same column check)
                        for col_index, (min_x, max_x, min_y, max_y) in enumerate(column_boundaries):
                            if min_x <= x + 5 <= max_x and min_y <= y+5 <= max_y:
                                self.columns[col_index]['number'] = text
                                self.columns[col_index]['number_box'] = (x, y, w, h)

        print (self.columns)
        print (self.rows)


        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw column lines and numbers
        painter.setPen(QColor(255, 0, 0, 150))  # Semi-transparent red for column lines
        painter.setBrush(Qt.NoBrush)

        for col_index, (min_x, max_x, min_y, max_y) in enumerate(column_boundaries):
            # Draw the column boundary lines
            painter.drawLine(min_x, 0, min_x, screen_region['height'])
            painter.drawLine(max_x, 0, max_x, screen_region['height'])

            # Draw Y-coordinate threshold lines
            painter.setPen(QColor(0, 255, 0, 150))  # Green color for Y threshold lines
            painter.drawLine(min_x, min_y, max_x, min_y)  # Upper Y threshold
            painter.drawLine(min_x, max_y, max_x, max_y)  # Lower Y threshold

            # Display column number at the top of each column
            painter.setPen(QColor(255, 255, 255))  # White text for column numbers
            painter.drawText(min_x + 5, 20, f"Col {col_index + 1}")

        # Draw row thresholds
        painter.setPen(QColor(0, 0, 255, 150))  # Blue for row thresholds
        for row_index, (row_min_y, row_max_y) in enumerate(row_boundaries):
            painter.drawLine(0, row_min_y, screen_region['width'], row_min_y)  # Upper Y threshold for rows
            painter.drawLine(0, row_max_y, screen_region['width'], row_max_y)  # Lower Y threshold for rows
            painter.drawText(10, row_min_y + 10, f"Row {row_index + 1}")

        # Highlight lowest numbers in each column
        for col_index, column_data in self.columns.items():
            if column_data['number_box']:
                x, y, w, h = column_data['number_box']
                painter.setPen(QColor(255, 255, 0))  # Yellow box around lowest number
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(x, y, w, h)


        painter.end()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OverlayWindow()
    window.show()
    sys.exit(app.exec_())