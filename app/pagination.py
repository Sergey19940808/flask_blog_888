# импорты
from flask import request
from config import PER_PAGE, PER_PAGE_MESSAGE, PER_PAGE_COMMENT
from .models import Entry, Support, CommentEntry, CommentSupport

# функция пагинации домашней страницы
def pagination_index():
    page = request.args.get('page', 1, type=int)
    entry = Entry.query.order_by(Entry.pub_date.desc()).paginate(
        page, per_page=PER_PAGE, error_out=False)
    return entry

# функция паганация комментариев
def pagination_comment_entry(entry):
    page = request.args.get('page', 1, type=int)
    comments = entry.entry_comment.order_by(CommentEntry.pub_date.desc()).paginate(
        page, per_page=PER_PAGE_COMMENT, error_out=False)
    return comments


# функция пагинация страницы тех. поддержки проекта
def pagination_message_support():
    page = request.args.get('page', 1, type=int)
    message = Support.query.order_by(Support.pub_date.desc()).paginate(
            page, per_page=PER_PAGE_MESSAGE, error_out=False)
    return message


def pagination_support_comment(support):
    comment_support = support.support_comment.order_by(CommentSupport.pub_date.desc())
    return comment_support

