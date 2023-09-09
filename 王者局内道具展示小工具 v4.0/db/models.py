# -*- encoding: utf-8 -*-
from db import Base, Engine
from sqlalchemy import Column, Integer, String, LargeBinary


# 常规 道具
class Item(Base):
    __tablename__ = "item"

    item_id = Column(Integer, primary_key=True, nullable=True)
    item_name = Column(String(20), nullable=True)
    item_type = Column(Integer)
    price = Column(Integer)
    total_price = Column(Integer)
    des1 = Column(String(20))
    des2 = Column(String(20))
    item_binary = Column(LargeBinary)

    def __init__(self,
                 item_id,
                 item_name,
                 item_type,
                 price=None,
                 total_price=None,
                 des1=None,
                 des2=None,
                 item_binary=None
                 ):
        self.item_id = item_id
        self.item_name = item_name
        self.item_type = item_type
        self.price = price
        self.total_price = total_price
        self.des1 = des1
        self.des2 = des2
        self.item_binary = item_binary


# 边境突围 道具
class Bjtwitem(Base):
    __tablename__ = "bjtwitem"

    itemidzbid_4a = Column(String(20), nullable=True, primary_key=True)
    itemlvzbdj_96 = Column(String(20), nullable=True)
    itemnamezwm_cd = Column(String(20), nullable=True)
    itemtypezbfl_30 = Column(String(20))
    des1zbsx_a6 = Column(String(20))
    des2fszx_cc = Column(String(20))
    zbid_7c = Column(String(20))
    item_binary = Column(LargeBinary)

    def __init__(self,
                 itemidzbid_4a,
                 itemlvzbdj_96,
                 itemnamezwm_cd,
                 itemtypezbfl_30,
                 des1zbsx_a6,
                 des2fszx_cc,
                 zbid_7c,
                 item_binary
                 ):
        self.itemidzbid_4a = itemidzbid_4a
        self.itemlvzbdj_96 = itemlvzbdj_96
        self.itemnamezwm_cd = itemnamezwm_cd
        self.itemtypezbfl_30 = itemtypezbfl_30
        self.des1zbsx_a6 = des1zbsx_a6
        self.des2fszx_cc = des2fszx_cc
        self.zbid_7c = zbid_7c
        self.item_binary = item_binary


if __name__ == '__main__':
    Item.metadata.create_all(bind=Engine)
    Bjtwitem.metadata.create_all(bind=Engine)
