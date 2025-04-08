
import asyncio
import datetime
import os
import sys
import logging

# aiogram использует aiohttp, импортируем сессии с отключением SSL
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not API_TOKEN or not CHAT_ID:
    logging.error("Переменные окружения BOT_TOKEN и CHAT_ID не заданы")
    sys.exit(1)

# Создаем aiohttp-сессию с отключённым SSL
try:
    connector = aiohttp.TCPConnector(ssl=False)
    session = aiohttp.ClientSession(connector=connector)
except Exception as e:
    logging.error(f"Ошибка создания aiohttp-сессии: {e}")
    sys.exit(1)

bot = Bot(token=API_TOKEN, session=session)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

# Клавиатуры
start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(KeyboardButton("Начать тренировку"))

mood_kb = ReplyKeyboardMarkup(resize_keyboard=True)
mood_kb.add("Отлично 💯", "Нормально 😊")
mood_kb.add("Так себе 😕", "Плохо 😞")

training_kb = ReplyKeyboardMarkup(resize_keyboard=True)
training_kb.add("Всё понял, поехали! 🔥")

# Напоминание
async def send_reminder():
    await bot.send_message(
        chat_id=CHAT_ID,
        text="Привет, Roos! Завтра тренировка 💪 Не забудь подготовиться! 🥗😴"
    )

# Обработка команд
@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    await message.reply(
        "Привет, Roos! Я твой фитнес-бот RoosFitCoach 💪 Готов начать тренировку?",
        reply_markup=start_kb
    )

@dp.message_handler(lambda message: message.text == "Начать тренировку")
async def handle_start_training(message: types.Message):
    await message.answer("Как ты себя сегодня чувствуешь, Roos?", reply_markup=mood_kb)

@dp.message_handler(lambda message: message.text in ["Отлично 💯", "Нормально 😊", "Так себе 😕", "Плохо 😞"])
async def handle_mood(message: types.Message):
    mood = message.text
    if mood == "Плохо 😞":
        await message.answer("Понял тебя, давай сегодня отдохнём. Завтра будет лучше! 🧘")
    elif mood == "Так себе 😕":
        await message.answer("Хорошо, я подберу адаптированную версию тренировки. 💡", reply_markup=training_kb)
    else:
        await message.answer("Отлично! Сейчас покажу, что у нас по плану 🔥", reply_markup=training_kb)

@dp.message_handler(lambda message: message.text == "Всё понял, поехали! 🔥")
async def handle_go_training(message: types.Message):
    await message.answer(
        "Сегодняшняя тренировка (Full Body)\n\n"
        "1. Приседания — https://youtu.be/aclHkVaku9U\n"
        "2. Жим гантелей сидя — https://youtu.be/qEwKCR5JCog\n"
        "3. Становая тяга — https://youtu.be/ytGaGIn3SjE\n"
        "4. Подъём на бицепс — https://youtu.be/ykJmrZ5v0Oo\n"
        "5. Планка 60 сек — https://youtu.be/pSHjTRCQxIw\n\n"
        "Поехали! 🏋️"
    )

# Планировщик
scheduler.add_job(send_reminder, 'cron', hour=21, minute=0)
scheduler.start()

# Запуск бота
if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True)
    finally:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(session.close())
