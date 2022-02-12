from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class WelcomeScreen(QWidget):
    """
    This class will be used when first running the simulator. It shows a welcome screen
    and lets the user select an EDF file and optionally an EDF device
    """

    def __init__(self, edf_worker, serial_comm_worker):
        super().__init__()

    def __new__(cls, edf_worker, serial_comm_worker):
        initial_selection = {}

        initial_selection["selected_edf_file"] = "C:/Users/juanc/Documents/Git/TProfesional_EEG/PyEDF-APP/samples/test_sample_23_channels.edf"


        return initial_selection

