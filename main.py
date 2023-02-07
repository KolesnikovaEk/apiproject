import sys
from io import BytesIO
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
import requests
from PIL import Image

SCREEN_SIZE = [600, 450]

class Example(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('file.ui', self)
        self.adr = 'Москва, ул.Тверская'
        self.delta = "0.005"
        self.up = 0
        self.right = 0
        self.comboBox.addItems(['схема', 'спутник', 'гибрид'])
        self.getImage()
        self.initUI()
        self.pushButton_up.clicked.connect(self.do_plus)
        self.pushButton_down.clicked.connect(self.do_minus)
        self.scheme = str(self.comboBox.currentText())


    def do_up(self):
        self.up = self.up + float(self.delta)
        self.getImage()
        self.initUI()

    def do_down(self):
        self.up = self.up - float(self.delta)
        self.getImage()
        self.initUI()

    def do_right(self):
        self.right = self.up + float(self.delta)
        self.getImage()
        self.initUI()

    def do_left(self):
        self.right = self.right - float(self.delta)
        self.getImage()
        self.initUI()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.do_up()
        elif event.key() == Qt.Key_Down:
            self.do_down()
        elif event.key() == Qt.Key_Right:
            self.do_right()
        elif event.key() == Qt.Key_Left:
            self.do_left()

    def get_adress(self):
        self.adr = self.lineEdit.text()
        self.getImage()
        self.initUI()

    def do_plus(self):
        self.delta = str(float(self.delta) + 0.005)
        if float(self.delta) > 1:
            self.delta = '1'
        self.getImage()
        self.initUI()

    def do_minus(self):
        self.delta = str(float(self.delta) - 0.005)
        if float(self.delta) < 0.00001:
            self.delta = '0.00001'
        self.getImage()
        self.initUI()

    def getImage(self):
        toponym_to_find = self.adr
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": toponym_to_find,
            "format": "json"}
        response = requests.get(geocoder_api_server, params=geocoder_params)
        if not response:
            pass
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        self.toponym_longitude, self.toponym_lattitude = toponym_coodrinates.split(" ")
        if self.comboBox.currentText() == 'схема':
            scheme = "map"
        elif self.comboBox.currentText() == 'спутник':
            scheme = "sat"
        else:
            scheme = "sat,skl"
        map_params = {
            "ll": ",".join([str(float(self.toponym_longitude) + self.up), str(float(self.toponym_lattitude) + self.right)]),
            "spn": ",".join([self.delta, self.delta]),
            "l": scheme
        }
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params=map_params)
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())

