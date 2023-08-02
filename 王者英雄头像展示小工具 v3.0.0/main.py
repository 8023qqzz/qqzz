# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QGraphicsOpacityEffect, \
    QMessageBox
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from formUI.form import Ui_MainWindow as Form
from sqlalchemy import or_
import sys
import requests
from db.base import Session
from db.models import Hero
from concurrent.futures import ThreadPoolExecutor


class HeroThread(QThread):
    signal = pyqtSignal(list)

    def run(self):
        session = Session()
        # 获取数据库中所有英雄数据 [(),(),...]
        hero_list = session.query(Hero.head_link, Hero.cname).all()

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(self.worker, hero) for hero in hero_list]

        hero_pool = [future.result() for future in futures]
        self.signal.emit(hero_pool)

    def worker(self, hero):
        response = requests.get(url=hero[0])
        image_bytes = response.content
        return image_bytes, hero[1]


class RadioThread(QThread):
    signal = pyqtSignal(list)

    info = {
        "坦克": 3,
        "战士": 1,
        "刺客": 4,
        "法师": 2,
        "射手": 5,
        "辅助": 6
    }

    def __init__(self, type):
        super(RadioThread, self).__init__()
        self.type = type

    def run(self):
        session = Session()
        # 获取满足条件的英雄数据
        hero_list = session.query(Hero.head_link, Hero.cname).filter(
            or_(Hero.hero_type == self.info[self.type], Hero.hero_type2 == self.info[self.type])).all()

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(self.worker, hero) for hero in hero_list]

        hero_pool = [future.result() for future in futures]
        self.signal.emit(hero_pool)

    def worker(self, hero):
        response = requests.get(url=hero[0])
        image_bytes = response.content
        return image_bytes, hero[1]


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.ui = Form()
        self.ui.setupUi(self)

        # 生成会话
        self.session = Session()

        # 在 ScrollArea 区域中添加垂直布局
        self.VLayout = QVBoxLayout()
        # 在 QScrollArea布局中只能对scrollAreaWidgetContents进行设置，这个比较特殊，scrollAreaWidgetContents 本质就是一个QWidget布局
        self.ui.scrollAreaWidgetContents.setLayout(self.VLayout)
        # 设置字体
        self.ui.scrollAreaWidgetContents.setFont(QFont("黑体"))

        self.ht = HeroThread()
        self.ht.signal.connect(self.update_scrollArea)
        self.ht.start()

        # 搜索按钮
        self.ui.btn_search.clicked.connect(self.event_search_clicked)

        # 单选按钮
        self.ui.radioButton_1.clicked.connect(self.event_radio_clicked)
        self.ui.radioButton_2.clicked.connect(self.event_radio_clicked)
        self.ui.radioButton_3.clicked.connect(self.event_radio_clicked)
        self.ui.radioButton_4.clicked.connect(self.event_radio_clicked)
        self.ui.radioButton_5.clicked.connect(self.event_radio_clicked)
        self.ui.radioButton_6.clicked.connect(self.event_radio_clicked)
        self.ui.radioButton_7.clicked.connect(self.event_radio_clicked)

    # 获取数据 更新王者头像展示
    def update_scrollArea(self, data):
        frame = QFrame()
        hbox = QHBoxLayout(frame)

        for k, item in enumerate(data):
            img = QImage.fromData(item[0])
            label = QLabel()
            label.setFixedWidth(90)
            label.setFixedHeight(90)
            label.setPixmap(QPixmap.fromImage(img))

            hero_name = QLabel(item[1])
            hero_name.setAlignment(Qt.AlignHCenter)
            hero_name.setFixedWidth(90)

            vbox = QVBoxLayout()
            vbox.addWidget(label)
            vbox.addWidget(hero_name)

            hbox.addLayout(vbox)

            # 如果满足8个 重新赋值新的Qframe 相当于换行
            if k % 8 == 7:
                self.VLayout.addWidget(frame)
                frame = QFrame()
                hbox = QHBoxLayout(frame)

        if 0 < hbox.count() < 8:
            for _ in range(8 - hbox.count()):
                label = QLabel(" ")
                label.setFixedWidth(90)
                label.setFixedHeight(90)
                hero_name = QLabel(" ")
                hero_name.setFixedWidth(90)
                vbox = QVBoxLayout()
                vbox.addWidget(label)
                vbox.addWidget(hero_name)

                # 设置label和checkbox透明度为0
                op = QGraphicsOpacityEffect()
                op.setOpacity(0.0)
                label.setGraphicsEffect(op)
                hero_name.setGraphicsEffect(op)
                hbox.addLayout(vbox)

            self.VLayout.addWidget(frame)

    # 搜索事件绑定
    def event_search_clicked(self):
        # 获取输入框的内容
        cname = self.ui.lineEdit.text().strip()
        cname_obj = self.session.query(Hero.head_link).filter(Hero.cname == cname)
        hero = cname_obj.first()

        if cname_obj.count() <= 0:
            QMessageBox.warning(self, "错误", "您输入的英雄查询不到")
            return

        # 清空布局
        self.clear_layout()

        # 重新布局
        frame = QFrame()
        h_layout = QHBoxLayout()
        frame.setLayout(h_layout)
        frame.setFixedHeight(135)

        response = requests.get(url=hero[0])
        img = QImage.fromData(response.content)
        label = QLabel()
        label.setFixedWidth(90)
        label.setFixedHeight(90)
        label.setPixmap(QPixmap.fromImage(img))

        hero_name = QLabel(cname)
        hero_name.setAlignment(Qt.AlignHCenter)
        hero_name.setFixedWidth(90)

        V_layout = QVBoxLayout()
        V_layout.addWidget(label)
        V_layout.addWidget(hero_name)

        h_layout.addLayout(V_layout)

        self.VLayout.addWidget(frame)

    # 单选按钮 事件绑定
    def event_radio_clicked(self):
        sender = self.sender()
        if sender.text() == "全部":
            self.clear_layout()
            # 再次使用初始化时候的线程
            self.ht.start()
        else:
            self.clear_layout()

            self.rt = RadioThread(type=sender.text())
            self.rt.signal.connect(self.update_scrollArea_R)
            # 子线程结束 销毁子线程对象
            self.rt.finished.connect(lambda: self.rt.deleteLater())
            self.rt.start()

    # 点击单选 更新scrollArea
    def update_scrollArea_R(self, data):
        frame = QFrame()
        hbox = QHBoxLayout(frame)
        frame.setFixedHeight(135)

        for k, item in enumerate(data):
            img = QImage.fromData(item[0])
            label = QLabel()
            label.setFixedWidth(90)
            label.setFixedHeight(90)
            label.setPixmap(QPixmap.fromImage(img))

            hero_name = QLabel(item[1])
            hero_name.setAlignment(Qt.AlignHCenter)
            hero_name.setFixedWidth(90)

            vbox = QVBoxLayout()
            vbox.addWidget(label)
            vbox.addWidget(hero_name)

            hbox.addLayout(vbox)

            # 满足8个 就进入创建新的Qframe
            if k % 8 == 7:
                self.VLayout.addWidget(frame)
                frame = QFrame()
                hbox = QHBoxLayout(frame)
                frame.setFixedHeight(135)

        if 0 < hbox.count() < 8:
            for _ in range(8 - hbox.count()):
                label = QLabel(" ")
                label.setFixedWidth(90)
                label.setFixedHeight(90)
                hero_name = QLabel(" ")
                hero_name.setFixedWidth(90)
                vbox = QVBoxLayout()
                vbox.addWidget(label)
                vbox.addWidget(hero_name)

                # 设置label和checkbox透明度为0
                op = QGraphicsOpacityEffect()
                op.setOpacity(0.0)
                label.setGraphicsEffect(op)
                hero_name.setGraphicsEffect(op)
                hbox.addLayout(vbox)

            self.VLayout.addWidget(frame)

    # 清空布局
    def clear_layout(self):
        if self.VLayout.count() > 0:
            for i in range(self.VLayout.count()):
                self.VLayout.itemAt(i).widget().deleteLater()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())
