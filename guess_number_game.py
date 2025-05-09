from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import ContentType
from aiogram import F
from random import randint
import config

# Вместо BOT TOKEN HERE нужно вставить токен вашего бота, полученный у @BotFather
BOT_TOKEN = config.BOT_TOKEN

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Кол-во попыток
ATTEMPTS = 7
# пустой словарь для добавления новых пользователей и информации об игре
users = {}


# Случайное число
def get_random_number() -> int:
    return randint(1, 100)


async def go_to_start(message: Message):
    if message.from_user.id not in users:
        return await message.answer("Начни работу с ботом с команды /start")


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    keyboard = [
        [
            types.KeyboardButton(text="/help"),
            types.KeyboardButton(text="/stat"),
            types.KeyboardButton(text="/cancel"),
        ]
    ]
    reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    await message.answer(f'Привет,{message.from_user.first_name}!\nДавай сыграем в игру "Угадай число"!\nНапиши "Да", если хочешь сыграть или "Нет", если не хочешь. \nПодробные правила можно прочитать в справке /help', reply_markup=reply_markup)  # type: ignore

    if message.from_user.id not in users:
        users[message.from_user.id] = {
            "in_game": False,
            "secret_number": None,
            "attempts": None,
            "total_games": 0,
            "wins": 0,
        }


# Хендлер для обработки команды "/help"
@dp.message(Command(commands=["help"]))
async def process_help_command(message: Message):
    await message.answer(
        f"1. Бот загадывает число от 1 до 100 и предлагает Вам угадать его.\n"
        f"2. У Вас есть {ATTEMPTS} попыток, чтобы угадать число.\n"
        "3. Для получения статистики игр напишите команду /stat.\n"
        "4. Для выхода из игры напишите команду /cancel"
    )


# Этот хэндлер будет срабатывать на команду /cancel
@dp.message(Command(commands=["cancel"]))
async def process_cancel_command(message: Message):
    await go_to_start(message)
    if users[message.from_user.id]["in_game"]:
        users[message.from_user.id]["in_game"] = False
        await message.answer(
            'Вы вышли из игры. Если захотите сыграть снова - напишите "Да".'
        )
    else:
        await message.answer(
            'А мы и так не играем. Если хотите сыграть - напишите "Да".'
        )


# Этот хэндлер будет срабатывать на команду /stat
@dp.message(Command(commands=["stat"]))
async def process_stat_command(message: Message):
    await message.answer(
        f"Всего сыграно {users[message.from_user.id]['total_games']} игр.\nИз них выиграно {users[message.from_user.id]['wins']} игр."
    )
    await go_to_start(message)


# Этот хэндлер будет срабатывать на ответ "Да"
@dp.message(F.text.lower() == "да")
async def yes_answer(message: Message):
    await go_to_start(message)
    if not users[message.from_user.id]["in_game"]:
        users[message.from_user.id]["in_game"] = True
        users[message.from_user.id]["secret_number"] = get_random_number()
        users[message.from_user.id]["attempts"] = ATTEMPTS
        await message.answer(
            "Отлично. Я уже загадал число от 1 до 100. Попробуй отгадай."
        )
    else:
        await message.answer(
            "Пока мы играем я реагирую только на числа от 1 до 100 и команды '/cancel' и '/stat'"
        )


# Этот хэндлер будет срабатывать на ответ "Нет"
@dp.message(F.text.lower() == "нет")
async def no_answer(message: Message):
    await go_to_start(message)
    if not users[message.from_user.id]["in_game"]:
        await message.answer(
            'Жаль :(\n\nЕсли захотите поиграть - просто напишите "Да".'
        )
    else:
        await message.answer(
            "Мы же сейчас с вами играем. Присылайте, " "пожалуйста, числа от 1 до 100"
        )


# Этот хэндлер будет срабатывать на числа от 1 до 100
@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def number_answer(message: Message):
    await go_to_start(message)
    if users[message.from_user.id]["in_game"]:
        if int(message.text) == users[message.from_user.id]["secret_number"]:  # type: ignore
            users[message.from_user.id]["in_game"] = False
            users[message.from_user.id]["total_games"] += 1
            users[message.from_user.id]["wins"] += 1
            await message.answer(
                f"Правильно. Загаданное число было {users[message.from_user.id]['secret_number']}! \nСыграем ещё? Напиши 'Да', если хочешь сыграть."
            )
        elif int(message.text) > users[message.from_user.id]["secret_number"]:  # type: ignore
            users[message.from_user.id]["attempts"] -= 1
            await message.answer(
                f"Неправильно. Моё число меньше.\nОсталось {users[message.from_user.id]['attempts']} попыток."
            )
        elif int(message.text) < users[message.from_user.id]["secret_number"]:  # type: ignore
            users[message.from_user.id]["attempts"] -= 1
            await message.answer(
                f"Неправильно. Моё число больше.\nОсталось {users[message.from_user.id]['attempts']} попыток."
            )

        if users[message.from_user.id]["attempts"] == 0:
            users[message.from_user.id]["in_game"] = False
            users[message.from_user.id]["total_games"] += 1
            await message.answer(
                f'Попыток больше не осталось.\nУвы, но вы проиграли.\nЗагаданное число было {users[message.from_user.id]['secret_number']}.\nЕсли хотите сыграть ещё раз - напишите "Да".'
            )
    else:
        await message.answer('Мы ещё не начали игру! Хотите начать - напишите "Да".')


# Этот хэндлер будет срабатывать на любые другие сообщения
@dp.message()
async def process_other_answers(message: Message):
    await go_to_start(message)
    if users[message.from_user.id]["in_game"]:
        await message.answer(
            "Мы же сейчас с вами играем. " "Присылайте, пожалуйста, числа от 1 до 100"
        )
    else:
        await message.answer(
            "Я довольно ограниченный бот, давайте "
            'просто сыграем в игру?\nНапишите "Да", если хотите начать.'
        )


if __name__ == "__main__":
    dp.run_polling(bot)
