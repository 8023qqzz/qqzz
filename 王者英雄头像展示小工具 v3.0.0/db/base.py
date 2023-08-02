# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

BASEDIR = os.path.dirname(os.path.abspath(__file__))
database = "sqlite:///{}".format(os.path.join(BASEDIR, 'hero.db3'))
# 建立连接
engine = create_engine(database, echo=False)
# 创建会话
Session = sessionmaker(bind=engine)
# 创建映射基类
Base = declarative_base()
