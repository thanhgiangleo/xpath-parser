# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
#
# app = Flask(__name__)
#
# POSTGRES = {
#     'user': 'postgres',
#     'pw': '123',
#     'db': 'mh',
#     'host': 'mh-x1',
#     'port': '5431',
# }
#
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
#
# db = SQLAlchemy(app)

from . import db
from ..models import BaseModel

import datetime


class Domain(db.Model, BaseModel):
    username = db.Column(
        db.String, primary_key=True,
        unique=True, nullable=False)
    avatar_url = db.Column(db.String, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, username: str, avatar_url: str = ''):
        self.username = username
        self.avatar_url = avatar_url