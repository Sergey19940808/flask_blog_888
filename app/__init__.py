# coding: utf-8
# импорты
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# инициализация приложений
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'login'
lm.login_message = 'Пожалуйста введите свои данные для входа на сайт, либо зарегистрируйтесь'
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
mail = Mail(app)
bcrypt = Bcrypt(app)





# import app
from app import views, models