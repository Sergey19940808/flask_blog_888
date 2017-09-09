# импорты
from datetime import datetime

from flask import render_template, redirect, flash, g, url_for, abort
from flask_login import login_user, logout_user, current_user, login_required
from itsdangerous import URLSafeTimedSerializer

from app import app, lm, db, bcrypt
from app.mailing import send_confirmation_email, send_password_reset_email
from config import SECRET_KEY, PER_PAGE
from .forms import LoginForm, RegisterForm, EmailForm, PasswordForm, \
    MessageSupportForm, AddCommentSupportForm, EditForm, EntryForm, CommentForm
from app.models import User, Support, CommentSupport, Entry, CommentEntry
from app.pagination import pagination_index, pagination_message_support, \
    pagination_support_comment, pagination_comment_entry


# декоратор выполнения запросов в контексте макета приложения
@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.today()
        db.session.add(g.user)
        db.session.commit()


# вьюшка домашняя страница
@app.route('/')
@app.route('/index')
@login_required
def index():
    title = 'Домашняя'
    entry = pagination_index()  # функция пагинации стихов на главной странице, смотри файл pagination
    if g.user.email_confirmed == False:
        flash('Подтвердите свой email')
    return render_template('entry/index.html', title=title, entry=entry)


# вьюшка страницы входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    title = 'Войти'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.nickname == form.nickname.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
        return redirect(url_for('index'))
    return render_template('auth/login.html', title=title, form=form)


# вьюшка регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    title = 'Регистрация'
    form = RegisterForm()
    if form.validate_on_submit():
        user_add = User(nickname=form.nickname.data,
                        email=form.email.data, password=form.password.data)
        user_add.authenticated = True
        db.session.add(user_add)
        db.session.commit()
        login_user(user_add)
        send_confirmation_email(user_add.email)
        flash('Спасибо за регистрацию!  Пожалуйста подтвердите свой email нажав в письме на ссылку.', 'success')
        return redirect(url_for('unconfirmed'))
    return render_template('auth/register.html', title=title, form=form)


# вьюшка подтверждения email
@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(SECRET_KEY)
        email = confirm_serializer.loads(token, salt='email-confirmation-salt', max_age=3600)
    except:
        flash('Ссылка для подтверждения email устарела или неправильная', 'error')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=email).first()

    if user.email_confirmed:
        flash('Ваш аккаунт уже подтверждался. Введите логин и пароль', 'info')
        return redirect(url_for('logout'))
    else:
        user.email_confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('Большое спасибо за подтверждение email и активации своего аккаунта!')
    return redirect(url_for('index'))


# вьюшка для неподтвердивших свою почту
@app.route('/unconfirmed')
@login_required
def unconfirmed():
    title = 'Подтвердите email'
    user = User.query.filter_by(nickname=g.user.nickname).first_or_404()
    return render_template('email/email_unconfirmed.html', title=title, user=user)


# вьюшка повторной отправки письма
@app.route('/resend_confirmation')
@login_required
def resend_email_confirmation():
    try:
        send_confirmation_email(g.user.email)
        flash('Email отправлен для подтверждения вашего адреса электронной почты. '
              'Пожалуйста, проверьте свою электронную почту!', 'success')
    except:
        flash('Ошибка!  Невозможно отправить письмо, чтобы подтвердить ваш адрес электронной почты', 'error')

    return redirect(url_for('unconfirmed'))


# вьюшка для сброса пароля
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    title = 'Укажите свой адрес электронной почты'
    form = EmailForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first_or_404()
        except:
            flash('Неверный адрес электронной почты!', 'error')
            return render_template('password_reset_email.html', form=form)

        if user.email_confirmed:
            send_password_reset_email(user.email)
            flash('Проверьте свою электронную почту, вам пришло письмо для сброса пароля.', 'success')
        else:
            flash('Ваш адрес электронной почты должен быть подтвержден перед попыткой сброса пароля.', 'error')
        return redirect(url_for('login'))

    return render_template('email/password_reset_email.html', form=form, title=title)


