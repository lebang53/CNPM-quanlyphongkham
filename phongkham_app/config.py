from urllib.parse import quote
from flask_mail import Mail

database_name = 'clinicdb'
database_password = 'Leb@ng532002'

SECRET_KEY = "cdc03376a9f235f53369da5a163d347ca3bd5d9755cf1df6924b68eace7359e3"
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:%s@localhost/%s?charset=utf8mb4' % (quote(database_password), database_name)
SQLALCHEMY_TRACK_MODIFICATIONS = True
PRESCRIPTION = 'prescription'

MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'vipproclinic123@gmail.com'
MAIL_PASSWORD = 'lclj aklx psrv lymk'
MAIL_DEFAULT_SENDER = 'vipproclinic123@gmail.com'
