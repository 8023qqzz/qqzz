# -*- encoding: utf-8 -*-
import requests
import json
import os
from db.models import Item, Bjtwitem
from db.base import Session

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(BASE_DIR, "item.json")
filename_ = os.path.join(BASE_DIR, "bjtwitem.json")


# 获取常规模式Item
def get_itemlist():
    url = "https://pvp.qq.com/web201605/js/item.json"
    response = requests.get(url)
    with open(filename, 'wt', encoding='utf-8') as f:
        json.dump(response.json(), f, indent=2, ensure_ascii=False)


def get_bjtwitem():
    url = "https://pvp.qq.com/zlkdatasys/data_zlk_bjtwitem.json"
    response = requests.get(url)

    with open(filename_, 'wt', encoding='utf-8') as f:
        json.dump(response.json().get("bjtwzbsy_ba"), f, indent=2, ensure_ascii=False)


def update_table_Item():
    session = Session()

    with open(filename, 'rt', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        try:
            i = Item(
                item_id=item.get("item_id"),
                item_name=item.get("item_name"),
                item_type=item.get("item_type"),
                price=item.get("price"),
                total_price=item.get('total_price'),
                des1=item.get('des1'),
                des2=item.get('des2'),
                item_link="https://game.gtimg.cn/images/yxzj/img201606/itemimg/{}.jpg".format(item.get("item_id"))
            )
            session.add(i)
            session.commit()
            print(item.get("item_name"))
        except:
            session.rollback()


def update_table_Bjtwitem():
    session = Session()
    with open(filename_, 'rt', encoding='utf-8') as f:
        data = json.load(f)

    for i in data:
        try:
            b = Bjtwitem(
                itemidzbid_4a=i.get('itemidzbid_4a'),
                itemlvzbdj_96=i.get('itemlvzbdj_96'),
                itemnamezwm_cd=i.get('itemnamezwm_cd'),
                itemtypezbfl_30=i.get('itemtypezbfl_30'),
                des1zbsx_a6=i.get('des1zbsx_a6'),
                des2fszx_cc=i.get('des2fszx_cc'),
                zbid_7c=i.get('zbid_7c'),
                item_link="https://game.gtimg.cn/images/yxzj/img201606/itemimg/{}.jpg".format(i.get('itemidzbid_4a'))
            )
            session.add(b)
            session.commit()
            print(i.get('itemnamezwm_cd'))
        except:
            session.rollback()


update_table_Bjtwitem()