# вьюшка для создания нового пароля
@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    title = 'Смена пароля'
    try:
        password_reset_serializer = URLSafeTimedSerializer(SECRET_KEY)
        email = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash('Ссылка для сброса пароля недействительна или устарела.', 'error')
        return redirect(url_for('login'))
    form = PasswordForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=email).first_or_404()
        except:
            flash('Неверный адрес электронной почты!', 'error')
            return redirect(url_for('login'))
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Ваш пароль успешно обновлён!', 'success')
        return redirect(url_for('login'))
    return render_template('email/reset_password_with_token.html', form=form, token=token, title=title)


# вьюшка изменения почты
@app.route('/email_change', methods=['GET', 'POST'])
@login_required
def user_email_change():
    title = 'Изменение почты'
    form = EmailForm()
    if form.validate_on_submit():
        user_check = User.query.filter_by(email=form.email.data).first()
        if user_check is None:
            user = g.user
            user.email = form.email.data
            user.email_confirmed = False
            user.email_confirmed_on = None
            db.session.add(user)
            db.session.commit()
            send_confirmation_email(user.email)
            flash('Ваша почта изменена!  Пожалуйста подтвердите новый адрес электронной почты '
                  '(ссылка отправлена Вам на почту).', 'success')
            return redirect(url_for('user'))
        else:
            flash('Простите, Ваш почта уже используется!', 'error')
    return render_template('email/email_change.html', form=form, title=title)


# вьюшка изменения пароля
@app.route('/password_change', methods=['GET', 'POST'])
@login_required
def user_password_change():
    title = 'Изменение пароля'
    form = PasswordForm()
    if form.validate_on_submit():
        user = g.user
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Ваш пароль обновлён!', 'success')
        return redirect(url_for('user', nickname=g.user.nickname))
    return render_template('user/password_change.html', form=form, title=title)


# вьюшки cодержит информацию о нас
@app.route('/our_about')
def our_about():
    title = 'О нас'
    return render_template('user/our_about.html', title=title)


# вьюшка содержит интрукции как стать автором
@app.route('/how_author')
def how_author():
    title = 'Как стать автором'
    return render_template('user/how_author.html', title=title)


# вьюшка содержит правила сайта
@app.route('/how_author/info')
def how_author_info():
    title = 'Правила сайта'
    return render_template('user/info.html', title=title)


# вьюшка содержит контакты руководителя блога
@app.route('/contacts')
def contacts():
    title = 'Контакты'
    return render_template('user/contacts.html', title=title)


# вьюшка содержит страницу для помощи проекту в мат. плане
@app.route('/donate')
def donate():
    title = 'Помощь проекту'
    return render_template('user/donate.html', title=title)


# вьюшка содержит страницу технической поддержки проекта, форма для отправки
# вопросов и пожеланий и ответы Администратора
@app.route('/technical_support', methods=['GET', 'POST'])
@login_required
def technical_support():
    title = 'Служба поддержки'
    form = MessageSupportForm()
    if form.validate_on_submit():
        message_support_add = Support(body=form.body.data, pub_date=datetime.now(),
                                      author_support=g.user)
        db.session.add(message_support_add)
        db.session.commit()
        flash('Вы написали в службу поддержки')
        return redirect(url_for('technical_support'))
    message = pagination_message_support()  # функция пагинации сообщений на странице тех. поддержки, см. файл
    return render_template('user/technical_support.html', title=title, form=form,  # pagination
                           message=message)


# добавление комментариев к сообщениям в поддержку
@app.route('/comment_support/<int:id>', methods=['GET', 'POST'])
@login_required
def comment_support(id):
    title = 'Добавление комментария к сообщениям в поддержку'
    support = Support.query.get_or_404(id)
    form = AddCommentSupportForm()
    if form.validate_on_submit():
        add_comment_support = CommentSupport(body=form.body.data, pub_date=datetime.now(),
                                             author_support_comment=g.user, message_support_comment=support)
        db.session.add(add_comment_support)
        db.session.commit()
        flash('Вы прокомментировали сообщение')
        return redirect(url_for('comment_support', id=support.id))
    comment_support = pagination_support_comment(support=support)
    return render_template('entry/add_comment_support.html', title=title, support=support, form=form,
                           comment_support=comment_support)


