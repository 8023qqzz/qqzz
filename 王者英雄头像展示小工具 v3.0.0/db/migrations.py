# -*- coding: utf-8 -*-
from base import engine
from models import Hero


if __name__ == '__main__':
    Hero.metadata.create_all(bind=engine)
