# -*- encoding: utf-8 -*-
from base import engine
from models import Item, Bjtwitem

if __name__ == '__main__':
    Item.metadata.create_all(bind=engine)
    Bjtwitem.metadata.create_all(bind=engine)
