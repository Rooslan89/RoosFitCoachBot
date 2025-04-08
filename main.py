
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import datetime
import asyncio

API_TOKEN = '7966092558:AAEOocrIi0BXVVYQx2h-6IrwZOw7bZTeSZ4'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Главное меню
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("🏋 Тренировка"), KeyboardButton("📊 Прогресс"))
main_kb.add(KeyboardButton("📸 Фото/Вес"), KeyboardButton("🛌 Сон"))
main_kb.add(KeyboardButton("🍽 Питание"))

# День недели
def get_today_workout():
    day = datetime.datetime.today().weekday()
    workouts = {
        0: "Тренировка 1 – Ноги + дельты + пресс",
        1: "Тренировка 2 – Спина + руки",
        3: "Тренировка 3 – Ноги + ягодицы + дельты",
        4: "Тренировка 4 – Грудь + руки + кора"
    }
    return workouts.get(day, "Сегодня нет тренировки — восстановление 🧘")

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет, я RoosFitCoach 🤖 Готов к тренировке?", reply_markup=main_kb)

@dp.message_handler(lambda message: message.text == "🏋 Тренировка")
async def show_workout(message: types.Message):
    workout = get_today_workout()
    await message.reply(f"📅 {workout}

Напиши 'подробнее', чтобы увидеть упражнения.")

@dp.message_handler(lambda message: message.text.lower() == "подробнее")
async def send_workout_detail(message: types.Message):
    await message.reply("Пример упражнений:
1. Жим ногами
2. Сгибание ног
3. Выпады
(и т.д.)

📹 Видео скоро будут добавлены.")

@dp.message_handler(lambda message: message.text == "📸 Фото/Вес")
async def input_photo_weight(message: types.Message):
    await message.reply("Пришли мне своё фото или напиши вес (в кг):")

@dp.message_handler(lambda message: message.text == "🛌 Сон")
async def input_sleep(message: types.Message):
    await message.reply("Сколько часов ты спал сегодня?")

@dp.message_handler(lambda message: message.text == "📊 Прогресс")
async def progress(message: types.Message):
    await message.reply("📈 Отслеживание прогресса будет здесь. Скоро добавим графики и данные.")

@dp.message_handler(lambda message: message.text == "🍽 Питание")
async def nutrition(message: types.Message):
    await message.reply("🍎 Сегодняшний совет по питанию:
– Больше белка на завтрак
– Не пропускай приём пищи после тренировки")

# Запуск
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
