from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from . import config

app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app=app)

login = LoginManager(app=app)
mail = Mail(app)
