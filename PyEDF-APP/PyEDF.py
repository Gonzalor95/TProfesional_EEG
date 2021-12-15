#!/usr/bin/python3

import sys
import os
import time
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from qtrangeslider import QLabeledRangeSlider
from EDFWorker import EDFWorker


class EDFSimulator(QWidget):
    big_int_ = 9999999999

    def __init__(self):
        super().__init__()
        self.info_h_boxes = []
        # Titles font
        self.title_font = QFont()
        self.title_font.setBold(True)
        self.title_font.setUnderline(True)
        self.title_font.setPointSize(15)
        # Info/config subtitles font
        self.info_key_font = QFont()
        self.info_key_font.setBold(True)
        self.info_key_font.setPointSize(14)
        # EDF worker instance
        self.edf_worker = EDFWorker()
        self.initUI()

    def initUI(self):
        # ==================================== LEFT COLUMN ====================================
        self.browse_button = QPushButton("BROWSE")
        self.browse_button.clicked.connect(self.browseEDFFiles)

        # ==================================== VERTICAL SEPARATOR LINE ====================================
        separator_line = QFrame()
        separator_line.setFrameShape(QFrame.VLine)
        separator_line.setStyleSheet("border:2px; border-style:solid")

        # ==================================== RIGHT COLUMN ====================================
        current_file_label = QLabel("Current EDF file: ")
        current_file_label.setFont(self.info_key_font)
        self.current_file_name_label = QLabel("")
        current_file_h_layout = QHBoxLayout()
        current_file_h_layout.addWidget(current_file_label)
        current_file_h_layout.addWidget(
            self.current_file_name_label, stretch=1)

        separator_line_2a = QFrame()
        separator_line_2a.setFrameShape(QFrame.HLine)
        separator_line_2a.setStyleSheet("border:1px; border-style:dashed")

        # Information vertical layout
        information_title_label = QLabel("Signal information:")
        information_title_label.setFont(self.title_font)
        self.information_labels_layout = QVBoxLayout()
        dotted_separator_line = QFrame()
        dotted_separator_line.setFrameShape(QFrame.HLine)
        dotted_separator_line.setFrameShadow(QFrame.Sunken)
        dotted_separator_line.setStyleSheet("border:1px; border-style:dashed")
        info_v_layout = QVBoxLayout()
        info_v_layout.addWidget(
            information_title_label, alignment=Qt.AlignHCenter)
        info_v_layout.addLayout(
            self.information_labels_layout)
        info_v_layout.addWidget(dotted_separator_line)
        info_v_layout.addStretch()

        # Config vertical layout
        # Title
        config_v_layout = QVBoxLayout()
        configuration_title_label = QLabel("Configuration:")
        configuration_title_label.setFont(self.title_font)
        config_v_layout.addWidget(
            configuration_title_label, alignment=Qt.AlignHCenter)
        # Selected channels
        selected_channels_key = QLabel("Selected channels: ")
        selected_channels_key.setFont(self.info_key_font)
        self.selected_channels_value = QLabel("")
        selected_channels_h_box = QHBoxLayout()
        selected_channels_h_box.addWidget(selected_channels_key)
        selected_channels_h_box.addWidget(
            self.selected_channels_value, stretch=1)
        channel_selector_h_box = QHBoxLayout()
        self.select_channels_button = QPushButton("Select")
        self.select_channels_button.clicked.connect(self.selectChannels)
        self.channel_select_line_edit = QLineEdit()
        self.channel_select_line_edit.setPlaceholderText("0, 1, 5 - 6,...")
        channel_selector_h_box.addWidget(self.channel_select_line_edit)
        channel_selector_h_box.addWidget(self.select_channels_button)
        config_v_layout.addLayout(selected_channels_h_box)
        config_v_layout.addLayout(channel_selector_h_box)
        # Time slider
        selected_sim_time_key = QLabel("Simulation time: ")
        selected_sim_time_key.setFont(self.info_key_font)
        self.selected_sim_time_value = QLabel("")
        selected_sim_time_h_box = QHBoxLayout()
        selected_sim_time_h_box.addWidget(selected_sim_time_key)
        selected_sim_time_h_box.addWidget(self.selected_sim_time_value)
        self.range_slider = QLabeledRangeSlider(Qt.Horizontal)
        self.range_slider.setHandleLabelPosition(
            QLabeledRangeSlider.LabelPosition.LabelsBelow)
        self.range_slider.setValue([0, 99])
        self.range_slider.valueChanged.connect(self.timeSliderChanged)
        config_v_layout.addLayout(selected_sim_time_h_box)
        config_v_layout.addWidget(self.range_slider)
        # Placeholders
        self.placeholder_label_3 = QLabel("asd3")
        self.placeholder_label_4 = QLabel("asd4")
        config_v_layout.addWidget(
            self.placeholder_label_3, alignment=Qt.AlignTop)
        config_v_layout.addWidget(
            self.placeholder_label_4, alignment=Qt.AlignTop)
        config_v_layout.addStretch()

        separator_line_2b = QFrame()
        separator_line_2b.setFrameShape(QFrame.HLine)
        separator_line_2b.setStyleSheet("border:1px; border-style:dashed")

        self.preview_button = QPushButton("PREVIEW PHYSICAL")
        self.preview_button.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.preview_button.clicked.connect(self.previewEDF)
        self.preview_dig_button = QPushButton("PREVIEW DIGITAL")
        self.preview_dig_button.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.preview_dig_button.clicked.connect(self.previewDigitalEDF)
        self.run_button = QPushButton("RUN")
        self.run_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.run_button.clicked.connect(self.runEDFSimulator)
        run_preview_buttons_h_layout = QHBoxLayout()
        run_preview_buttons_h_layout.addStretch(1)
        run_preview_buttons_h_layout.addWidget(self.preview_button)
        run_preview_buttons_h_layout.addWidget(self.preview_dig_button)
        run_preview_buttons_h_layout.addWidget(self.run_button)
        run_preview_buttons_h_layout.addStretch(1)

        # ==================================== GRID ====================================
        main_grid = QGridLayout()
        main_grid.setRowStretch(1, 1)
        main_grid.setRowStretch(2, 1)
        main_grid.setRowStretch(3, 1)
        main_grid.setRowStretch(4, 100)
        main_grid.setRowStretch(5, 1)
        main_grid.setRowStretch(6, 10)
        main_grid.addWidget(self.browse_button, 1, 1, alignment=Qt.AlignTop)
        main_grid.addWidget(separator_line, 1, 2, 6, 1)
        main_grid.addLayout(current_file_h_layout,
                            1, 3, alignment=Qt.AlignTop)
        main_grid.addWidget(separator_line_2a, 2, 3)
        main_grid.addLayout(info_v_layout, 3, 3)
        main_grid.addLayout(config_v_layout, 4, 3)
        main_grid.addWidget(separator_line_2b, 5, 3)
        main_grid.addLayout(run_preview_buttons_h_layout, 6, 3)

        self.setLayout(main_grid)

        self.setGeometry(300, 300, 1000, 800)
        self.setWindowTitle('EDF Simulator')

        self.centerMainWindow()
        self.show()

    # ==================================== CLASS METHODS ====================================
    def centerMainWindow(self):
        """
        Class method to center the main window in the user screen
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def browseEDFFiles(self):
        """
        Callback method for the "browse" button press.
        This method will try to load the EDF file clicked by the user
        into the system and display the corresponding information.
        """
        # Filter only for EDF files
        filter = "EDFFiles(*.edf)"
        file_name = QFileDialog.getOpenFileName(
            self, "Select EDF file", os.getcwd(), filter)[0]
        # Load EDF file into worker
        if(self.edf_worker.readEDF(file_name)):
            # Place the file name in the dialog box
            self.current_file_name_label.setText(file_name)
            # Set the maximun time selector slider value to the signal duration
            self.range_slider.setMaximum(self.edf_worker.getDuration())
            self.range_slider.setValue([0, self.big_int_])
            # Set selected channels to ALL
            self.selected_channels_value.setText("ALL")
            # Delete info h layouts in the info v layout (not the title)
            for widget_index in range(self.information_labels_layout.count()):
                self.deleteBoxFromLayout(
                    self.information_labels_layout, self.info_h_boxes[widget_index])
            # Generate the information h boxes and add them to the info v layout
            signal_info_dict = self.edf_worker.getSignalInfo()
            self.info_h_boxes.clear()
            for key in signal_info_dict:
                info_key = QLabel(str(key) + ": ")
                info_key.setFont(self.info_key_font)
                info_value = QLabel(str(signal_info_dict[key]))
                h_box = QHBoxLayout()
                h_box.addWidget(info_key)
                h_box.addWidget(info_value, stretch=1)
                self.info_h_boxes.append(h_box)
                self.information_labels_layout.addLayout(h_box)
        else:
            print("Error when trying to load the EDF file")

    def previewEDF(self):
        """
        Callback method for the "preview" button press. Used to preview the physical signals
        This method will plot the selected signal channels and show it to the user
        """
        print("Preview EDF requested")
        if(self.edf_worker.previewSignals("physical") == False):
            print("Error in preview EDF signal. Check if a file was loaded")

    def previewDigitalEDF(self):
        """
        Callback method for the "preview" button press. Used to preview digital signals.
        This method will plot the selected signal channels and show it to the user
        """
        print("Preview digital EDF requested")
        if(self.edf_worker.previewSignals("digital") == False):
            print("Error in preview EDF signal. Check if a file was loaded")

    def runEDFSimulator(self):
        print("Run EDF simulator requested")

    def selectChannels(self):
        """
        Callback method for the select channels button
        This method reads the selected channels line edit, parses it into an array of
        integers and set the EDF worker with it
        """
        raw_string = self.channel_select_line_edit.text()
        if raw_string:
            if raw_string == "ALL":
                selected_channels = [i for i in range(
                    0, self.edf_worker.getNumberOfChannels())]
            else:
                # Remove all whitespaces
                raw_string = raw_string.replace(" ", "")
                selected_channels = self.parseSelectedChannelsString(raw_string)
            if not selected_channels:
                print("Error when parsing input into channels")
            if self.edf_worker.setSelectedChannels(selected_channels) == False:
                print("Error when trying to set the selected channels in the EDF worker")
            else:
                self.selected_channels_value.setText(
                    ",".join([str(int) for int in selected_channels]))
        else:
            print("Empty input in channel selector")
        # Clear line edit
        self.channel_select_line_edit.clear()

    def timeSliderChanged(self):
        if self.edf_worker.isFileLoaded():
            self.edf_worker.setSelectedSimTime(self.range_slider.value())

    def deleteBoxFromLayout(self, layout, box):
        """
        Method to delete a box layout from another layout
        """
        for i in range(layout.count()):
            layout_item = layout.itemAt(i)
            if layout_item.layout() == box:
                self.deleteItemsOfLayout(layout_item.layout())
                layout.removeItem(layout_item)
                break

    def deleteItemsOfLayout(self, layout):
        """
        Method to delete the items of a layout
        """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.deleteItemsOfLayout(item.layout())

    def parseSelectedChannelsString(self, raw_selected_channels_string):
        """
        Method to parse the user input selected channel string into an array of ints
        """
        return_list = []
        aux_list = raw_selected_channels_string.split(",")
        for value in aux_list:
            if value.isdigit() and int(value) not in return_list:
                return_list.append(int(value))
            elif "-" in value:
                dash_subarray = parse_dash_separated_values(value)
                for value in dash_subarray:
                    if value not in return_list:
                        return_list.append(value)
            elif not value.isdigit():
                print("Wrong input format for channel selection")
                return []
        return return_list


def main():
    app = QApplication(sys.argv)
    # App icon
    app_icon = QIcon()
    app_icon.addFile('logo_fiuba.png', QSize(16, 16))
    app_icon.addFile('logo_fiuba.png', QSize(24, 24))
    app_icon.addFile('logo_fiuba.png', QSize(32, 32))
    app_icon.addFile('logo_fiuba.png', QSize(48, 48))
    app_icon.addFile('logo_fiuba.png', QSize(256, 256))
    app.setWindowIcon(app_icon)
    # Start EDF worker
    ex = EDFSimulator()
    # Start app
    sys.exit(app.exec_())

# Auxiliary methods =========================================


def parse_dash_separated_values(dash_string):
    """
    Aux method to parse the dash separated values into an array of ints
    """
    aux_list = dash_string.split("-")
    return_list = []
    if len(aux_list) != 2:
        print(
            "Error when parsing '-' separated values, more than two values found")
        return []
    if (not aux_list[0].isdigit()) or (not aux_list[1].isdigit()):
        print(
            "Error when parsing '-' separated values, values are not digits")
        return []
    if int(aux_list[0]) > int(aux_list[1]):
        print(
            "Error when parsing '-' separated values, first value bigger than the second one")
        return []
    for i in range(int(aux_list[1]) - int(aux_list[0])):
        return_list.append(int(aux_list[0]) + i)
    return_list.append(int(aux_list[1]))
    return return_list


if __name__ == '__main__':
    main()
