from db import Databases
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from States import *
from Keyboards import *
from cfg import token
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


db = Databases("users.db")
storage = MemoryStorage()
bot = Bot(token)
dp = Dispatcher(bot, storage=storage)


tic_tac_toe = {}


@dp.message_handler(commands=["отмена"], state="*")
@dp.message_handler(Text(equals="отмена", ignore_case=True), state="*")
async def stop(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()


@dp.message_handler(commands=['friends'], state=None)
async def get_friends(message: types.Message):
    if db.id_exists(message.from_user.id):
        friends = db.get_friends(message.from_user.id)
        if "," in (friends[0][0]):
            await bot.send_message(message.from_user.id, "Ваши друзья:",
                                   reply_markup=show_friends(friends[0][0].split(',')[1:]))
        else:
            await bot.send_message(message.from_user.id, "У вас нет друзей")
    else:
        await bot.send_message(message.from_user.id, "Вы не зарегестрированы")


@dp.message_handler(commands=['register'], state=None)
async def register(message: types.Message):
    if db.id_exists(message.from_user.id):
        await bot.send_message(message.from_user.id, "Вы уже зарегестрированы")
    else:
        await bot.send_message(message.from_user.id, "Введите ник")
        await Reg.nickname.set()


@dp.message_handler(state=Reg.nickname)
async def nickname(message: types.Message, state: FSMContext):
    if not db.user_exists(message.text):
        db.add_user(message.from_user.id, message.text)
        await bot.send_message(message.from_user.id, "Готово")
        await state.finish()
    else:
        await bot.send_message(message.from_user.id, "Данный ник уже занят")


@dp.message_handler(commands=['add'], state=None)
async def add(message: types.Message):
    await bot.send_message(message.from_user.id, "Введите ник")
    await Add_friends.nickname.set()


@dp.message_handler(state=Add_friends.nickname)
async def nickname(message: types.Message, state: FSMContext):
    if db.user_exists(message.text):
        user_id = db.get_user_id(message.text)[0][0]
        if user_id != message.from_user.id:
            if str(user_id) in db.get_friends(message.from_user.id)[0][0].split(',')[1:]:
                await bot.send_message(message.from_user.id, "Пользователь уже у вас в друзьях")
            else:
                await bot.send_message(user_id, f"Запрос в друзья от {db.get_nickname(message.from_user.id)[0][0]}",
                                       reply_markup=friend_request(message.from_user.id))
                await bot.send_message(message.from_user.id, "Запрос отправлен")
                await state.finish()
        else:
            await bot.send_message(message.from_user.id, "Вы не можете отправить запрос сами себе")
    else:
        await bot.send_message(message.from_user.id, "Пользователь не найден")


@dp.callback_query_handler(Text(startswith="response"))
async def response(callback: types.CallbackQuery):
    name = db.get_nickname(callback.from_user.id)
    if callback.data.split('-')[1] == "true":
        db.add_friend(callback.from_user.id, callback.data.split('-')[2])
        await callback.answer("Запрос принят")
        await bot.send_message(int(callback.data.split('-')[2]), f'{name[0][0]} принял(а) ваш запрос')
    else:
        await callback.answer("Запрос откланен")
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)


@dp.callback_query_handler(Text(startswith="friend"))
async def fr(callback: types.CallbackQuery):
    name = db.get_nickname(callback.data.split('-')[1])[0][0]
    await callback.answer(name)
    await bot.send_message(callback.from_user.id, name,
                           reply_markup=friend(callback.data.split('-')[1]))
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)


@dp.callback_query_handler(Text(startswith="kick"))
async def duel(callback: types.CallbackQuery):
    db.kick_friend(callback.from_user.id, callback.data.split('-')[1])
    await callback.answer("Друг удален")
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)


@dp.callback_query_handler(Text(startswith="tic_tac_toe"))
async def tic(callback: types.CallbackQuery, state: FSMContext):
    status1 = db.get_status(callback.from_user.id)
    status2 = db.get_status(int(callback.data.split('-')[1]))
    if status1 != "Game" and status2 != "Game":
        db.edit_status(callback.from_user.id, "Game")
        await Tic_tac_toe.game.set()
        tic_tac_toe[str(callback.from_user.id)] = {"status": "wait", "players": [callback.from_user.id],
                                                  "board": [[0, 0, 0] for i in range(3)], "move": 0, "msg_id": [1, 1]}
        await bot.send_message(int(callback.data.split('-')[1]), f"Вызов в крестики-нолики от {db.get_nickname(callback.from_user.id)[0][0]}",
                               reply_markup=tic_tac_toe_kb(callback.from_user.id))
        async with state.proxy() as data:
            data["game"] = str(callback.from_user.id)
    else:
        await bot.send_message(callback.from_user.id, "Игрок уже в игре")
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)


