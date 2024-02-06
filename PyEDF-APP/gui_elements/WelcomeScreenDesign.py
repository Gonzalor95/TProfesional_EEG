# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_elements/WelcomeScreenDesign.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_WelcomeDialog(object):
    def setupUi(self, WelcomeDialog):
        WelcomeDialog.setObjectName("WelcomeDialog")
        WelcomeDialog.resize(400, 300)
        self.verticalLayoutWidget = QtWidgets.QWidget(WelcomeDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 408, 301))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.welcome_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.welcome_label.setTextFormat(QtCore.Qt.RichText)
        self.welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        self.welcome_label.setObjectName("welcome_label")
        self.verticalLayout.addWidget(self.welcome_label)
        self.line = QtWidgets.QFrame(self.verticalLayoutWidget)
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setLineWidth(3)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.instructions_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.instructions_label.setObjectName("instructions_label")
        self.verticalLayout_2.addWidget(self.instructions_label)
        self.welcome_list = QtWidgets.QListWidget(self.verticalLayoutWidget)
        self.welcome_list.setObjectName("welcome_list")
        self.verticalLayout_2.addWidget(self.welcome_list)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.back_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.back_button.setObjectName("back_button")
        self.horizontalLayout.addWidget(self.back_button)
        self.skip_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.skip_button.setObjectName("skip_button")
        self.horizontalLayout.addWidget(self.skip_button)
        self.next_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.next_button.setObjectName("next_button")
        self.horizontalLayout.addWidget(self.next_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.retranslateUi(WelcomeDialog)
        QtCore.QMetaObject.connectSlotsByName(WelcomeDialog)

    def retranslateUi(self, WelcomeDialog):
        _translate = QtCore.QCoreApplication.translate
        WelcomeDialog.setWindowTitle(_translate("WelcomeDialog", "Dialog"))
        self.welcome_label.setText(_translate("WelcomeDialog", "Bienvenido!"))
        self.instructions_label.setText(_translate("WelcomeDialog", "Por favor, seleccione un archivo EDF (puede seleccionarlo luego):"))
        self.back_button.setText(_translate("WelcomeDialog", "Anterior"))
        self.skip_button.setText(_translate("WelcomeDialog", "Saltear"))
        self.next_button.setText(_translate("WelcomeDialog", "Siguiente"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    WelcomeDialog = QtWidgets.QDialog()
    ui = Ui_WelcomeDialog()
    ui.setupUi(WelcomeDialog)
    WelcomeDialog.show()
    sys.exit(app.exec_())
