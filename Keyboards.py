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
    inkb.add(InlineKeyboardButton(text="Крестики-нолики", callback_data=f'tic_tac_toe-{fr}'))
    inkb.add(InlineKeyboardButton(text="Выгнать из друзей", callback_data=f'kick-{fr}'))
    return inkb


def tic_tac_toe_kb(user_id):
    inkb = InlineKeyboardMarkup()
    inkb.add(InlineKeyboardButton(text=f"Принять", callback_data=f'tic_response-true-{user_id}'))
    inkb.add(InlineKeyboardButton(text=f"Отказать", callback_data=f'tic_response-false-{user_id}'))
    return inkb


def tic_tac_toe_board(list, game_id):
    l = ["-", "0", "+"]
    inkb = InlineKeyboardMarkup(row_width=1)
    for i in range(3):
        kb1 = InlineKeyboardButton(text=l[list[i][0]], callback_data=f"tic_game-{game_id}-{i}-{0}")
        kb2 = InlineKeyboardButton(text=l[list[i][1]], callback_data=f"tic_game-{game_id}-{i}-{1}")
        kb3 = InlineKeyboardButton(text=l[list[i][2]], callback_data=f"tic_game-{game_id}-{i}-{2}")
        inkb.row(kb1, kb2, kb3)
    return inkb


def check(board):
    for i in board:
        if i[0] == i[1] == i[2] != 0:
            return i[0]
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i] != 0:
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] != 0:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != 0:
        return board[0][2]
    if 0 not in board[0] and 0 not in board[1] and 0 not in board[2]:
        return -1
    return False


def exit_kb():
    inkb = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(text="Выход", callback_data="exit")
    inkb.add(btn1)
    return inkb


