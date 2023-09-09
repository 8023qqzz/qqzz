# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMessageBox, QGridLayout
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont
from Ui.Ui import Ui_Form
from db import Session
from db.models import Item, Bjtwitem
import sys


# 常规道具 数据
class ItemThread(QThread):
    ready_signal = pyqtSignal(list)

    def run(self):
        session = Session()
        # 常规道具 二进制数据 [(item_name,item_binary),...]
        itemList = session.query(Item.item_name, Item.item_binary).all()

        self.ready_signal.emit(itemList)
        session.close()


# 边境突围 道具 数据
class BjtwItemThread(QThread):
    ready_signal = pyqtSignal(list)

    def run(self):
        session = Session()
        # 边境突围 道具 二进制数据 [(itemnamezwm_cd,item_binary),...]
        itemList = session.query(Bjtwitem.itemnamezwm_cd, Bjtwitem.item_binary).all()

        self.ready_signal.emit(itemList)
        session.close()


# 道具类型 数据
class ItemTypeThread(QThread):
    ready_signal = pyqtSignal(list)
    item_type_mapper = {"攻击": 1,
                        "法术": 2,
                        "防御": 3,
                        "移动": 4,
                        "打野": 5,
                        "游走": 7}
    bjtw_type_mapper = {"装备": 1,
                        "道具": 2,
                        "额外技能": 3}

    def __init__(self, item_type: str = None):
        super().__init__()
        self.item_type = item_type

    def run(self):
        if self.item_type:
            session = Session()

            if self.item_type in self.item_type_mapper:
                itemList = session.query(Item.item_name, Item.item_binary).filter(
                    Item.item_type == self.item_type_mapper[self.item_type]).all()
            else:
                itemList = session.query(Bjtwitem.itemnamezwm_cd, Bjtwitem.item_binary).filter(
                    Bjtwitem.itemtypezbfl_30 == self.bjtw_type_mapper[self.item_type]).all()

            self.ready_signal.emit(itemList)
            session.close()


# 搜索道具 数据
class SearchItemThread(QThread):
    ready_signal = pyqtSignal(list)
    error_signal = pyqtSignal()

    def __init__(self, name: str = None):
        super().__init__()
        self.name = name

    def run(self):
        if self.name:
            session = Session()
            # 查询数据 [(),()...]
            itemList = session.query(Item.item_name, Item.item_binary) \
                .filter(Item.item_name.like('%' + self.name + '%')) \
                .union(session.query(Bjtwitem.itemnamezwm_cd, Bjtwitem.item_binary).filter(
                Bjtwitem.itemnamezwm_cd.like('%' + self.name + '%'))).all()

            # 没查询到数据
            if len(itemList) == 0:
                self.error_signal.emit()
                return

            self.ready_signal.emit(itemList)


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # scrollArea 网格布局
        self.GridBox = QGridLayout()
        self.ui.scrollAreaWidgetContents.setLayout(self.GridBox)
        self.ui.scrollAreaWidgetContents.setFont(QFont("黑体"))

        # 常规道具
        self.itemThreading = ItemThread()
        self.itemThreading.ready_signal.connect(self.event_updateScrollArea)
        self.itemThreading.start()

        # 边境突围 道具
        self.bjtwItemThreading = BjtwItemThread()
        self.bjtwItemThreading.ready_signal.connect(self.event_updateScrollArea)

        # 常规道具 边境突围道具 按钮切换
        self.ui.radioButton_1.clicked.connect(self.event_toggleMode)
        self.ui.radioButton_2.clicked.connect(self.event_toggleMode)

        # 道具类型 数据 线程 初始化
        self.itemTypeThread = ItemTypeThread()
        self.itemTypeThread.ready_signal.connect(self.event_updateScrollArea)

        # 道具类型 切换
        self.ui.radioButton_11.clicked.connect(self.event_radioClicked)
        self.ui.radioButton_12.clicked.connect(self.event_radioClicked)
        self.ui.radioButton_13.clicked.connect(self.event_radioClicked)
        self.ui.radioButton_14.clicked.connect(self.event_radioClicked)
        self.ui.radioButton_15.clicked.connect(self.event_radioClicked)
        self.ui.radioButton_16.clicked.connect(self.event_radioClicked)
        self.ui.radioButton_17.clicked.connect(self.event_radioClicked)
        self.ui.radioButton_21.clicked.connect(self.event_radioClicked)
        self.ui.radioButton_22.clicked.connect(self.event_radioClicked)
        self.ui.radioButton_23.clicked.connect(self.event_radioClicked)
        self.ui.radioButton_24.clicked.connect(self.event_radioClicked)

        # 搜素数据 线程 初始化
        self.searchItemThread = SearchItemThread()
        self.searchItemThread.ready_signal.connect(self.event_updateScrollArea)
        self.searchItemThread.error_signal.connect(lambda: QMessageBox.warning(self, "错误", "您输入的道具不存在"))

        # 搜索道具
        self.ui.btn_search.clicked.connect(self.event_searchItem)

    # scrollArea 道具展示
    def event_updateScrollArea(self, itemList: list):
        # 清空原始英雄头像
        self.clear_layout()
        # 分成8个一组 [[(item_name,item_binary),...8],...]
        itemGroup = [itemList[i:i + 8] for i in range(0, len(itemList), 8)]

        for index, item in enumerate(itemGroup):
            # index 行数
            for column, value in enumerate(item):
                # column 列数; value:(item_name,item_binary)
                # 布局
                VBox = QVBoxLayout()
                hero_img = QLabel()
                hero_img.setFixedWidth(90)
                hero_img.setFixedHeight(90)
                img = QImage.fromData(value[1])
                hero_img.setPixmap(QPixmap.fromImage(img))

                hero_name = QLabel(value[0])
                hero_name.setAlignment(Qt.AlignHCenter)
                hero_name.setFixedWidth(90)

                VBox.addWidget(hero_img)
                VBox.addWidget(hero_name)

                # 布局添加到网格布局中
                self.GridBox.addLayout(VBox, index, column)

    # 切换 道具 模式
    def event_toggleMode(self):
        sender = self.sender()
        if sender.text() == "常规模式":
            self.ui.stackedWidget.setCurrentIndex(0)
            self.itemThreading.start()
        elif sender.text() == "边境突围模式":
            self.ui.stackedWidget.setCurrentIndex(1)
            self.bjtwItemThreading.start()

    # 切换 道具 类型
    def event_radioClicked(self):
        sender = self.sender()

        if sender == self.ui.radioButton_11:
            self.itemThreading.start()
        elif sender == self.ui.radioButton_21:
            self.bjtwItemThreading.start()
        else:
            self.itemTypeThread.item_type = sender.text()
            self.itemTypeThread.start()

    # 搜索 道具
    def event_searchItem(self):
        item_name = self.ui.lineEdit.text().strip()
        self.searchItemThread.name = item_name
        self.searchItemThread.start()

    # 清空布局
    def clear_layout(self):
        if self.GridBox.count() > 0:
            for i in range(self.GridBox.count()):
                self.GridBox.itemAt(i).layout().itemAt(0).widget().deleteLater()
                self.GridBox.itemAt(i).layout().itemAt(1).widget().deleteLater()
                self.GridBox.itemAt(i).layout().deleteLater()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
