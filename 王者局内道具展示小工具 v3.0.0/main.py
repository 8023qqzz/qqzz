# -*- encoding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont
from formUI.formUI import Ui_Form
from concurrent.futures import ThreadPoolExecutor
from db.base import Session
from db.models import Item, Bjtwitem
import requests


# 常规模式数据获取
class ModeThread(QThread):
    ready = pyqtSignal(list)

    def run(self):
        session = Session()
        # 获取道具数据 [(),(),...]
        item_list = session.query(Item.item_link, Item.item_name).all()

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(self.worker, item) for item in item_list]

        item_pool = [future.result() for future in futures]  # [(image_bytes, item_name),(),...]
        self.ready.emit(item_pool)

    def worker(self, item):
        """
        :param item: obj
        :return: (image_bytes, item_name)
        """
        response = requests.get(url=item[0])
        image_bytes = response.content
        return image_bytes, item[1]


# 边境突围模式数据获取
class BModeThread(QThread):
    ready = pyqtSignal(list)

    def run(self):
        session = Session()
        # 获取道具数据 [(),(),...]
        item_list = session.query(Bjtwitem.item_link, Bjtwitem.itemnamezwm_cd).all()
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(self.worker, item) for item in item_list]

        item_pool = [future.result() for future in futures]  # [(image_bytes, item_name),(),...]
        self.ready.emit(item_pool)

    def worker(self, item):
        """
        :param bitem: obj
        :return: (image_bytes, item_name)
        """
        response = requests.get(url=item[0])
        image_bytes = response.content
        return image_bytes, item[1]


# 搜索数据获取
class SearchThread(QThread):
    ready = pyqtSignal(list)
    error = pyqtSignal()

    def __init__(self, name):
        super(SearchThread, self).__init__()
        self.name = name

    def run(self):
        session = Session()
        # 查询数据 [(),()...]
        item_list = session.query(Item.item_name, Item.item_link) \
            .filter(Item.item_name.like('%' + self.name + '%')) \
            .union(session.query(Bjtwitem.itemnamezwm_cd, Bjtwitem.item_link).filter(
            Bjtwitem.itemnamezwm_cd.like('%' + self.name + '%'))).all()

        # 没查询到数据
        if len(item_list) == 0:
            self.error.emit()
            return

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(self.worker, item) for item in item_list]

        item_pool = [future.result() for future in futures]
        self.ready.emit(item_pool)

    def worker(self, item):
        """
        :param item: (name,item_link)
        :return: (image_bytes, item_name)
        """
        response = requests.get(url=item[1])
        image_bytes = response.content
        return image_bytes, item[0]


