# импорты
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms import ValidationError
from wtforms.widgets import TextArea
from wtforms.validators import Length, DataRequired, Regexp, EqualTo, \
    Email

from .models import User


# классы веб-форм входа
class LoginForm(FlaskForm):
    nickname = StringField('Введите свой логин',
                           validators=[Length(min=0, max=20, message='Максимальная длина 20 символов'),
                                       DataRequired('Пожалуйста введите свой ник')])
    password = PasswordField('Введите свой пароль',
                           validators=[Length(min=0, max=20, message='Максимальная длина 20 символов'),
                                       DataRequired('Пожалуйста введите свой пароль')])

# класс веб-формы регистрации
class RegisterForm(FlaskForm):
    nickname = StringField('Новый никнейм', validators=[Length(min=6, max=20, message='Максимальная длина 20 символов'),
                                                        DataRequired('Это поле не должно быть пустым')])
    email = StringField('Новый адрес почты',
                        validators=[Length(min=10, max=30, message='Максимальная длина 30 символов'),
                                    DataRequired('Это поле не должно быть пустым'), Regexp(r'^[A-Za-z0-9_@.!?]{12,24}$',
                                                                                           message='Email содержит не допустимые символы')])
    password = PasswordField('Новый пароль',
                             validators=[Length(min=6, max=18, message='Максимальная длина 18 символов'),
                                         Regexp(r'^[A-Za-z0-9_]{6,18}$',
                                                message='Пароль содержит недопустимые символы'),
                                         DataRequired('Это поле не должно быть пустым'),
                                         EqualTo('confirm', message='Пароли должны совпадать')])
    confirm = PasswordField('Повторите пароль')

    # методы проверки полей
    def validate_nickname(self, field):
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError('Такой ник уже зарегистрирован')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Такая почта уже зарегистрирована')

    def validate_password(self, field):
        if User.query.filter_by(password=field.data).first():
            raise ValidationError('Такой пароль уже существует')



# класс веб-формы для сброса пароля
class EmailForm(FlaskForm):
    email = StringField('Емайл', validators=[DataRequired(), Email(), Length(min=6, max=40)])

# класс веб-формы для ввода нового пароля
class PasswordForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])


from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired, Length




# класс веб-формы коментариев
class CommentForm(FlaskForm):
    body = TextAreaField('Оставьте сообщение, совет: переводите каждую строчку не доходя до краёв формы',
                         validators=[DataRequired('Это поле не должно быть пустым'), Length(min=1, max=5000)])



# класс веб-формы записи(стиха)
class EntryForm(FlaskForm):
    title = StringField('Имя стиха', validators=[DataRequired('Это поле не должно быть пустым')])
    text = TextAreaField('Текст стиха', widget=TextArea(), validators=[Length(min=0, max=5000,
                          message='Максимальная длина 5000 символов'), DataRequired('Это поле не должно быть пустым')])



# класс веб-формы отправка сообщений на странице технической поддержки
class MessageSupportForm(FlaskForm):
    body = TextAreaField('Введите своё сообщение', validators=[DataRequired('Это поле не должно быть'),
                                                               Length(min=1, max=5000)])


# класс веб-формы для комментирование сообщений в службу поддержки
class AddCommentSupportForm(FlaskForm):
    body = TextAreaField('Оставьте комментарий к сообщению', validators=[DataRequired('Это поле не должно быть пустым'),
                                                                        Length(min=1, max=5000, message='нельзя превышать '
                                                                        'лимит символов 5000')])



# класс веб-формы редактирования профиля
class EditForm(FlaskForm):
    nickname = StringField('Никнейм', validators=[Length(min=0, max=20, message='Максимальная длина 20 символов'),
                                                  DataRequired('Это поле не должно быть пустым')])
    about_me = TextAreaField('Информация обо мне',
                             validators=[Length(min=0, max=140, message='Максимальная длина 140 символов')])

    # методы конструктора и проверки полей
    def __init__(self, original_nickname, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        if self.nickname.data == self.original_nickname:
            return True

        user = User.query.filter_by(nickname=self.nickname.data).first()

        if user != None:
            self.nickname.errors.append('Этот ник существует. Пожалуйста придумайте другой.')
            return False
        else:
            return True