import sys
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget,QMainWindow, QDialog, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.uic import loadUi

class OceanViewGui(QMainWindow):
    def __init__(self):
        super(OceanViewGui, self).__init__()
        self.giris_window = QWidget()
        self.analiz_window = QWidget()
        self.tbs_window = QWidget()

        self.w = 1000
        self.h = 640

        self.init_ui()

        self.init_giris_window()
        self.init_analiz_window()
        self.init_tbs_window()



    @pyqtSlot()
    def on_backtohomeButton_clicked(self):
        self.giris_window.hide()
        self.analiz_window.hide()
        self.tbs_window.hide()
        self.show()



    @staticmethod
    def createTable(tableWidget):
       # Create table
        tableWidget.setRowCount(4)
        tableWidget.setColumnCount(2)
        tableWidget.setItem(0,0, QTableWidgetItem("Cell (1,1)"))
        tableWidget.setItem(0,1, QTableWidgetItem("Cell (1,2)"))
        tableWidget.setItem(1,0, QTableWidgetItem("Cell (2,1)"))
        tableWidget.setItem(1,1, QTableWidgetItem("Cell (2,2)"))
        tableWidget.setItem(2,0, QTableWidgetItem("Cell (3,1)"))
        tableWidget.setItem(2,1, QTableWidgetItem("Cell (3,2)"))
        tableWidget.setItem(3,0, QTableWidgetItem("Cell (4,1)"))
        tableWidget.setItem(3,1, QTableWidgetItem("Cell (4,2)"))


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

        self.setWindowIcon(QIcon('icon/image.png'))

        OceanViewGui.setButtonIcon(self.girisButton, 'icon/house.png')
        OceanViewGui.setButtonIcon(self.analizButton, 'icon/analytics.png')
        OceanViewGui.setButtonIcon(self.tarimsalbilgisistemiButton, 'icon/fertilizer.png')



    def init_giris_window(self):

        # self.giris_window.setFixedSize(self.w, self.h)
        loadUi('giris_window.ui', self.giris_window)
        self.giris_window.setWindowTitle('Giriş')

        self.giris_window.uruntipiCB.addItems(['Bitkisel Ürün'])
        self.giris_window.tarimsekliCB.addItems(['Kuru', 'Sulu'])
        self.giris_window.derinlikCB.addItems(['0-30 cm','30-60 cm','60-90 cm','90-120 cm'])

        OceanViewGui.setButtonIcon(self.giris_window.backtohomeButton, 'icon/back.png')
        self.giris_window.backtohomeButton.clicked.connect(self.on_backtohomeButton_clicked)

    def init_analiz_window(self):

        # self.analiz_window.setFixedSize(self.w, self.h)
        loadUi('analiz_window.ui', self.analiz_window)
        self.analiz_window.setWindowTitle('Analiz')

        self.analiz_window.lazeratissayisiCB.addItems(list(map(str, range(1,11))))
        self.analiz_window.birimCB.addItems(['%','ppm','kg/da'])

        OceanViewGui.setButtonIcon(self.analiz_window.baslatButton, 'icon/play-button.png')


        table_widget = self.analiz_window.tableWidget
        header = table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        pixmap = QPixmap('icon/result.png')
        self.analiz_window.resultLabel.setPixmap(pixmap)
        self.analiz_window.resultLabel.setScaledContents(True)
        self.analiz_window.resultLabel.setFixedSize(364,265)
        # self.analiz_window.resultLabel.setSizePolicy(QSizePolicy.Prefered, QSizePolicy.Prefered)
        self.analiz_window.resultLabel.show()

        OceanViewGui.setButtonIcon(self.analiz_window.backtohomeButton, 'icon/back.png')
        self.analiz_window.backtohomeButton.clicked.connect(self.on_backtohomeButton_clicked)

    def init_tbs_window(self):


        # self.tbs_window.setFixedSize(self.w, self.h)
        loadUi('tbs_window.ui', self.tbs_window)
        self.tbs_window.setWindowTitle('Tarım Bilgi Sistemi')



        OceanViewGui.setButtonIcon(self.tbs_window.backtohomeButton, 'icon/back.png')
        self.tbs_window.backtohomeButton.clicked.connect(self.on_backtohomeButton_clicked)

app = QApplication(sys.argv)

widget = OceanViewGui()
widget.show()

sys.exit(app.exec_())
