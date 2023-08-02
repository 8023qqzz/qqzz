# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer
from base import Base


class Hero(Base):
    __tablename__ = "hero"

    ename = Column(Integer, primary_key=True)
    cname = Column(String(20), nullable=False)
    title = Column(String(20), nullable=False)
    pay_type = Column(Integer)
    new_type = Column(Integer)
    hero_type = Column(Integer)
    hero_type2 = Column(Integer)
    skin_name = Column(String(20))
    moss_id = Column(Integer)
    head_link = Column(String(20))

    def __init__(
            self,
            ename,
            cname,
            title,
            pay_type=None,
            new_type=None,
            hero_type=None,
            hero_type2=None,
            skin_name=None,
            moss_id=None,
            head_link=None
    ):
        """
        :param ename: 英雄id
        :param cname: 英雄名称
        :param title: 标题名称
        :param pay_type: 未知
        :param new_type: 是否是新英雄
        :param hero_type: 英雄类型
        :param hero_type2: 英雄类型2
        :param skin_name: 皮肤名称
        :param moss_id: 未知
        :param head_link: 头像链接
        """
        self.ename = ename
        self.cname = cname
        self.title = title
        self.pay_type = pay_type
        self.new_type = new_type
        self.hero_type = hero_type
        self.hero_type2 = hero_type2
        self.skin_name = skin_name
        self.moss_id = moss_id
        self.head_link = head_link
