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
        self.pixmap = None
        self.map_file = None
        self.toponym_longitude = None
        self.toponym_lattitude = None
        self.mark = False

        uic.loadUi('file.ui', self)
        self.adr = 'Москва, ул.Тверская'
        self.delta = "0.005"
        self.up = 0
        self.right = 0

        self.findbutton.clicked.connect(self.get_adress)
        self.checkBox.clicked.connect(self.indexx)
        self.index.hide()
        self.deletebutton.clicked.connect(self.delete)
        self.pushButton_up.clicked.connect(self.do_minus)
        self.pushButton_down.clicked.connect(self.do_plus)
        self.comboBox.addItems(['схема', 'спутник', 'гибрид'])
        self.scheme = str(self.comboBox.currentText())
        self.pushButton_scheme.clicked.connect(self.show_scheme)

        self.get_image()
        self.initUI()


    def show_scheme(self):
        self.get_image()
        self.initUI()

    def indexx(self):
        if self.checkBox.isChecked():
            self.index.show()
        else:
            self.index.hide()

    def delete(self):
        self.findline.clear()
        self.adr = 'Москва, ул.Тверская'
        self.get_image()
        self.initUI()
        self.mark = False

    def do_up(self):
        self.up = self.up + float(self.delta)
        self.get_image()
        self.initUI()

    def do_down(self):
        self.up = self.up - float(self.delta)
        self.get_image()
        self.initUI()

    def do_right(self):
        self.right = self.right + float(self.delta)
        self.get_image()
        self.initUI()

    def do_left(self):
        self.right = self.right - float(self.delta)
        self.get_image()
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
        elif event.key() == Qt.Key_Plus:
            self.do_plus()
        elif event.key() == Qt.Key_Minus:
            self.do_minus()

    def get_adress(self):
        self.adr = self.findline.text()
        self.mark = True
        self.up = 0
        self.right = 0
        self.get_image()
        self.initUI()

    def do_minus(self):
        self.delta = str(float(self.delta) * 2)
        if float(self.delta) > 20:
            self.delta = '20'
        self.get_image()
        self.initUI()

    def do_plus(self):
        self.delta = str(float(self.delta) / 2)
        if float(self.delta) < 0.00001:
            self.delta = '0.00001'
        self.get_image()
        self.initUI()

    def get_image(self):
        self.image.setFocus()
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
        address = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]
        self.address.setText(address["formatted"])
        try:
            self.index.setText(address["postal_code"])
        except KeyError:
            self.index.setText("Индекса у этого адреса нет(")
        self.toponym_longitude, self.toponym_lattitude = toponym_coodrinates.split(" ")

        if self.comboBox.currentText() == 'схема':
            scheme = "map"
        elif self.comboBox.currentText() == 'спутник':
            scheme = "sat"
        else:
            scheme = "sat,skl"

        line = ''
        if self.mark:
            line = f"{self.toponym_longitude},{self.toponym_lattitude},pm2ntl"
        self.curr_ll = (float(self.toponym_longitude) + self.right, float(self.toponym_lattitude) + self.up)
        map_params = {
            "ll": ",".join([str(float(self.toponym_longitude) + self.right),
                            str(float(self.toponym_lattitude) + self.up)]),
            "spn": ",".join([self.delta, self.delta]),
            "l": scheme,
            "pt": line,
            "size": ",".join(['450', '450'])
        }
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params=map_params)
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def mousePressEvent(self, event):
        if event.x() in range(31, 481) and event.y() in range(41, 491):
            if event.button() == Qt.LeftButton:
                k = float(self.delta) / 450
                print(event.y(), event.x())
                print(event.y() - 41 - 225, event.x() - 31 - 225)
                x = round((event.x() - 31 - 225) * 2 * k + self.curr_ll[0], 8)
                y = round(-(event.y() - 41 - 225) * k + self.curr_ll[1], 8)
                print(x, y)
                self.curr_ll = (x, y)
                map_params = {
                    "ll": ",".join([str(x), str(y)]),
                    "spn": ",".join([self.delta, self.delta]),
                    "l": "map",
                    "size": ",".join(['450', '450'])
                }
                map_api_server = "http://static-maps.yandex.ru/1.x/"
                response = requests.get(map_api_server, params=map_params)
                self.map_file = "map.png"
                with open(self.map_file, "wb") as file:
                    file.write(response.content)
                self.initUI()

    def initUI(self):
        self.setWindowTitle('Отображение карты')
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
