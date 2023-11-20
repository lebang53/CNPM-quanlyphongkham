from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from phongkham_app import db


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
