import sys
from io import BytesIO
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
import requests
from PIL import Image

SCREEN_SIZE = [900, 450]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.pixmap = None
        self.map_file = None
        self.toponym_longitude = None
        self.toponym_lattitude = None

        uic.loadUi('file.ui', self)
        self.adr = 'Москва, ул.Тверская'
        self.delta = "0.005"
        self.up = 0
        self.right = 0
        self.get_image()
        self.initUI()

        self.findbutton.clicked.connect(self.get_adress)
        self.deletebutton.clicked.connect(self.delete)
        self.pushButton_up.clicked.connect(self.do_plus)
        self.pushButton_down.clicked.connect(self.do_minus)

    def delete(self):
        self.findline.clear()
        self.adr = 'Москва, ул.Тверская'
        self.get_image()
        self.initUI()
        # remove mark

    def do_up(self):
        self.up = self.up + float(self.delta)
        self.get_image()
        self.initUI()

    def do_down(self):
        self.up = self.up - float(self.delta)
        self.get_image()
        self.initUI()

    def do_right(self):
        self.right = self.up + float(self.delta)
        self.get_image()
        self.initUI()

    def do_left(self):
        self.right = self.right - float(self.delta)
        self.get_image()
        self.initUI()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:
            self.do_up()
        elif event.key() == Qt.Key_S:
            self.do_down()
        elif event.key() == Qt.Key_D:
            self.do_right()
        elif event.key() == Qt.Key_A:
            self.do_left()
        elif event.key() == Qt.Key_Plus:
            self.do_plus()
        elif event.key() == Qt.Key_Minus:
            self.do_minus()

    def get_adress(self):
        self.adr = self.findline.text()
        self.get_image()
        self.initUI()

    def do_minus(self):
        self.delta = str(float(self.delta) + 0.005)
        if float(self.delta) > 1:
            self.delta = '1'
        self.get_image()
        self.initUI()

    def do_plus(self):
        self.delta = str(float(self.delta) - 0.005)
        if float(self.delta) < 0.00001:
            self.delta = '0.00001'
        self.get_image()
        self.initUI()

    def get_image(self):
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
        map_params = {
            "ll": ",".join([str(float(self.toponym_longitude) + self.up),
                            str(float(self.toponym_lattitude) + self.right)]),
            "spn": ",".join([self.delta, self.delta]),
            "l": "map"
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
