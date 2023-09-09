# -*- coding: utf-8 -*-
import requests
import os
import json
from db.models import Hero
from db import Session

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(BASE_DIR, 'herolist.json')
session = Session()


# 下载herolist.json文件
def get_heroList_file():
    url = "https://pvp.qq.com/web201605/js/herolist.json"
    response = requests.get(url)

    with open(filename, 'wt', encoding='utf-8') as f:
        json.dump(response.json(), f, indent=2, ensure_ascii=False)


# 下载图片数据
def get_heroBinary(url):
    response = requests.get(url)
    heroBinary = response.content
    return heroBinary


# 更新数据哭数据
def update_SQL():
    with open(filename, 'rt', encoding='utf-8') as f:
        heroList = json.load(f)

    for hero in heroList:
        try:
            heroObj = Hero(
                ename=hero.get("ename"),
                cname=hero.get('cname'),
                title=hero.get('title'),
                pay_type=hero.get("pay_type"),
                new_type=hero.get('new_type'),
                hero_type=hero.get('hero_type'),
                hero_type2=hero.get('hero_type2'),
                skin_name=hero.get('skin_name'),
                moss_id=hero.get("moss_id"),
                head_binary=get_heroBinary(
                    "https://game.gtimg.cn/images/yxzj/img201606/heroimg/{}/{}.jpg".format(hero.get("ename"),
                                                                                           hero.get("ename")))
            )
            session.add(heroObj)
            session.commit()
            print(hero.get('cname'))
        except Exception as e:
            session.rollback()
            print(e)
        finally:
            session.close()


if __name__ == '__main__':
    update_SQL()
