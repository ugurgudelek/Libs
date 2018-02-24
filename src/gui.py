import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi

class OceanViewGui(QDialog):
    def __init__(self):
        super(OceanViewGui, self).__init__()
        loadUi('../ui/oceanview.ui', self)
        self.setWindowTitle('OceanView')
        self.pushButton.clicked.connect(self.on_pushButton_clicked)

    @pyqtSlot()
    def on_pushButton_clicked(self):
        self.label.setText(self.lineEdit.text())


app = QApplication(sys.argv)
widget = OceanViewGui()
widget.show()
sys.exit(app.exec_())