# вьюшка своей страницы
@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    title = 'Ваша страница'
    user = User.query.filter_by(nickname=nickname).first_or_404()
    if user == None:
        flash('Пользователь ' + nickname + ' не найден.')
        return redirect(url_for('index'))
    entry = user.posts.paginate(page, PER_PAGE, False)
    return render_template('user/user.html', title=title, user=user, entry=entry)


# вьюшка удаления своего профиля
@app.route('/delete_user/<int:id>', methods=['GET', 'DELETE'])
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь удалён')
    return redirect(url_for('logout', ))


# вьюшка редактирования профиля
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    title = 'Редактирование информации о себе'
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Ваши изменения сохранены')
        return redirect(url_for('edit_profile'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('user/edit_profile.html', form=form, title=title)


# вьюшка добавления записи
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    title = 'Добавление стиха'
    form = EntryForm()
    if g.user and form.validate_on_submit():
        add_entry = Entry(title=form.title.data, text=form.text.data,
                          pub_date=datetime.now(), author_entry=g.user)
        db.session.add(add_entry)
        db.session.commit()
        flash('Вы добавили новый стих')
        return redirect(url_for('user', nickname=g.user.nickname))
    return render_template('entry/add_entry.html', title=title, form=form)


# вьюшка редактирования записи
@app.route('/edit_entry/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_entry(id):
    title = 'Редактирование стиха'
    entry = Entry.query.get_or_404(id)
    form = EntryForm()
    if form.validate_on_submit():
        entry.title = form.title.data
        entry.text = form.text.data
        entry.pub_date = datetime.today()
        db.session.add(entry)
        db.session.commit()
        flash('Ваш стих обновлён')
        return redirect(url_for('user', nickname=g.user.nickname))
    else:
        form.title.data = entry.title
        form.text.data = entry.text
    return render_template('entry/edit_entry.html', title=title, form=form)


# вьюшка удаления записи
@app.route('/delete_entry/<int:id>', methods=['GET', 'DELETE'])
@login_required
def delete_entry(id):
    entry = Entry.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    flash('Стих удалён')
    return redirect(url_for('user', nickname=g.user.nickname))


# вьюшка для показа отдельного стиха, и для добавления  комментариев
@app.route('/entry_comments/<int:id>/', methods=['GET', 'POST'])
@login_required
def entry_comments(id):
    title = 'Показать стих'
    entry = Entry.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment_add = CommentEntry(body=form.body.data, pub_date=datetime.now(),
                                   author_entry_comment=current_user, post_entry_comment=entry)
        db.session.add(comment_add)
        db.session.commit()
        flash('Вы добавили свой комментарий')
        return redirect(url_for('entry_comments', id=entry.id))
    comments = pagination_comment_entry(entry=entry)  # функция для выполенения паганации комментариев смотри файл
    # pagination
    return render_template('entry/entry_comments.html', title=title, entry=entry,
                           form=form, comment=comments)


# вьюшка админа для показа пользователей
@app.route('/admin_view_users')
@login_required
def admin_view_users():
    title = 'Администратор'
    if current_user.role != 'user':
        abort(403)
    else:
        users = User.query.order_by(User.id).all()
        return render_template('auth/admin_view_users.html', users=users, title=title)


# вьюшка выхода из своего профиля
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# декораторы обработчиков ошибок 401, 403, 500
@app.errorhandler(401)
def page_not_found(error):
    title = 401
    return render_template('layout/401.html', title=title), 401


@app.errorhandler(404)
def not_found_error(error):
    title = 404
    return render_template('layout/404.html', title=title), 404


@app.errorhandler(500)
def internal_error(error):
    title = 500
    db.session.rollback()
    return render_template('layout/500.html', title=title), 500


# декоратор загрузчика пользователя
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
