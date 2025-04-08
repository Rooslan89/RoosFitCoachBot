from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import datetime
import os

API_TOKEN = os.getenv('BOT_TOKEN')  # Безопасно подтягиваем токен из переменной окружения
CHAT_ID = os.getenv('CHAT_ID')      # Тоже самое для ID

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

import json

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_user(user_id, data):
    users = load_users()
    users[str(user_id)] = data
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class RegisterState(StatesGroup):
    name = State()
    gender = State()
    height = State()
    weight = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id in users:
        user = users[user_id]
        await message.answer(
            f"Привет, {user['name']}! Рад тебя снова видеть 💪\n"
            f"Пол: {user['gender']}, Рост: {user['height']} см, Вес: {user['weight']} кг"
        )
        await ask_mood(message)  # Переходим сразу к самочувствию
    else:
        await message.answer("Привет! Я твой фитнес-бот RoosFitCoach 💪\nПеред началом тренировок давай познакомимся.")
        await message.answer("Как тебя зовут?")
        await RegisterState.name.set()

@dp.message_handler(state=RegisterState.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Какой у тебя пол?", reply_markup=gender_kb)
    await RegisterState.gender.set()

@dp.message_handler(state=RegisterState.gender)
async def process_gender(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await message.answer("Укажи свой рост (в см):", reply_markup=types.ReplyKeyboardRemove())
    await RegisterState.height.set()

@dp.message_handler(state=RegisterState.height)
async def process_height(message: types.Message, state: FSMContext):
    await state.update_data(height=message.text)
    await message.answer("А теперь укажи свой вес (в кг):")
    await RegisterState.weight.set()

@dp.message_handler(state=RegisterState.weight)
async def process_weight(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = str(message.from_user.id)
    user_data = {
        "name": data['name'],
        "gender": data['gender'],
        "height": data['height'],
        "weight": data['weight']
    }
    save_user(user_id, user_data)

    await message.answer(
        f"Спасибо, {data['name']}!\n"
        f"Пол: {data['gender']}, Рост: {data['height']} см, Вес: {data['weight']} кг\n\n"
        "Теперь давай оценим твоё самочувствие 💬",
        reply_markup=mood_kb
    )
    await state.finish()





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
    if CHAT_ID:
        await bot.send_message(chat_id=CHAT_ID, text="Привет, Roos! Завтра тренировка 💪 Не забудь подготовиться! 🥗😴")

# Команда старт
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Привет, Roos! Я твой фитнес-бот RoosFitCoach 💪 Готов начать тренировку?", reply_markup=start_kb)

# Обработка кнопки "Начать тренировку"
@dp.message_handler(lambda message: message.text == "Начать тренировку")
async def ask_mood(message: types.Message):
    await message.answer("Как ты себя сегодня чувствуешь, Roos?", reply_markup=mood_kb)

@dp.message_handler(lambda message: message.text in ["Отлично 💯", "Нормально 😊", "Так себе 😕", "Плохо 😞"])
async def mood_response(message: types.Message):
    mood = message.text
    if mood == "Плохо 😞":
        await message.answer("Понял тебя, давай сегодня отдохнём. Завтра будет лучше! 🧘")
    elif mood == "Так себе 😕":
        await message.answer("Хорошо, я подберу адаптированную версию тренировки. 💡", reply_markup=training_kb)
    else:
        await message.answer("Отлично! Сейчас покажу, что у нас по плану 🔥", reply_markup=training_kb)

@dp.message_handler(lambda message: message.text == "Всё понял, поехали! 🔥")
async def start_training(message: types.Message):
    await message.answer(
        "Сегодняшняя тренировка (Full Body)\n\n"
        "1. Приседания — https://youtu.be/aclHkVaku9U\n"
        "2. Жим гантелей сидя — https://youtu.be/qEwKCR5JCog\n"
        "3. Становая тяга — https://youtu.be/ytGaGIn3SjE\n"
        "4. Подъём на бицепс — https://youtu.be/ykJmrZ5v0Oo\n"
        "5. Планка 60 сек — https://youtu.be/pSHjTRCQxIw\n\n"
        "Поехали! 🏋️"
    )

# Планировщик уведомлений
scheduler.add_job(send_reminder, 'cron', hour=21, minute=0)

# Хук на запуск
async def on_startup(dispatcher):
    scheduler.start()
    print("RoosFitCoach запущен! 💪")

# Хук на завершение
async def on_shutdown(dispatcher):
    await bot.session.close()
    print("RoosFitCoach завершает работу. Сессия закрыта.")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
