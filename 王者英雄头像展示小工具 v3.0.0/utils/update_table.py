# -*- encoding: utf-8 -*-
"""
该文件是用来更新数据库表文件的
前提是必须下载herlist.json文件
"""
from db.models import Hero
from db.base import Session
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(BASE_DIR, 'herolist.json')
session = Session()

with open(filename, 'rt', encoding='utf-8') as f:
    data_dic = json.load(f)

for item in data_dic:
    try:
        hero = Hero(
            ename=item.get("ename"),
            cname=item.get('cname'),
            title=item.get('title'),
            pay_type=item.get("pay_type"),
            new_type=item.get('new_type'),
            hero_type=item.get('hero_type'),
            hero_type2=item.get('hero_type2'),
            skin_name=item.get('skin_name'),
            moss_id=item.get("moss_id"),
            head_link="https://game.gtimg.cn/images/yxzj/img201606/heroimg/{}/{}.jpg".format(item.get("ename"),
                                                                                             item.get("ename"))
        )
        session.add(hero)
        session.commit()
        print(item.get('cname'))
    except Exception as e:
        print(e)
        session.rollback()

session.close()
