from PyQt5.QtWidgets import *

class PopUpWindow(QMessageBox):
    """
    Class to handle the pop up msg windows for the user
    """

    def __init__(self, title, msg, button_type, icon):
        super().__init__()
        self.setWindowTitle(title)
        self.setText(msg)
        self.setIcon(icon)
        self.setStandardButtons(button_type)
        self.setDefaultButton(button_type)
        self.exec_()
