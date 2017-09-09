# импорты
import hashlib
from datetime import datetime
from flask_login import UserMixin
from app import db, bcrypt


# Модель пользователей
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(100), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    posts = db.relationship('Entry', backref='users', lazy='dynamic', passive_deletes=True)  # ссылка на др. таблицу!!!
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime())
    avatar_hash = db.Column(db.String(32))
    authenticated = db.Column(db.Boolean, default=False)
    email_confirmed = db.Column(db.Boolean, nullable=True, default=False)
    comment_entry = db.relationship('CommentEntry', backref='comment_user', lazy='dynamic', passive_deletes=True) # связь пользователей и комментов
    comment_support = db.relationship('CommentSupport', backref='comment_support', lazy='dynamic')
    support = db.relationship('Support', backref='support', lazy='dynamic', passive_deletes=True) # связь сообщений в поддержку и пользователей
    role = db.Column(db.String(30), default='user')


    # метод-контсруктор
    def __init__(self, nickname, email, password, about_me=None, role='user'):
        self.nickname = nickname
        self.email = email
        self.about_me = about_me
        self.set_password(password)
        self.email_confirmed = False
        self.authenticated = False
        self.role = role

        # условие метода
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    # метод изменения хэша аватара email
    def change_email(self, new_email):
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    # загрузка аватара
    def avatar(self, size=100, default='wavatar', rating='g'):
        url = 'http://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url,
                                                                     hash=hash, size=size, default=default,
                                                                     rating=rating)

    # метод хэширования пароля
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    # метод получения пароля
    def check_password(self, password):
        if bcrypt.check_password_hash(self.password, password):
            return True


# модель стихов (записей)
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    text = db.Column(db.Text)
    pub_date = db.Column(db.DateTime, default=datetime.now())
    author_entry = db.relationship('User')  # cсылка на идентификацию пользователя во время создания стиха
    user_entry_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    entry_comment = db.relationship('CommentEntry', backref='entry_comment', lazy='dynamic', passive_deletes=True)


    # метод-контсруктор
    def __init__(self, title, text, pub_date, author_entry):
        self.title = title
        self.text = text
        self.pub_date = pub_date
        self.author_entry = author_entry


# модель комментариев стихов
class CommentEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime, default=datetime.now())
    writer_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')) # внешний ключ
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id')) # внешний ключ
    author_entry_comment = db.relationship('User')  # cсылка на идентификацию пользователя во время создания стиха
    post_entry_comment = db.relationship('Entry')  # ссылка комментария на определенный стих

    # метод-контсруктор
    def __init__(self, body, pub_date, author_entry_comment, post_entry_comment):

        self.body = body
        self.pub_date = pub_date
        self.author_entry_comment = author_entry_comment
        self.post_entry_comment = post_entry_comment


# модель технической поддержки
class Support(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime, default=datetime.now())
    author_support = db.relationship('User') # связь сообщения в поддержку с пользователем
    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')) # внешний ключ
    support_comment = db.relationship('CommentSupport', backref='support_comment', lazy='dynamic')

    # метод-контсруктор
    def __init__(self, body, pub_date, author_support):
        self.body = body
        self.pub_date = pub_date
        self.author_support = author_support


# модель комментариев сообщений в поддержку
class CommentSupport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime, default=datetime.now())
    support_comment_id = db.Column(db.Integer, db.ForeignKey('support.id'))  # внешний ключ
    user_comment_id = db.Column(db.Integer, db.ForeignKey('user.id')) # внешний ключ
    author_support_comment = db.relationship('User')
    message_support_comment = db.relationship('Support')


    # метод-конструктор
    def __init__(self, body, pub_date, author_support_comment, message_support_comment):
        self.body = body
        self.pub_date = pub_date
        self.author_support_comment = author_support_comment
        self.message_support_comment = message_support_comment
