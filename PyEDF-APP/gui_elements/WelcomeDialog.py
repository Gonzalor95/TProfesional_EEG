import os

from gui_elements.WelcomeScreenDesigner import Ui_WelcomeDialog
from PyQt5.QtWidgets import QDialog


class WelcomeDialog(QDialog):
    initial_selection_ = {}
    state_ = "file"  # State of the welcome dialog screen. Two possible options: "file" and "device"

    def __init__(self, serial_comm_worker, parent=None):
        super().__init__(parent)
        # Create an instance of the GUI
        self.ui = Ui_WelcomeDialog()
        # Run the .setupUi() method to show the GUI
        self.ui.setupUi(self)

        # Save the serial comm worker. It will be used to list the edf devices
        self.serial_comm_worker = serial_comm_worker

        # Set up for initial state
        self.setUpInitialState()

        # Execute and show widget
        self.exec_()

    def setUpInitialState(self):
        """
        Method to set up the initial state. Disables the corresponding buttons and lloks for EDF files in
        the "edf_samples" folder at the same level the program is located
        """
        if self.state_ == "file":
            self.ui.back_button.setEnabled(False)
            edf_files_path = os.getcwd() + "\edf_samples"
            for file in os.listdir(edf_files_path):
                if file.endswith(".edf"):
                    self.ui.welcome_list.addItem(file)
        else:
            print("Error in the initial state of the welcome screen")

    def setState(self, state):
        """
        Method to set the state of the welcome screen

        @param state -- State of the welcome screen. Supports "file" and "device"
        """
        if state == "file":
            self.setUpInitialState()

    def getInitialSelection(self):
        """
        Method to return the initial selection of the user for EDF file and EDF device

        @return initial_selection -- Dictionary with the initial_file and initial_device selected by the user
        """
        return self.initial_selection_
