# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\gui_elements\EDFGUIDesigner.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(948, 723)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.information_title_label = QtWidgets.QLabel(self.centralwidget)
        self.information_title_label.setFrameShape(QtWidgets.QFrame.Box)
        self.information_title_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.information_title_label.setMidLineWidth(0)
        self.information_title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.information_title_label.setObjectName("information_title_label")
        self.gridLayout.addWidget(self.information_title_label, 2, 2, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_2.setLineWidth(2)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 1, 2, 1, 1)
        self.configuration_title_label = QtWidgets.QLabel(self.centralwidget)
        self.configuration_title_label.setFrameShape(QtWidgets.QFrame.Box)
        self.configuration_title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.configuration_title_label.setObjectName("configuration_title_label")
        self.gridLayout.addWidget(self.configuration_title_label, 4, 2, 1, 1)
        self.information_labels_layout = QtWidgets.QVBoxLayout()
        self.information_labels_layout.setObjectName("information_labels_layout")
        self.gridLayout.addLayout(self.information_labels_layout, 3, 2, 1, 1)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setLineWidth(4)
        self.line.setMidLineWidth(0)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 0, 1, 10, 1)
        self.buttons_v_layout = QtWidgets.QVBoxLayout()
        self.buttons_v_layout.setContentsMargins(-1, -1, -1, 0)
        self.buttons_v_layout.setObjectName("buttons_v_layout")
        self.browse_edf_button = QtWidgets.QPushButton(self.centralwidget)
        self.browse_edf_button.setObjectName("browse_edf_button")
        self.buttons_v_layout.addWidget(self.browse_edf_button)
        self.browse_devices_button = QtWidgets.QPushButton(self.centralwidget)
        self.browse_devices_button.setObjectName("browse_devices_button")
        self.buttons_v_layout.addWidget(self.browse_devices_button)
        self.testing_signals_button = QtWidgets.QPushButton(self.centralwidget)
        self.testing_signals_button.setObjectName("testing_signals_button")
        self.buttons_v_layout.addWidget(self.testing_signals_button)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.buttons_v_layout.addItem(spacerItem)
        self.gridLayout.addLayout(self.buttons_v_layout, 0, 0, 10, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.selected_channels_key = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selected_channels_key.sizePolicy().hasHeightForWidth())
        self.selected_channels_key.setSizePolicy(sizePolicy)
        self.selected_channels_key.setObjectName("selected_channels_key")
        self.horizontalLayout.addWidget(self.selected_channels_key)
        self.selected_channels_value = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selected_channels_value.sizePolicy().hasHeightForWidth())
        self.selected_channels_value.setSizePolicy(sizePolicy)
        self.selected_channels_value.setMinimumSize(QtCore.QSize(0, 0))
        self.selected_channels_value.setText("")
        self.selected_channels_value.setObjectName("selected_channels_value")
        self.horizontalLayout.addWidget(self.selected_channels_value)
        self.channel_browse_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.channel_browse_button.sizePolicy().hasHeightForWidth())
        self.channel_browse_button.setSizePolicy(sizePolicy)
        self.channel_browse_button.setObjectName("channel_browse_button")
        self.horizontalLayout.addWidget(self.channel_browse_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.selected_sim_time_key = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selected_sim_time_key.sizePolicy().hasHeightForWidth())
        self.selected_sim_time_key.setSizePolicy(sizePolicy)
        self.selected_sim_time_key.setObjectName("selected_sim_time_key")
        self.horizontalLayout_6.addWidget(self.selected_sim_time_key)
        self.selected_sim_time_value = QtWidgets.QLabel(self.centralwidget)
        self.selected_sim_time_value.setText("")
        self.selected_sim_time_value.setObjectName("selected_sim_time_value")
        self.horizontalLayout_6.addWidget(self.selected_sim_time_value)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.range_slider_layout = QtWidgets.QHBoxLayout()
        self.range_slider_layout.setObjectName("range_slider_layout")
        self.verticalLayout.addLayout(self.range_slider_layout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.sample_rate_config_h_layout = QtWidgets.QHBoxLayout()
        self.sample_rate_config_h_layout.setObjectName("sample_rate_config_h_layout")
        self.sample_rate_config_key = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sample_rate_config_key.sizePolicy().hasHeightForWidth())
        self.sample_rate_config_key.setSizePolicy(sizePolicy)
        self.sample_rate_config_key.setObjectName("sample_rate_config_key")
        self.sample_rate_config_h_layout.addWidget(self.sample_rate_config_key)
        self.sample_rate_config_selected = QtWidgets.QLabel(self.centralwidget)
        self.sample_rate_config_selected.setText("")
        self.sample_rate_config_selected.setObjectName("sample_rate_config_selected")
        self.sample_rate_config_h_layout.addWidget(self.sample_rate_config_selected)
        self.verticalLayout_2.addLayout(self.sample_rate_config_h_layout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.sample_rate_config_input = QtWidgets.QLineEdit(self.centralwidget)
        self.sample_rate_config_input.setObjectName("sample_rate_config_input")
        self.horizontalLayout_2.addWidget(self.sample_rate_config_input)
        self.sample_rate_config_set_button = QtWidgets.QPushButton(self.centralwidget)
        self.sample_rate_config_set_button.setObjectName("sample_rate_config_set_button")
        self.horizontalLayout_2.addWidget(self.sample_rate_config_set_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout, 5, 2, 1, 1)
        self.current_selection_layout = QtWidgets.QVBoxLayout()
        self.current_selection_layout.setObjectName("current_selection_layout")
        self.current_file_h_layout = QtWidgets.QHBoxLayout()
        self.current_file_h_layout.setObjectName("current_file_h_layout")
        self.current_file_label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.current_file_label.sizePolicy().hasHeightForWidth())
        self.current_file_label.setSizePolicy(sizePolicy)
        self.current_file_label.setTextFormat(QtCore.Qt.RichText)
        self.current_file_label.setObjectName("current_file_label")
        self.current_file_h_layout.addWidget(self.current_file_label)
        self.current_file_name_label = QtWidgets.QLabel(self.centralwidget)
        self.current_file_name_label.setText("")
        self.current_file_name_label.setObjectName("current_file_name_label")
        self.current_file_h_layout.addWidget(self.current_file_name_label)
        self.current_selection_layout.addLayout(self.current_file_h_layout)
        self.current_device_h_layout = QtWidgets.QHBoxLayout()
        self.current_device_h_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.current_device_h_layout.setObjectName("current_device_h_layout")
        self.current_device_label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.current_device_label.sizePolicy().hasHeightForWidth())
        self.current_device_label.setSizePolicy(sizePolicy)
        self.current_device_label.setTextFormat(QtCore.Qt.PlainText)
        self.current_device_label.setObjectName("current_device_label")
        self.current_device_h_layout.addWidget(self.current_device_label)
        self.current_device_name_label = QtWidgets.QLabel(self.centralwidget)
        self.current_device_name_label.setText("")
        self.current_device_name_label.setObjectName("current_device_name_label")
        self.current_device_h_layout.addWidget(self.current_device_name_label)
        self.current_selection_layout.addLayout(self.current_device_h_layout)
        self.gridLayout.addLayout(self.current_selection_layout, 0, 2, 1, 1)
        self.prev_run_buttons_layout = QtWidgets.QHBoxLayout()
        self.prev_run_buttons_layout.setObjectName("prev_run_buttons_layout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.prev_run_buttons_layout.addItem(spacerItem1)
        self.preview_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.preview_button.sizePolicy().hasHeightForWidth())
        self.preview_button.setSizePolicy(sizePolicy)
        self.preview_button.setObjectName("preview_button")
        self.prev_run_buttons_layout.addWidget(self.preview_button)
        self.run_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.run_button.sizePolicy().hasHeightForWidth())
        self.run_button.setSizePolicy(sizePolicy)
        self.run_button.setObjectName("run_button")
        self.prev_run_buttons_layout.addWidget(self.run_button)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.prev_run_buttons_layout.addItem(spacerItem2)
        self.gridLayout.addLayout(self.prev_run_buttons_layout, 9, 2, 1, 1)
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_3.setLineWidth(2)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 7, 2, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 6, 2, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.run_button, self.testing_signals_button)
        MainWindow.setTabOrder(self.testing_signals_button, self.browse_devices_button)
        MainWindow.setTabOrder(self.browse_devices_button, self.preview_button)
        MainWindow.setTabOrder(self.preview_button, self.browse_edf_button)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "EDF signal generator"))
        self.information_title_label.setText(_translate("MainWindow", "Signal information"))
        self.configuration_title_label.setText(_translate("MainWindow", "Signal configuration"))
        self.browse_edf_button.setText(_translate("MainWindow", "Browse EDFs"))
        self.browse_devices_button.setText(_translate("MainWindow", "Browse devices"))
        self.testing_signals_button.setText(_translate("MainWindow", "Testing signals"))
        self.selected_channels_key.setText(_translate("MainWindow", "Selected channels: "))
        self.channel_browse_button.setText(_translate("MainWindow", "Browse channels"))
        self.selected_sim_time_key.setText(_translate("MainWindow", "Simulation time [s]: "))
        self.sample_rate_config_key.setText(_translate("MainWindow", "Sample rate:"))
        self.sample_rate_config_set_button.setText(_translate("MainWindow", "Set sample rate"))
        self.current_file_label.setText(_translate("MainWindow", "Current signal: "))
        self.current_device_label.setText(_translate("MainWindow", "Current device: "))
        self.preview_button.setText(_translate("MainWindow", "PREVIEW"))
        self.run_button.setText(_translate("MainWindow", "RUN"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
