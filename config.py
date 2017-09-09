#
import os
# системный настройки
SECRET_KEY = 'secret_key'
SECURITY_PASSWORD_SALT = '\x87\xc6\xfd-=\x10\x02\x18#|\xb8\xe1E|\xaa)\xc2\x02rz\xd7\xc8\xd7$\x017\xbeb\x99'
WTF_CSRF_ENABLED = True
DEBUG = True
# настройка БД

SQLALCHEMY_TRACK_MODIFICATIONS = True

# mail server settings
FLASK_MAIL_SUBJECT_PREFIX = 'FB'
FLASK_MAIL_SENDER = 'FB Admin <alekseyserzh88@gmail.com>'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'alekseyserzh88@gmail.com'
MAIL_PASSWORD = 'nemate8888'


# настройки пагинации
PER_PAGE = 10
PER_PAGE_COMMENT = 40
PER_PAGE_MESSAGE = 30
PER_PAGE_SUPPORT_COMMENT = 40


if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'mysql://root:nemate666@localhost:3306/flask_blog'
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']