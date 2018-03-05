import sys
from PyQt5.QtCore import pyqtSlot,Qt
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QSpinBox, QMessageBox, QLineEdit, QMainWindow, QGraphicsView, QLabel, QStyle, QSizePolicy
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QPen, QPixmap

from iomanager import IOManager
from analyzer import Analyzer, Database, Sample
from config import Config
from engine import Engine
from util import subplot

class OceanViewGui(QMainWindow):
    def __init__(self, engine, config):
        super(OceanViewGui, self).__init__()
        self.init_ui()
        self.engine = engine

        self.dev_mode = True if config.mode == 'dev' else False


    @property
    def remainingrecord(self):
        return self._remainingrecord

    @remainingrecord.setter
    def remainingrecord(self, value):
        self._remainingrecord = value
        self.remainingrecordLineEdit.setText(str(value))
        QtWidgets.qApp.processEvents()

    def init_ui(self):
        loadUi('../ui/oceanview_mainw.ui', self)
        self.setWindowTitle('OceanView')

        self.setWindowIcon(QIcon('../input/image.png'))

        pixmap = QPixmap('../input/image.png')
        self.testlabel.setPixmap(pixmap)
        self.testlabel.setScaledContents(True)
        self.testlabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.testlabel.show()


        self.recordnumSpinBox.setValue(10)
        self.recordnumSpinBox.valueChanged.connect(self.on_recordnumSpinBox_valueChanged)
        self.readIOButton.clicked.connect(self.onreadIOButton_clicked)
        self.recordnameLineEdit.textChanged.connect(self.on_recordnameLineEdit_valueChanged)

        self.remainingrecord = self.recordnumSpinBox.value()

    ####################################
    #             EVENTS               #
    ####################################
    @pyqtSlot()
    def on_recordnameLineEdit_valueChanged(self):
        self.recordname = self.recordnameLineEdit.text()

    @pyqtSlot()
    def on_recordnumSpinBox_valueChanged(self):
        self.remainingrecord = self.recordnumSpinBox.value()


    @pyqtSlot()
    def onreadIOButton_clicked(self):
        readings = {}

        while self.remainingrecord > 0:
            name, reading = engine.read_io(fake=True)
            readings[name] = reading
            self.remainingrecord -= 1

        # Save readings
        choice = QMessageBox.question(self, 'Record', 'Recording Finished!\nRecordings are saved to\n{}'.format(self.recordname),
                                      QMessageBox.Ok)

        dir = engine.save_readings(name=self.recordname, readings=readings)

        if self.dev_mode:
            # Plot readings
            subplot(dictionary=readings, xname='wavelengths', yname='intensities', ncols=3)

            # Analyze readings
            choice = QMessageBox.question(self, 'Analyze',
                                      'Do you want to analyze {}'.format(self.recordname),
                                      QMessageBox.Yes|QMessageBox.No)


            if choice == QMessageBox.Yes:
                engine.analyze(dir=dir)

        # reset for next record
        self.remainingrecord = self.recordnumSpinBox.value()

config = Config('../config.ini')
engine = Engine(iomanager=IOManager(),
                analyzer=Analyzer(config=config, database=Database(config)),
                config=config)



app = QApplication(sys.argv)

widget = OceanViewGui(engine=engine, config=config)
widget.show()



sys.exit(app.exec_())

