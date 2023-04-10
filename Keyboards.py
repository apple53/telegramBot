from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from db import Databases


db = Databases("users.db")


def friend_request(user_id):
    inkbn = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text="Принять", callback_data=f"response-true-{user_id}")
    btn2 = InlineKeyboardButton(text="Отказать", callback_data=f"response-false-{user_id}")
    inkbn.add(btn1).add(btn2)
    return inkbn


def show_friends(friends):
    inkbn = InlineKeyboardMarkup()
    for i in friends:
        name = db.get_nickname(int(i))[0][0]
        inkbn.add(InlineKeyboardButton(text=name, callback_data=f'friend-{i}'))
    return inkbn


def friend(fr):
    inkb = InlineKeyboardMarkup()
    inkb.add(InlineKeyboardButton(text="Дуэль", callback_data=f'duel-{fr}'))
    inkb.add(InlineKeyboardButton(text="Выгнать из друзей", callback_data=f'kick-{fr}'))
    return inkb

