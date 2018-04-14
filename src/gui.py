import sys
from PyQt5.QtCore import pyqtSlot, Qt, QRect
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QSpinBox, QMessageBox, QLineEdit, QMainWindow, \
    QGraphicsView, QLabel, QStyle, QSizePolicy, QWidget, QTableWidgetItem, QHeaderView, QComboBox
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QPen, QPixmap

from iomanager import IOManager
from analyzer import Analyzer, Database, Sample
from config import Config
from engine import Engine
from util import subplot
from calibration import Calibrator



import pandas as pd
import os


class OceanViewGui(QMainWindow):
    def __init__(self, engine, config):
        super(OceanViewGui, self).__init__()

        self.engine = engine
        self.config = config


        self.giris_window = QWidget()
        self.analiz_window = QWidget()
        self.tbs_window = QWidget()

        self.w = 1000
        self.h = 640

        self.init_ui()

        self.init_giris_window()
        self.init_analiz_window()
        self.init_tbs_window()

    @property
    def remainingrecord(self):
        return self._remainingrecord

    @remainingrecord.setter
    def remainingrecord(self, value):
        self._remainingrecord = value
        self.analiz_window.remainingrecordLE.setText(str(value))
        QtWidgets.qApp.processEvents()

    # def init_ui(self):
    #
    #     self.locnameLineEdit = QLineEdit()
    #     self.sampleIDSpinBox = QSpinBox()
    #     self.howmanyrecordSpinBox = QSpinBox()
    #
    #     self.remainingrecordLineEdit = QLineEdit()
    #
    #     self.readIOButton = QPushButton()
    #
    #     loadUi('../ui/oceanview_mainw.ui', self)
    #     self.setWindowTitle('OceanView')
    #
    #     self.setWindowIcon(QIcon('../input/image.png'))
    #     pixmap = QPixmap('../input/image.png')
    #     self.testlabel.setPixmap(pixmap)
    #     self.testlabel.setScaledContents(True)
    #     self.testlabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
    #     self.testlabel.show()
    #
    #     #  initializations
    #     self.howmanyrecordSpinBox.setValue(10)
    #     self.remainingrecord = self.howmanyrecordSpinBox.value()
    #
    #     # connect events
    #     self.howmanyrecordSpinBox.valueChanged.connect(self.on_howmanyrecordSpinBox_valueChanged)
    #     self.readIOButton.clicked.connect(self.onreadIOButton_clicked)

    ####################################
    #             EVENTS               #
    ####################################

    @pyqtSlot()
    def on_howmanyrecordSpinBox_valueChanged(self):
        self.remainingrecord = self.analiz_window.howmanyrecordSpinBox.value()

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




    @pyqtSlot()
    def on_backtohomeButton_clicked(self):
        self.giris_window.hide()
        self.analiz_window.hide()
        self.tbs_window.hide()
        self.show()

    @staticmethod
    def createTable(tableWidget):
        # Create table
        tableWidget.setRowCount(0)
        tableWidget.setColumnCount(5)
        tableWidget.setHorizontalHeaderLabels(['Numune Adı', 'Element', 'Miktar', 'Birim', 'Durumu'])


    def assign_triggers(self):
        self.girisButton.clicked.connect(self.on_girisButton_clicked)
        self.analizButton.clicked.connect(self.on_analizButton_clicked)
        self.tarimsalbilgisistemiButton.clicked.connect(self.on_tarimsalbilgisistemiButton_clicked)

    @pyqtSlot()
    def on_girisButton_clicked(self):
        self.hide()
        self.giris_window.show()

    @pyqtSlot()
    def on_analizButton_clicked(self):
        self.hide()
        self.analiz_window.show()

    @pyqtSlot()
    def on_tarimsalbilgisistemiButton_clicked(self):
        self.hide()
        self.tbs_window.show()

    @staticmethod
    def setButtonIcon(button, filepath):
        pixmap = QPixmap(filepath)
        icon = QIcon(pixmap)
        button.setIcon(icon)
        button.setIconSize(pixmap.rect().size())

    def init_ui(self):
        # MainWindow
        self.girisButton = QPushButton()
        self.analizButton = QPushButton()
        self.tarimsalbilgisistemiButton = QPushButton()

        loadUi('../ui/mainw.ui', self)
        self.setWindowTitle('OceanView')
        self.setFixedSize(self.w, self.h)

        self.setWindowIcon(QIcon('../ui/icon/image.png'))

        OceanViewGui.setButtonIcon(self.girisButton, '../ui/icon/house.png')
        OceanViewGui.setButtonIcon(self.analizButton, '../ui/icon/analytics.png')
        OceanViewGui.setButtonIcon(self.tarimsalbilgisistemiButton, '../ui/icon/fertilizer.png')

    def init_giris_window(self):
        # self.giris_window.setFixedSize(self.w, self.h)
        loadUi('../ui/giris_window.ui', self.giris_window)
        self.giris_window.setWindowTitle('Giriş')

        self.giris_window.uruntipiCB.addItems(['Bitkisel Ürün'])
        self.giris_window.tarimsekliCB.addItems(['Kuru', 'Sulu'])
        self.giris_window.derinlikCB.addItems(['0-30 cm', '30-60 cm', '60-90 cm', '90-120 cm'])

        OceanViewGui.setButtonIcon(self.giris_window.backtohomeButton, '../ui/icon/back.png')
        self.giris_window.backtohomeButton.clicked.connect(self.on_backtohomeButton_clicked)

        self.giris_window.saveButton.clicked.connect(self.on_saveButton_clicked)

    def show_save_popup(self, text):
        QMessageBox.question(self, 'Bilgi', text, QMessageBox.Ok)

    @pyqtSlot()
    def on_saveButton_clicked(self):
        il = self.giris_window.ilLE.text()
        ilce = self.giris_window.ilceLE.text()
        koy = self.giris_window.koyLE.text()
        adaparsel = self.giris_window.adaparselLE.text()

        uruntipi = self.giris_window.uruntipiCB.currentText()
        tarimsekli = self.giris_window.tarimsekliCB.currentText()
        derinlik = self.giris_window.derinlikCB.currentText()

        giris_info = dict(il=il,
                               ilce=ilce,
                               koy=koy,
                               adaparsel=adaparsel,
                               uruntipi=uruntipi,
                               tarimsekli=tarimsekli,
                               derinlik=derinlik)

        self.engine.set_giris_info(giris_info)
        self.engine.save_giris_info()

        # todo: show saved popup.
        self.show_save_popup('Arazi bilgileri kaydedildi.')

    @pyqtSlot()
    def on_analyzeButton_clicked(self):
        numuneadi = self.analiz_window.numuneadiLE.text()
        lazeratissayisi = self.analiz_window.howmanyrecordSpinBox.value()
        birim = self.analiz_window.birimCB.currentText()

        numune_info = dict(numuneadi=numuneadi,
                           lazeratissayisi=lazeratissayisi,
                           birim=birim)

        self.engine.set_numune_info(numune_info)


        # to update remainingrecord, I need to create a generator
        for self.remainingrecord in self.engine.read_remainingrecords(self.remainingrecord):
            readings = self.engine.readings



        dir = self.engine.save_readings()

        # show saved popup
        self.show_save_popup('Atışlar kaydedildi.\nAnalize devam edilecek.')

        # analyze and show peaks and its neighbours
        (sample, matches) = self.engine.analyze(dir=dir, plotnow=True)

        # match elements in calibration excel with peak values.
        found_el_intensity_matches = self.engine.calibrate(matches=matches)


        # todo: read calibration file

        # done: implement fit calibration

        numuneadi = self.engine.numune_info['numuneadi']
        element = 'N 5 @ 443.506'
        X = self.engine.fit(found_el_intensity_matches[element])
        miktar = str(X)
        birim = self.engine.numune_info['birim']
        durumu = 'NA'

        # done: fill table
        self.engine.data_to_row(self.analiz_window.tableWidget, numuneadi, element, miktar, birim, durumu)

        # todo: show results
        self.engine.result_image()

        # reset remainingrecord
        self.remainingrecord = self.analiz_window.howmanyrecordSpinBox.value()



    def init_analiz_window(self):
        # self.analiz_window.setFixedSize(self.w, self.h)
        loadUi('../ui/analiz_window.ui', self.analiz_window)
        self.analiz_window.setWindowTitle('Analiz')

        # self.analiz_window.lazeratissayisiCB.addItems(list(map(str, range(1, 11))))
        self.analiz_window.howmanyrecordSpinBox.valueChanged.connect(self.on_howmanyrecordSpinBox_valueChanged)
        self.analiz_window.howmanyrecordSpinBox.setValue(10)
        self.remainingrecord = self.analiz_window.howmanyrecordSpinBox.value()

        self.analiz_window.birimCB.addItems(['%', 'ppm', 'kg/da'])

        OceanViewGui.setButtonIcon(self.analiz_window.analyzeButton, '../ui/icon/play-button.png')
        self.analiz_window.analyzeButton.clicked.connect(self.on_analyzeButton_clicked)

        table_widget = self.analiz_window.tableWidget
        self.createTable(table_widget)


        header = table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # pixmap = QPixmap('../ui/icon/result.png')
        # self.analiz_window.resultLabel.setPixmap(pixmap)
        # self.analiz_window.resultLabel.setScaledContents(True)
        # self.analiz_window.resultLabel.setFixedSize(364, 265)
        # # self.analiz_window.resultLabel.setSizePolicy(QSizePolicy.Prefered, QSizePolicy.Prefered)
        # self.analiz_window.resultLabel.show()

        OceanViewGui.setButtonIcon(self.analiz_window.backtohomeButton, '../ui/icon/back.png')
        self.analiz_window.backtohomeButton.clicked.connect(self.on_backtohomeButton_clicked)

        # fixme
        self.analiz_window.resultLayout.setSizePolicy(QSizePolicy.Prefered, QSizePolicy.Prefered)
        self.analiz_window.resultLayout.addWidget(self.engine.result_image())

    def init_tbs_window(self):
        # self.tbs_window.setFixedSize(self.w, self.h)
        loadUi('../ui/tbs_window.ui', self.tbs_window)
        self.tbs_window.setWindowTitle('Tarım Bilgi Sistemi')

        OceanViewGui.setButtonIcon(self.tbs_window.backtohomeButton, '../ui/icon/back.png')
        self.tbs_window.backtohomeButton.clicked.connect(self.on_backtohomeButton_clicked)

if __name__ == '__main__':

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