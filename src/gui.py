import sys
from PyQt5.QtCore import pyqtSlot, Qt, QRect, QDateTime, QUrl
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QSpinBox, QMessageBox, QLineEdit, QMainWindow, \
    QGraphicsView, QLabel, QStyle, QSizePolicy, QWidget, QTableWidgetItem, QHeaderView, QComboBox, QDateTimeEdit
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QPen, QPixmap


from PyQt5 import QtWebEngineWidgets

from iomanager import IOManager
from analyzer import Analyzer, Database, Sample
from config import Config
from engine import Engine
from util import subplot
from calibration import Calibrator

import pandas as pd
import time
import matplotlib.pyplot as plt

from sample import Sample


class OceanViewGui(QMainWindow):
    def __init__(self, engine, config):
        super(OceanViewGui, self).__init__()

        self.engine = engine
        self.config = config


        if config.mode == "angle_calibration":
            # TODO: pls reconstruct these methods!!
            numune_info = dict(numuneadi='angle_calibration_default',
                               lazeratissayisi=1)
            self.engine.set_numune_info(numune_info)

            while True:
                _, sample = self.engine.read_io()

                sample = Sample(name="angle_calibration_default",
                       dataframe=sample,
                       peak_interval=self.engine.analyzer.peak_interval,
                       is_valid=False,
                        find_peaks=False)

                self.engine.analyzer.sample = sample

                fig, ax = plt.subplots()

                self.engine.analyzer.plot_data(ax, point_peaks=False, draw_verticals=False)


                ax.legend()
                plt.show()



        else:

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
                                          'output/samples/{loc_name}/{sample_id}'.format(loc_name=loc_name,
                                                                                         sample_id=sample_id),
                                          QMessageBox.Ok)

            dir = engine.save_readings()

            # if self.dev_mode:
            #     # Plot readings
            #     subplot(dictionary=readings, xname='wavelengths', yname='intensities', ncols=3)
            #
            #     # Analyze readings
            #     choice = QMessageBox.question(self, 'Analyze',
            #                                   'Do you want to analyze {}-{}'.format(loc_name, sample_id),
            #                                   QMessageBox.Yes | QMessageBox.No)
            #
            #     if choice == QMessageBox.Yes:
            #         # fixme: make it generic
            #         engine.pipeline(loc_name='niğde')

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
        if self.engine.giris_info is None:
            self.show_save_popup('Lütfen giriş sayfasındaki bilgileri doldurun.')
        else:
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
        self.dateTimeEdit = QDateTimeEdit()

        loadUi('../ui/mainw.ui', self)
        self.setWindowTitle('OceanView')
        self.setFixedSize(self.w, self.h)

        self.setWindowIcon(QIcon('../ui/icon/image.png'))

        OceanViewGui.setButtonIcon(self.girisButton, '../ui/icon/house.png')
        OceanViewGui.setButtonIcon(self.analizButton, '../ui/icon/analytics.png')
        OceanViewGui.setButtonIcon(self.tarimsalbilgisistemiButton, '../ui/icon/fertilizer.png')

        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())

    def init_giris_window(self):
        # self.giris_window.setFixedSize(self.w, self.h)
        loadUi('../ui/giris_window.ui', self.giris_window)
        self.giris_window.setWindowTitle('Giriş')

        self.giris_window.uruntipiCB.addItems(['Buğday', 'Arpa', 'Mısır', 'Çeltik',
                                               'A.çiçeği', 'Patates','Ş.pancarı','Bağ',
                                               'Meyve','Sebze','Yonca','Kavak',
                                               'Bostan','Kuru soğan','Sarımsak','K.Fasulye',
                                               'Nohut','Mercimek','Macar Fiğ', 'Yaygın Fiğ',
                                               'Korunga','Kanola','Haşhaş','Havuç',
                                               'Kimyon','Susam'])
        self.giris_window.tarimsekliCB.addItems(['Kuru', 'Sulu'])
        self.giris_window.derinlikCB.addItems(['0-30 cm', '30-60 cm', '60-90 cm', '90-120 cm'])

        OceanViewGui.setButtonIcon(self.giris_window.backtohomeButton, '../ui/icon/back.png')
        OceanViewGui.setButtonIcon(self.giris_window.analizWindowButton, '../ui/icon/analytics.png')
        OceanViewGui.setButtonIcon(self.giris_window.saveButton, '../ui/icon/save.png')
        self.giris_window.backtohomeButton.clicked.connect(self.on_backtohomeButton_clicked)
        self.giris_window.analizWindowButton.clicked.connect(self.on_analizButton_clicked)

        self.giris_window.saveButton.clicked.connect(self.on_saveButton_clicked)

    def show_save_popup(self, text):
        QMessageBox.question(self, 'Bilgi', text, QMessageBox.Ok)

    def read_giriswindow_field(self):
        il = self.giris_window.ilLE.text()
        ilce = self.giris_window.ilceLE.text()
        koy = self.giris_window.koyLE.text()
        adaparsel = self.giris_window.adaparselLE.text()

        uruntipi = self.giris_window.uruntipiCB.currentText()
        tarimsekli = self.giris_window.tarimsekliCB.currentText()
        derinlik = self.giris_window.derinlikCB.currentText()

        return (il, ilce, koy, adaparsel, uruntipi, tarimsekli, derinlik)

    def are_fields_empty(self, field_values):
        for value in field_values:
            if len(value) == 0:
                return True
        return False

    @pyqtSlot()
    def on_saveButton_clicked(self):

        (il, ilce, koy, adaparsel, uruntipi, tarimsekli, derinlik) = self.read_giriswindow_field()

        # check for empty fields
        if self.are_fields_empty((il, ilce, koy, adaparsel, uruntipi, tarimsekli, derinlik)):
            self.show_save_popup('Lütfen bilgileri eksiksiz doldurunuz.')

        else:
            giris_info = dict(il=il,
                              ilce=ilce,
                              koy=koy,
                              adaparsel=adaparsel,
                              uruntipi=uruntipi,
                              tarimsekli=tarimsekli,
                              derinlik=derinlik)

            self.engine.set_giris_info(giris_info)
            self.engine.save_giris_info()

            # done: show saved popup.
            self.show_save_popup('Arazi bilgileri kaydedildi.')

    @pyqtSlot()
    def on_analyzeButton_clicked(self):
        self.analiz_window.progressLabel.setText('Hazır.')
        numuneadi = self.analiz_window.numuneadiLE.text()
        lazeratissayisi = self.analiz_window.howmanyrecordSpinBox.value()

        numune_info = dict(numuneadi=numuneadi,
                           lazeratissayisi=lazeratissayisi)

        self.engine.set_numune_info(numune_info)

        self.analiz_window.progressLabel.setText('Cihazdan okuma yapılıyor...')
        # to update remainingrecord, I need to create a generator
        for self.remainingrecord in self.engine.read_remainingrecords(self.remainingrecord):
            readings = self.engine.readings

        self.analiz_window.progressLabel.setText('Veriler kaydediliyor...')
        dir = self.engine.save_readings()



        # show saved popup
        self.show_save_popup('Atışlar kaydedildi.\nAnalize devam edilecek.')

        self.analiz_window.progressLabel.setText('Analiz yapılıyor...')
        QtWidgets.qApp.processEvents()
        # analyze and show peaks and its neighbours
        (sample, matches) = self.engine.analyze(dir=dir, plotnow=True)




        if matches is not None:
            self.analiz_window.progressLabel.setText('Kalibrasyon verisi işleniyor...')
            # match elements in calibration excel with peak values.
            found_el_intensity_matches = self.engine.calibrate(matches=matches)

            # done: read calibration file

            # done: implement fit calibration

            # numuneadi = self.engine.numune_info['numuneadi']
            # element = 'N 5 @ 443.506'
            # X = self.engine.fit(found_el_intensity_matches[element])
            # miktar = '{:.2f}'.format(X)
            # birim = self.engine.numune_info['birim']
            # durumu = self.engine.limit_values('N', X)

            (names, quantities, statuses, units) = self.engine.analysis_to_ppm_data(found_el_intensity_matches)

            self.analiz_window.progressLabel.setText('Bilgiler işleniyor...')
            # done: fill table
            numuneadi = self.engine.numune_info['numuneadi']
            for name,quantity,status, unit in zip(names, quantities, statuses, units):
                self.engine.data_to_row(self.analiz_window.tableWidget, numuneadi, name, quantity, unit, status)

            # todo: show results
            df = pd.DataFrame()
            df['x'] = ['N', 'OM', 'P2O5', 'K2O']
            df['y'] = [10, 20, 30, 40]
            widget = self.engine.result_image(df)
            widget.setFixedSize(200, 200)
            self.analiz_window.resultLayout.itemAt(0).widget().setParent(None)
            self.analiz_window.resultLayout.addWidget(widget)

        # reset remainingrecord
        self.remainingrecord = self.analiz_window.howmanyrecordSpinBox.value()

        self.analiz_window.progressLabel.setText('Hazır.')

    def init_analiz_window(self):
        # self.analiz_window.setFixedSize(self.w, self.h)
        loadUi('../ui/analiz_window.ui', self.analiz_window)
        self.analiz_window.setWindowTitle('Analiz')

        # self.analiz_window.lazeratissayisiCB.addItems(list(map(str, range(1, 11))))
        self.analiz_window.howmanyrecordSpinBox.valueChanged.connect(self.on_howmanyrecordSpinBox_valueChanged)
        self.analiz_window.howmanyrecordSpinBox.setValue(10)
        self.remainingrecord = self.analiz_window.howmanyrecordSpinBox.value()



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

        widget = self.engine.result_image()
        widget.setFixedSize(200, 200)
        self.analiz_window.resultLayout.addWidget(widget)

    def init_tbs_window(self):
        # self.tbs_window.setFixedSize(self.w, self.h)
        loadUi('../ui/tbs_window.ui', self.tbs_window)
        self.tbs_window.setWindowTitle('Tarım Bilgi Sistemi')

        OceanViewGui.setButtonIcon(self.tbs_window.backtohomeButton, '../ui/icon/back.png')
        self.tbs_window.backtohomeButton.clicked.connect(self.on_backtohomeButton_clicked)

        webView = QtWebEngineWidgets.QWebEngineView(self.tbs_window.webWidget)
        webView.setUrl(QtCore.QUrl("https://tbs.tarbil.gov.tr/Authentication.aspx"))
        webView.setObjectName("webView")



if __name__ == '__main__':
    config = Config('../config.ini')
    engine = Engine(iomanager=IOManager(trigger_mode=4),
                    analyzer=Analyzer(config=config, database=Database(config)),
                    calibrator=Calibrator(input_dir=config.calibration_input_dir,
                                          output_dir=config.calibration_output_dir,
										  calibration_eqns=config.calibration_equation),
                    config=config)

    app = QApplication(sys.argv)

    widget = OceanViewGui(engine=engine, config=config)
    widget.show()

    sys.exit(app.exec_())
