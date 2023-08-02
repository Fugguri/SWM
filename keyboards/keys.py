from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def inline():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="", callback_data=""))
    return kb


def keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text=""))
    return kb


def start():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        text="Добавить бота", callback_data="Добавить бота"))
    kb.add(InlineKeyboardButton(text="Редактировать бота",
           callback_data="Редактировать бота"))
    kb.add(InlineKeyboardButton(text="Запуск бота",
           callback_data="Запуск бота"))
    kb.add(InlineKeyboardButton(text="Статистика",
           callback_data="Собрать статистику"))
    kb.add(InlineKeyboardButton(text="Информация", callback_data="Информация"))
    kb.add(InlineKeyboardButton(text="Пообщаться с ботом",
           callback_data="Пообщаться с ботом"))
    kb.add(InlineKeyboardButton(text="Оплата", callback_data="Оплата"))

    return kb


def back():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="Назад", callback_data="back"))
    return kb
