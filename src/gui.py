import sys
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QSpinBox, QMessageBox, QLineEdit, QMainWindow, \
    QGraphicsView, QLabel, QStyle, QSizePolicy
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QPen, QPixmap

from iomanager import IOManager
from analyzer import Analyzer, Database, Sample
from config import Config
from engine import Engine
from util import subplot
from calibration import Calibrator


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

        self.locnameLineEdit = QLineEdit()
        self.sampleIDSpinBox = QSpinBox()
        self.howmanyrecordSpinBox = QSpinBox()

        self.remainingrecordLineEdit = QLineEdit()

        self.readIOButton = QPushButton()

        loadUi('../ui/oceanview_mainw.ui', self)
        self.setWindowTitle('OceanView')

        self.setWindowIcon(QIcon('../input/image.png'))
        pixmap = QPixmap('../input/image.png')
        self.testlabel.setPixmap(pixmap)
        self.testlabel.setScaledContents(True)
        self.testlabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.testlabel.show()

        #  initializations
        self.howmanyrecordSpinBox.setValue(10)
        self.remainingrecord = self.howmanyrecordSpinBox.value()

        # connect events
        self.howmanyrecordSpinBox.valueChanged.connect(self.on_howmanyrecordSpinBox_valueChanged)
        self.readIOButton.clicked.connect(self.onreadIOButton_clicked)

    ####################################
    #             EVENTS               #
    ####################################

    @pyqtSlot()
    def on_howmanyrecordSpinBox_valueChanged(self):
        self.remainingrecord = self.howmanyrecordSpinBox.value()

    @pyqtSlot()
    def onreadIOButton_clicked(self):
        loc_name = self.locnameLineEdit.text().lower()
        sample_id = self.sampleIDSpinBox.value()
        howmanyrecord = self.howmanyrecordSpinBox.value()

        sample_dir_already_exists = engine.connect_to_gui(loc_name=loc_name, sample_id=sample_id)

        start_reading = True
        if sample_dir_already_exists:
            choice = QMessageBox.question(self,
                                          'Sample directory', 'Sample dir already exists. \n'
                                                                   'Do you want to continue?',
                                          QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.No:
                start_reading = False

        if start_reading:
            readings = {}
            while self.remainingrecord > 0:
                name, reading = engine.read_io()
                readings[name] = reading
                self.remainingrecord -= 1

            engine.load_readings(readings=readings)


            # Save readings
            choice = QMessageBox.question(self,
                                          'Record',
                                          'Recording Finished!\n'
                                          'Recordings are saved to\n'
                                          'output/samples/{loc_name}/{sample_id}'.format(loc_name=loc_name, sample_id=sample_id),
                                          QMessageBox.Ok)

            dir = engine.save_readings()

            if self.dev_mode:
                # Plot readings
                subplot(dictionary=readings, xname='wavelengths', yname='intensities', ncols=3)

                # Analyze readings
                choice = QMessageBox.question(self, 'Analyze',
                                              'Do you want to analyze {}-{}'.format(loc_name, sample_id),
                                              QMessageBox.Yes | QMessageBox.No)

                if choice == QMessageBox.Yes:
                    # fixme: make it generic
                    engine.pipeline(loc_name='niğde')

        # reset for next record
        self.remainingrecord = self.howmanyrecordSpinBox.value()


config = Config('../config.ini')
engine = Engine(iomanager=IOManager(),
                analyzer=Analyzer(config=config, database=Database(config)),
                calibrator=Calibrator(input_dir=config.calibration_input_dir,
                                      output_dir=config.calibration_output_dir),
                config=config)

app = QApplication(sys.argv)

widget = OceanViewGui(engine=engine, config=config)
widget.show()

sys.exit(app.exec_())