# 按钮点击获取数据
class RadioThread(QThread):
    ready = pyqtSignal(list)

    type_1 = {"攻击": 1,
              "法术": 2,
              "防御": 3,
              "移动": 4,
              "打野": 5,
              "游走": 7}

    type_2 = {"装备": "1",
              "道具": "2",
              "额外技能": "3"}

    def __init__(self, item_type):
        super(RadioThread, self).__init__()
        self.item_type = item_type

    def run(self):
        session = Session()

        if self.item_type in self.type_1:
            item_list = session.query(Item.item_name, Item.item_link).filter(
                Item.item_type == self.type_1[self.item_type]).all()
        else:
            item_list = session.query(Bjtwitem.itemnamezwm_cd, Bjtwitem.item_link).filter(
                Bjtwitem.itemtypezbfl_30 == self.type_2[self.item_type]).all()

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(self.worker, item) for item in item_list]

        item_pool = [future.result() for future in futures]
        self.ready.emit(item_pool)

    def worker(self, item):
        response = requests.get(item[1])
        image_bytes = response.content
        return image_bytes, item[0]


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # 模式按钮 信号绑定
        self.ui.radioButton_1.clicked.connect(self.switch_mode)
        self.ui.radioButton_2.clicked.connect(self.switch_mode)

        # 搜索按钮 信号绑定
        self.ui.btn_search.clicked.connect(self.search_item)

        # scrollAreaWidgetContents 区域设置垂直布局
        self.VLayout = QVBoxLayout()
        self.ui.scrollAreaWidgetContents.setLayout(self.VLayout)
        # 设置字体
        self.ui.scrollAreaWidgetContents.setFont(QFont("黑体"))

        # 常规模式展示
        self.mt = ModeThread()
        self.mt.ready.connect(self.update_scrollArea)
        self.mt.start()

        # 边境突围模式展示
        self.bmt = BModeThread()
        self.bmt.ready.connect(self.update_scrollArea_B)
        # 这里不进行start 只需要绑定信号与槽函数

        # 按钮点击 信号绑定
        self.ui.radioButton_11.clicked.connect(self.event_radio_clicked)
        self.ui.radioButton_12.clicked.connect(self.event_radio_clicked)
        self.ui.radioButton_13.clicked.connect(self.event_radio_clicked)
        self.ui.radioButton_14.clicked.connect(self.event_radio_clicked)
        self.ui.radioButton_15.clicked.connect(self.event_radio_clicked)
        self.ui.radioButton_16.clicked.connect(self.event_radio_clicked)
        self.ui.radioButton_17.clicked.connect(self.event_radio_clicked)
        self.ui.radioButton_21.clicked.connect(self.event_radio_clicked)
        self.ui.radioButton_22.clicked.connect(self.event_radio_clicked)
        self.ui.radioButton_23.clicked.connect(self.event_radio_clicked)
        self.ui.radioButton_24.clicked.connect(self.event_radio_clicked)

    # 常规模式 道具展示
    def update_scrollArea(self, data):
        """
        :param data: [(image_bytes, item_name),(...),...]
        """
        # 清空布局
        self.clear_layout()

        frame = QFrame()
        hbox = QHBoxLayout(frame)
        for k, v in enumerate(data):
            vLayout = QVBoxLayout()

            img = QImage.fromData(v[0])
            label = QLabel()
            label.setFixedWidth(90)
            label.setFixedHeight(90)
            label.setPixmap(QPixmap.fromImage(img))

            item_name = QLabel(v[1])
            item_name.setAlignment(Qt.AlignHCenter)
            item_name.setFixedWidth(90)

            vLayout.addWidget(label)
            vLayout.addWidget(item_name)

            hbox.addLayout(vLayout)

            if k % 8 == 7:
                self.VLayout.addWidget(frame)
                frame = QFrame()
                hbox = QHBoxLayout(frame)

        if hbox.count() > 0:
            self.VLayout.addWidget(frame)

    # 边境突围模式 道具展示
    def update_scrollArea_B(self, data):
        # 清空布局
        self.clear_layout()

        frame = QFrame()
        hbox = QHBoxLayout(frame)
        for k, v in enumerate(data):
            vLayout = QVBoxLayout()

            img = QImage.fromData(v[0])
            label = QLabel()
            label.setFixedWidth(90)
            label.setFixedHeight(90)
            label.setPixmap(QPixmap.fromImage(img))

            item_name = QLabel(v[1])
            item_name.setAlignment(Qt.AlignHCenter)
            item_name.setWordWrap(True)
            item_name.setFixedWidth(90)

            vLayout.addWidget(label)
            vLayout.addWidget(item_name)

            hbox.addLayout(vLayout)

            if k % 8 == 7:
                self.VLayout.addWidget(frame)
                frame = QFrame()
                hbox = QHBoxLayout(frame)

        if hbox.count() < 8:
            self.VLayout.addWidget(frame)

    # 切换模式
    def switch_mode(self):
        sender = self.sender()
        if sender.text() == "常规模式":
            self.ui.stackedWidget.setCurrentIndex(0)
            self.mt.start()
        elif sender.text() == "边境突围模式":
            self.ui.stackedWidget.setCurrentIndex(1)
            self.bmt.start()

    # 搜索道具
    def search_item(self):
        item_name = self.ui.lineEdit.text().strip()

        self.st = SearchThread(name=item_name)
        self.st.ready.connect(self.event_search_ready)
        self.st.error.connect(self.event_search_error)
        # 线程 查询结束 销毁子线程
        self.st.finished.connect(lambda: self.st.deleteLater())
        self.st.start()

    # 搜索 ready
    def event_search_ready(self, data):
        self.clear_layout()

        frame = QFrame()
        hbox = QHBoxLayout(frame)
        for k, item in enumerate(data):
            img = QImage.fromData(item[0])
            lable = QLabel()
            lable.setPixmap(QPixmap.fromImage(img))
            lable.setFixedWidth(90)
            lable.setFixedHeight(90)

            item_name = QLabel(item[1])
            item_name.setFixedWidth(90)
            item_name.setAlignment(Qt.AlignHCenter)
            item_name.setWordWrap(True)

            vbox = QVBoxLayout()
            vbox.addWidget(lable)
            vbox.addWidget(item_name)

            hbox.addLayout(vbox)

            if k % 8 == 7:
                self.VLayout.addWidget(frame)
                frame = QFrame()
                hbox = QHBoxLayout(frame)

        if hbox.count() < 8:
            self.VLayout.addWidget(frame)

    # 搜索 error
    def event_search_error(self):
        QMessageBox.warning(self, "error", "您所搜索的道具查询不到!")

    # 单选按钮 事件
    def event_radio_clicked(self):
        sender = self.sender()
        if sender == self.ui.radioButton_11:
            self.mt.start()
        elif sender == self.ui.radioButton_21:
            self.bmt.start()
        else:
            self.rt = RadioThread(sender.text())
            self.rt.ready.connect(self.event_radio_update)
            self.rt.finished.connect(lambda: self.rt.deleteLater())
            self.rt.start()

    # 单选点击 更新布局
    def event_radio_update(self, data):
        self.clear_layout()

        frame = QFrame()
        hbox = QHBoxLayout(frame)
        for k, item in enumerate(data):
            img = QImage.fromData(item[0])
            lable = QLabel()
            lable.setPixmap(QPixmap.fromImage(img))
            lable.setFixedWidth(90)
            lable.setFixedHeight(90)

            item_name = QLabel(item[1])
            item_name.setFixedWidth(90)
            item_name.setAlignment(Qt.AlignHCenter)
            item_name.setWordWrap(True)

            vbox = QVBoxLayout()
            vbox.addWidget(lable)
            vbox.addWidget(item_name)

            hbox.addLayout(vbox)

            if k % 8 == 7:
                self.VLayout.addWidget(frame)
                frame = QFrame()
                hbox = QHBoxLayout(frame)

        if hbox.count() < 8:
            self.VLayout.addWidget(frame)

    # 清空布局
    def clear_layout(self):
        if self.VLayout.count() > 0:
            for i in range(self.VLayout.count()):
                self.VLayout.itemAt(i).widget().deleteLater()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
