# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\oceanview.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(60, 60, 160, 80))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.recordnumSpinBox = QtWidgets.QSpinBox(self.verticalLayoutWidget)
        self.recordnumSpinBox.setMaximum(20)
        self.recordnumSpinBox.setProperty("value", 10)
        self.recordnumSpinBox.setObjectName("recordnumSpinBox")
        self.horizontalLayout.addWidget(self.recordnumSpinBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.readIOButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.readIOButton.setObjectName("readIOButton")
        self.verticalLayout.addWidget(self.readIOButton)
        self.remainingrecordLineEdit = QtWidgets.QLineEdit(Dialog)
        self.remainingrecordLineEdit.setGeometry(QtCore.QRect(230, 80, 113, 20))
        self.remainingrecordLineEdit.setObjectName("remainingrecordLineEdit")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(230, 60, 61, 16))
        self.label_2.setObjectName("label_2")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "record Num"))
        self.readIOButton.setText(_translate("Dialog", "Read From Device"))
        self.label_2.setText(_translate("Dialog", "Remaining"))

