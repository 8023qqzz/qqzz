# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QVBoxLayout, QMessageBox, QGridLayout
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from Ui.Ui import Ui_MainWindow
from sqlalchemy import or_
import sys
from db import Session
from db.models import Hero


# 获取所有英雄二进制数据
class HeroThread(QThread):
    ready_signal = pyqtSignal(list)

    def run(self):
        session = Session()

        # 获取头像二进制 [(cname,herd_binary),...]
        heroList = session.query(Hero.cname, Hero.head_binary).all()
        self.ready_signal.emit(heroList)

        session.close()


# 英雄职业类型 分类
class HeroTypeThread(QThread):
    ready_signal = pyqtSignal(list)

    info = {
        "坦克": 3,
        "战士": 1,
        "刺客": 4,
        "法师": 2,
        "射手": 5,
        "辅助": 6
    }

    def __init__(self, type: str = None):
        super().__init__()
        self.type = type

    def run(self):
        if self.type:
            session = Session()

            # 满足条件 [(cname,herd_binary),...]
            heroList = session.query(Hero.cname, Hero.head_binary).filter(
                or_(Hero.hero_type == self.info[self.type], Hero.hero_type2 == self.info[self.type])).all()

            self.ready_signal.emit(heroList)

            session.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 滚动区域 网格布局
        self.GridBox = QGridLayout(self.ui.scrollAreaWidgetContents)
        self.ui.scrollAreaWidgetContents.setFont(QFont("黑体"))

        # 设置滚动区域 头像
        self.heroThreading = HeroThread()
        self.heroThreading.ready_signal.connect(self.event_updateScrollArea)
        self.heroThreading.start()

        # 单选按钮 英雄类型 分类
        self.ui.radioButton_1.clicked.connect(self.event_radioClicked)
        self.ui.radioButton_2.clicked.connect(self.event_radioClicked)
        self.ui.radioButton_3.clicked.connect(self.event_radioClicked)
        self.ui.radioButton_4.clicked.connect(self.event_radioClicked)
        self.ui.radioButton_5.clicked.connect(self.event_radioClicked)
        self.ui.radioButton_6.clicked.connect(self.event_radioClicked)
        self.ui.radioButton_7.clicked.connect(self.event_radioClicked)

        # 搜索按钮 搜索英雄 模糊匹配
        self.ui.btn_search.clicked.connect(self.event_btnSearchClicked)

        # 初始化 英雄类型 分类 单例模式
        self.heroTypeThreading = HeroTypeThread()
        self.heroTypeThreading.ready_signal.connect(self.event_updateScrollArea)

    # 设置scrollArea 切换英雄 展示
    def event_updateScrollArea(self, heroList: list):
        """
        :param heroList: [(cname,head_binary),...]
        """
        # 清空原始英雄头像
        self.clear_layout()
        # 分成8个一组 [[(cname,head_binary),...8],...]
        heroGroup = [heroList[i:i + 8] for i in range(0, len(heroList), 8)]

        for index, item in enumerate(heroGroup):
            # index 行数
            for column, value in enumerate(item):
                # column 列数 ;value:(cname,head_binary)
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

                # 添加到网格布局中
                self.GridBox.addLayout(VBox, index, column)

    # 切换英雄类型
    def event_radioClicked(self):
        sender = self.sender()

        if sender.text() == "全部":
            # 再次使用初始化时候的线程
            self.heroThreading.start()
        else:
            self.heroTypeThreading.type = sender.text()
            self.heroTypeThreading.start()

    # 切换搜索英雄
    def event_btnSearchClicked(self):
        session = Session()

        # 输入框 文本
        hero_name = self.ui.lineEdit.text().strip()
        heroList = session.query(Hero.cname, Hero.head_binary).filter(
            Hero.cname.like(f'%{hero_name}%')).all()  # [(head_binary,)]

        if len(heroList) == 0:
            QMessageBox.warning(self, "错误", "您输入的英雄查询不到")
            return

        self.event_updateScrollArea(heroList)
        session.close()

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
