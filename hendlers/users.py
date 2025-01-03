import asyncio
import datetime
from aiogram import F, types, Router
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bd import sql

router_user = Router()

class Waterbalanse(StatesGroup):
    Water = State()
    Weight = State()
    Age = State()
    Physical_activity = State()
    Sex = State()
    Climatic_conditions = State()

registered_user_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Ввести количество воды")],
        [KeyboardButton(text="Посмотреть прогресс")],
        [KeyboardButton(text="Обновить данные")],
        [KeyboardButton(text="Напоминание")]
    ],
    resize_keyboard=True
)

@router_user.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username

    user_created = await sql.get_or_create_user(user_id, username)

    if user_created:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='1000'),
                    KeyboardButton(text='2000'),
                    KeyboardButton(text='2500')
                ],
            ],
            resize_keyboard=True
        )
        await message.answer(
            "Привет! Я помогу тебе отслеживать водный баланс. Сколько ты выпил сегодня в миллилитрах (только цифры)?",
            reply_markup=keyboard
        )
        await state.set_state(Waterbalanse.Water)
    else:
        await message.answer(
            "Привет! Ты уже зарегистрирован в системе. Давай начнем отслеживание водного баланса.",
            reply_markup=registered_user_keyboard
        )

@router_user.message(Waterbalanse.Water)
async def Waterbalanse_Water(message: types.Message, state: FSMContext):
    try:
        water_amount = int(message.text)
        if water_amount <= 0:
            raise ValueError("Количество воды должно быть положительным числом.")
        await state.update_data(Water=water_amount)
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='70'),
                    KeyboardButton(text='50'),
                    KeyboardButton(text='60')
                ],
            ],
            resize_keyboard=True
        )
        await message.answer(
            f"Отлично! Сегодня ты уже выпил {water_amount} мл воды. Теперь введи свой вес (в килограммах), чтобы я мог рассчитать твою норму воды.",
            reply_markup=keyboard
        )
        await state.set_state(Waterbalanse.Weight)
    except ValueError:
        await message.answer(
            "Пожалуйста, введи корректное количество воды в миллилитрах (только цифры). Например: 200"
        )


@router_user.message(Waterbalanse.Weight)
async def Waterbalanse_Weight(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)
        if weight <= 0:
            raise ValueError("Вес должен быть положительным числом.")

        await state.update_data(Weight=weight)
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='20'),
                    KeyboardButton(text='30'),
                    KeyboardButton(text='40')
                ],
            ],
            resize_keyboard=True
        )
        await message.answer(
            f"Отлично! Ты указал свой вес: {weight} кг. Теперь введи свой возраст (в годах), чтобы я мог учесть это в расчёте нормы воды.",
            reply_markup=keyboard
        )
        await state.set_state(Waterbalanse.Age)
    except ValueError:
        await message.answer(
            "Пожалуйста, введи корректный вес в килограммах (только цифры). Например: 70"
        )


@router_user.message(Waterbalanse.Age)
async def Waterbalanse_Age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if age <= 0:
            raise ValueError("Возраст должен быть положительным числом.")
        await state.update_data(Age=age)
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='20'),
                    KeyboardButton(text='30'),
                    KeyboardButton(text='60')
                ],
            ],
            resize_keyboard=True
        )
        await message.answer(
            f"Ты указал возраст: {age} лет.\n\n"
            "Теперь укажи сколько ты занимаешься в день (в минутах)!", reply_markup=keyboard
        )
        await state.set_state(Waterbalanse.Physical_activity)
    except ValueError:
        await message.answer(
            "Пожалуйста, введи корректный возраст (только цифры). Например: 25"
        )


@router_user.message(Waterbalanse.Physical_activity)
async def Waterbalanse_Physical_activity(message: types.Message, state: FSMContext):
    try:
        physical_activity = int(message.text)
        if physical_activity < 0:
            raise ValueError("Физическая активность не может быть отрицательной.")
        await state.update_data(Physical_activity=physical_activity)
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='мужской'),
                    KeyboardButton(text='женский')
                ],
            ],
            resize_keyboard=True
        )
        await message.answer(
            f"Ты указал {physical_activity} минут физической активности в день. "
            "Теперь укажи, свой пол ('мужской' или 'женский).", reply_markup=keyboard
        )
        await state.set_state(Waterbalanse.Sex)
    except ValueError:
        await message.answer(
            "Пожалуйста, введи корректное значение физической активности (только цифры). Например: 60"
        )


@router_user.message(Waterbalanse.Sex)
async def Waterbalanse_Sex(message: types.Message, state: FSMContext):
    try:
        gender = message.text.strip().lower()
        if gender not in ["мужской", "женский"]:
            raise ValueError("Пол должен быть указан как 'мужской' или 'женский'.")
        await state.update_data(Sex=gender)
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='да'),
                    KeyboardButton(text='нет')
                ],
            ],
            resize_keyboard=True
        )
        await message.answer(
            f"Ты указал пол: {gender}.\n\n"
            "Теперь укажи, живёшь ли ты в жарком климате (да/нет).", reply_markup=keyboard
        )
        await state.set_state(Waterbalanse.Climatic_conditions)
    except ValueError:
        await message.answer(
            "Пожалуйста, введи 'мужской' или 'женский' для указания пола."
        )


