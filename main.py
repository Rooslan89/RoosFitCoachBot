from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import datetime
import os
import json

API_TOKEN = os.getenv('BOT_TOKEN')  # Безопасно подтягиваем токен из переменной окружения
CHAT_ID = os.getenv('CHAT_ID')      # Тоже самое для ID

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()


# Работа с JSON-файлом
USER_DATA_FILE = "users.json"

def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_user(user_id, user_data):
    users = load_users()
    users[str(user_id)] = user_data
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def user_exists(user_id):
    users = load_users()
    return str(user_id) in users

def get_user(user_id):
    users = load_users()
    return users.get(str(user_id), None)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id

    if user_exists(user_id):
        user = get_user(user_id)
        await message.answer(
            f"С возвращением, Roos! 💪\n\n"
            f"Твои данные:\n"
            f"Пол: {user['gender']}\n"
            f"Рост: {user['height']} см\n"
            f"Вес: {user['weight']} кг\n\n"
            f"Готов к тренировке?",
            reply_markup=start_kb
        )
    else:
        await message.answer("Привет, Roos! Я твой фитнес-бот RoosFitCoach 💪\n\nПеред началом тренировок, давай немного познакомимся.")
        await message.answer("Какой у тебя пол?", reply_markup=gender_kb)
        await RegisterState.gender.set()
4. 🧠 В process_weight — добавим сохранение:
python
Копировать
Редактировать
@dp.message_handler(state=RegisterState.weight)
async def process_weight(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    # Сохраняем пользователя в файл
    user_id = message.from_user.id
    save_user(user_id, {
        "gender": data['gender'],
        "height": data['height'],
        "weight": data['weight']
    })

    await message.answer(
        f"Отлично, Roos!\n"
        f"Пол: {data['gender']}\n"
        f"Рост: {data['height']} см\n"
        f"Вес: {data['weight']} кг\n\n"
        "Теперь давай оценим твоё самочувствие перед тренировкой 💬",
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
