from PyQt5.QtWidgets import *

class CommPortsPopUp(QListWidget):
    """
    Class to handle the pop window used to select between different items on a list

    param[in] list_to_display: List of items to be listed
    param[in] cb_method: Method to call when an item is double clicked
    """

    def __init__(self, list_to_display, cb_method, prefix=""):
        super().__init__()
        self.cb_method = cb_method

        for item in list_to_display:
            self.addItem(prefix + item)

        self.resize(400, 300)
        self.setStyleSheet("font-size: 15px")

        self.itemDoubleClicked.connect(self.doubleClicked)
        self.centerMainWindow()

    def centerMainWindow(self):
        """
        Class method to center the main window in the user screen
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def doubleClicked(self, item):
        """
        Callback method for when a user double clicks an item in the list
        """
        self.cb_method(item.text())
        self.close()
