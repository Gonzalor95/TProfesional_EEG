import os

from gui_elements.TestingSignalsDesign import Ui_testing_signals_dialog
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class TestingSignalsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Create an instance of the GUI
        self.ui = Ui_testing_signals_dialog()
        # Run the .setupUi() method to show the GUI
        self.ui.setupUi(self)

        # Connect items with callbacks
        self.ui.testing_signal_selection_accept_button.clicked.connect(self.acceptButtonClicked)
        self.ui.testing_signal_selection_cancel_button.clicked.connect(self.cancelButtonClicked)
        self.ui.sin_checkbox.stateChanged.connect(self.check)
        self.ui.triang_checkbox.stateChanged.connect(self.check)
        self.ui.square_checkbox.stateChanged.connect(self.check)

        # Dictionary with information to return
        self.selection_ = {}

        # Execute and show widget
        self.exec_()

    def acceptButtonClicked(self):
        """
        Callback method for the Back button
        """
        selected_signal = self.checkWhichSignalIsChecked()
        if selected_signal:
            self.selection_["signal_name"] = selected_signal
        else:
            print("No testing signal selected, defaulting to sinusoidal")
            self.selection_["signal_name"] = "Sinusoidal"

        if (self.ui.amplitude_input_line_edit.text().isnumeric()):
            self.selection_["amplitude"] = int(self.ui.amplitude_input_line_edit.text())
        else:
            print("Invalid input amplitude in testing signal selection, defaulting to 120 uV")
            self.selection_["amplitude"] = 120

        if (self.ui.frecuency_input_line_edit.text().isnumeric()):
            self.selection_["frecuency"] = int(self.ui.frecuency_input_line_edit.text())
        else:
            print("Invalid input frecuency in testing signal selection, defaulting to 50 Hz")
            self.selection_["frecuency"] = 50

        if (self.ui.sample_rate_input_line_edit.text().isnumeric()):
            self.selection_["sample_rate"] = int(self.ui.sample_rate_input_line_edit.text())
        else:
            print("Invalid input sample rate in testing signal selection, defaulting to 2048 1/sec")
            self.selection_["sample_rate"] = 2048

        if (self.ui.duration_input_line_edit.text().isnumeric()):
            self.selection_["duration"] = int(self.ui.duration_input_line_edit.text())
        else:
            print("Invalid input duration in testing signal selection, defaulting to 5 sec")
            self.selection_["duration"] = 5
        self.done(1)

    def cancelButtonClicked(self):
        """
        Callback method for the Skip button
        """
        # Return an empty dict
        self.selection_ = {}
        self.close()

    def trackSelectedChannels(self, item):
        clicked_channel = item.text()
        if clicked_channel not in self.selected_channels:
            self.selected_channels.append(clicked_channel)

    def getSelection(self):
        """
        Method to return the testing signal selection

        @return selection -- Dictionary with the testing signal info
        """
        return self.selection_

    def check(self, state):
        """
        Method to handle the 3 testing signal checkboxes, only one active at a time
        """
        if state == Qt.Checked:
            if self.sender() == self.ui.sin_checkbox:
                self.ui.triang_checkbox.setChecked(False)
                self.ui.square_checkbox.setChecked(False)
            elif self.sender() == self.ui.triang_checkbox:
                self.ui.sin_checkbox.setChecked(False)
                self.ui.square_checkbox.setChecked(False)
            elif self.sender() == self.ui.square_checkbox:
                self.ui.triang_checkbox.setChecked(False)
                self.ui.sin_checkbox.setChecked(False)

    def checkWhichSignalIsChecked(self):
        """
        Checks which signal is checked, empty if none
        """
        if (self.ui.sin_checkbox.isChecked()):
            return "Sinusoidal"
        elif (self.ui.square_checkbox.isChecked()):
            return "Square"
        elif (self.ui.triang_checkbox.isChecked()):
            return "Triangular"
        else:
            return ""
