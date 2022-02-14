from PyQt5.QtGui import *

class FontStyles():
    def __init__(self):
        # Titles font
        self.title_font = QFont()
        self.title_font.setBold(True)
        self.title_font.setUnderline(False)
        self.title_font.setPointSize(15)
        # Info/config subtitles font
        self.info_key_font = QFont()
        self.info_key_font.setBold(True)
        self.info_key_font.setPointSize(14)