@router_user.message(Waterbalanse.Climatic_conditions)
async def Waterbalanse_Climatic_conditions(message: types.Message, state: FSMContext):
    try:
        climatic_conditions = message.text.strip().lower()
        if climatic_conditions not in ["да", "нет"]:
            raise ValueError("Ответ должен быть 'да' или 'нет'.")


        await state.update_data(Climatic_conditions=climatic_conditions)

        user_data = await state.get_data()
        user_id = message.from_user.id
        weight = float(user_data.get('Weight', 0))
        age = int(user_data.get('Age', 0))  # Возраст
        physical_activity = int(user_data.get('Physical_activity', 0))
        sex = user_data.get('Sex', 'не указан')  # Пол
        water_drunk = float(user_data.get('Water', 0))


        daily_goal = weight * 30

        if age > 60:
            daily_goal *= 0.9

        if physical_activity > 30:
            daily_goal += (physical_activity // 30) * 300

        if climatic_conditions == "да":
            daily_goal *= 1.2

        if sex == "женский":
            daily_goal *= 0.9

        remaining_water = max(daily_goal - water_drunk, 0)

        await sql.update_user_water_data(
            user_id=user_id,
            weight=weight,
            age=age,
            physical_activity=physical_activity,
            sex=sex,
            climatic_conditions=climatic_conditions,
            water_drunk=water_drunk,
        )
        await message.answer(
            f"Твоя рекомендованная дневная норма воды составляет {daily_goal:.0f} мл.\n"
            f"Ты уже выпил {water_drunk:.0f} мл воды.\n"
            f"Тебе осталось выпить ещё {remaining_water:.0f} мл воды сегодня."
        )
        await state.clear()
    except ValueError:
        await message.answer(
            "Пожалуйста, введи 'да' или 'нет' в ответ на вопрос о климатических условиях."
        )

class Waterone(StatesGroup):
    Water = State()


@router_user.message(F.text == "Ввести количество воды")
async def enter_water_amount(message: types.Message, state: FSMContext):
    await message.answer("Сколько ты выпил сегодня в миллилитрах?")
    await state.set_state(Waterone.Water)


@router_user.message(Waterone.Water)
async def process_water_amount(message: types.Message, state: FSMContext):
    try:
        water_amount = int(message.text.strip())

        user_data = await sql.get_user_data(message.from_user.id)

        if not user_data:
            await message.answer("Упс, данные о тебе не найдены. Пожалуйста, начни регистрацию.")
            return


        weight = user_data['weight']
        age = user_data['age']
        physical_activity = user_data['physical_activity']
        sex = user_data['sex']
        climatic_conditions = user_data['climatic_conditions']

        # Базовая норма воды: 30 мл на килограмм веса
        daily_goal = weight * 30

        # Коррекция по возрасту (если возраст старше 60 лет, норма воды снижается)
        if age > 60:
            daily_goal *= 0.9  # Уменьшаем на 10%

        # Коррекция по физической активности: увеличиваем норму на 10% за каждые 30 минут активности
        if physical_activity > 30:
            daily_goal += (physical_activity // 30) * 300  # 300 мл за каждые 30 минут активности

        # Коррекция по климату: увеличиваем норму на 20% для жаркого климата
        if climatic_conditions == "да":
            daily_goal *= 1.2

        # Коррекция по полу: для женщин уменьшаем норму на 10%
        if sex == "женский":
            daily_goal *= 0.9

        # Вычисляем, сколько ещё воды нужно выпить
        remaining_water = max(daily_goal - water_amount, 0)

        await message.answer(
            f"Твоя рекомендованная дневная норма воды составляет {daily_goal:.0f} мл.\n"
            f"Ты уже выпил {water_amount:.0f} мл воды.\n"
            f"Тебе осталось выпить ещё {remaining_water:.0f} мл воды сегодня."
        )
        await state.clear()

    except ValueError:
        await message.answer("Пожалуйста, введите число для количества воды в миллилитрах.")

@router_user.message(F.text == "Посмотреть прогресс")
async def show_progress(message: types.Message):
    user_id = message.from_user.id
    progress = await sql.get_user_progress(user_id)
    await message.answer(progress)

@router_user.message(F.text == "Обновить данные")
async def update_data(message: types.Message, state: FSMContext):
    await message.answer("Давай обновим твои данные. Начнем с веса. Укажи свой вес в килограммах.")
    await state.set_state(Waterbalanse.Weight)


class Reminder(StatesGroup):
    reminder = State()

@router_user.message(F.text == "Напоминание")
async def reminder(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='да'),
                KeyboardButton(text='нет')
            ],
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Я могу напоминать тебе о питье воды каждые 3 часа.\nТы хочешь включить напоминания? Напиши 'да' или 'нет'.", reply_markup=keyboard
    )
    await state.set_state(Reminder.reminder)


reminder_task = None

@router_user.message(Reminder.reminder)
async def set_reminder(message: types.Message):
    global reminder_task
    response = message.text.strip().lower()

    if response == "да":
        if reminder_task is not None:
            await message.answer("Напоминания уже включены!")
            return

        await message.answer("Отлично! Я буду напоминать тебе о питье воды каждые 3 часа.")

        async def send_hourly_reminder():
            while True:
                current_hour = datetime.datetime.now().hour

                if 6 <= current_hour < 22:
                    await message.answer("Не забывай пить воду! 🥤")
                else:
                    await asyncio.sleep(10800)
                    continue
                await asyncio.sleep(10800)

        reminder_task = asyncio.create_task(send_hourly_reminder())

    elif response == "нет":
        if reminder_task is None:
            await message.answer("Напоминания уже отключены.")
        else:
            reminder_task.cancel()
            reminder_task = None
            await message.answer("Хорошо, напоминания не будут включены.")
    else:
        await message.answer("Пожалуйста, ответь 'да' или 'нет'.")
