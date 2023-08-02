# -*- encoding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
database = "sqlite:///{}".format(os.path.join(BASE_DIR, "item.db3"))

engine = create_engine(database, echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()
