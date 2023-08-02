# -*- encoding: utf-8 -*-
"""
该方法主要是用来下载herolist.json 文件
如果官方更新新的英雄，只需更新该json文件即可
"""
import requests
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(BASE_DIR, 'herolist.json')


def get_herolist():
    url = "https://pvp.qq.com/web201605/js/herolist.json"
    response = requests.get(url)

    with open(filename, 'wt', encoding='utf-8') as f:
        json.dump(response.json(), f, indent=2, ensure_ascii=False)


def sort_hero():
    with open(filename, 'rt', encoding='utf-8') as f:
        data = json.load(f)

    new_data = sorted(data, key=lambda x: x["ename"])
    filename_ = os.path.join(BASE_DIR, "herolist_sorted.json")
    with open(filename_, 'wt', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)


sort_hero()