@dp.callback_query_handler(Text(startswith="tic_response"))
async def rsp(callback: types.CallbackQuery, state: FSMContext):
    if callback.data.split('-')[1] == "true":
        status1 = db.get_status(callback.from_user.id)
        if status1 != "Game":
            db.edit_status(callback.from_user.id, "Game")
            await Tic_tac_toe.game.set()
            tic_tac_toe[callback.data.split('-')[2]]["status"] = "game"
            x = tic_tac_toe[callback.data.split('-')[2]]["players"]
            x.append(callback.from_user.id)
            tic_tac_toe[callback.data.split('-')[2]]["players"] = x
            msg1 = await bot.send_message(tic_tac_toe[callback.data.split('-')[2]]["players"][0], "Игра началась",
                                          reply_markup=tic_tac_toe_board(tic_tac_toe[callback.data.split('-')[2]]["board"],
                                                                  callback.data.split('-')[2]))
            msg2 = await bot.send_message(callback.from_user.id, "Игра началась",
                                          reply_markup=tic_tac_toe_board(tic_tac_toe[callback.data.split('-')[2]]["board"],
                                                                  callback.data.split('-')[2]))
            tic_tac_toe[callback.data.split('-')[2]]["msg_id"] = [msg1.message_id, msg2.message_id]
            await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
            async with state.proxy() as data:
                data["game"] = str([callback.data.split('-')[1]])


@dp.callback_query_handler(Text(startswith="tic_game"), state=Tic_tac_toe.game)
async def response(callback: types.CallbackQuery, state: FSMContext):
    move = tic_tac_toe[callback.data.split('-')[1]]["move"]
    if tic_tac_toe[callback.data.split('-')[1]]["players"][move] == callback.from_user.id:
        x = int(callback.data.split('-')[2])
        y = int(callback.data.split('-')[3])
        if tic_tac_toe[callback.data.split('-')[1]]["board"][x][y] == 0:
            tic_tac_toe[callback.data.split('-')[1]]["board"][x][y] = move + 1
            tic_tac_toe[callback.data.split('-')[1]]["move"] = (move + 1) % 2
            t = check(tic_tac_toe[callback.data.split('-')[1]]["board"])
            id1 = tic_tac_toe[callback.data.split('-')[1]]["players"][0]
            id2 = tic_tac_toe[callback.data.split('-')[1]]["players"][1]
            if not t:
                await bot.edit_message_text("Игра началась:", id1, tic_tac_toe[callback.data.split('-')[1]]["msg_id"][0],
                                            reply_markup=tic_tac_toe_board(tic_tac_toe[callback.data.split('-')[1]]["board"], id1))
                await bot.edit_message_text("Игра началась:", id2, tic_tac_toe[callback.data.split('-')[1]]["msg_id"][1],
                                            reply_markup=tic_tac_toe_board(tic_tac_toe[callback.data.split('-')[1]]["board"], id1))
            else:
                kb = exit_kb()
                if t == -1:
                    await bot.edit_message_text(f"Игра окончена, ничья", id1,
                                                tic_tac_toe[callback.data.split('-')[1]]["msg_id"][0], reply_markup=kb)
                    await bot.edit_message_text(f"Игра окончена, ничья", id2,
                                                tic_tac_toe[callback.data.split('-')[1]]["msg_id"][1], reply_markup=kb)
                else:
                    print(t)
                    winner = db.get_nickname([id1, id2][t - 1])[0][0]
                    await bot.edit_message_text(f"Игра окончена, победитель: {winner}", id1, tic_tac_toe[callback.data.split('-')[1]]["msg_id"][0], reply_markup=kb)
                    await bot.edit_message_text(f"Игра окончена, победитель: {winner}", id2, tic_tac_toe[callback.data.split('-')[1]]["msg_id"][1], reply_markup=kb)
        else:
            await callback.answer("Вы не можете ходить сюда")
    else:
        await callback.answer("Сейчас не ваш ход")


@dp.callback_query_handler(Text(startswith="exit"), state=Tic_tac_toe.game)
async def exit(callback: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    db.edit_status(callback.from_user.id, "None")
    await state.finish()

executor.start_polling(dp, skip_updates=True)
