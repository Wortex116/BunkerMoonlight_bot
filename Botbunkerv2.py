import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# ТОКЕН ТВОЕГО БОТА (замени на реальный)
TOKEN = "YOUR_BOT_TOKEN_HERE"

# ЦЕЛЕВОЙ ЧАТ ДЛЯ ИГРЫ
TARGET_CHAT_ID = -1003839393171

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# ================= НАСТРОЙКИ ПО УМОЛЧАНИЮ =================
DEFAULT_SETTINGS = {
    "round_time": 120,  # секунд на раунд (2 минуты)
    "min_players": 2,
    "max_players": 20,
    "reg_time": 300,    # 5 минут на регистрацию (в секундах)
}

current_settings = DEFAULT_SETTINGS.copy()

# ================= БАЗЫ ДАННЫХ ДЛЯ ГЕНЕРАЦИИ КАРТ =================
PROFESSIONS = ["Инженер", "Психолог", "Врач-хирург", "Программист", "Агроном", "Электрик", "Повар", "Учитель", "Пожарный", "Военный"]
HEALTH_CONDITIONS = ["Здоров", "Астма", "Больное сердце", "Ампутирована правая рука", "Диабет", "Глухота на одно ухо", "Слабое зрение"]
BIO_LIST = ["Мужчина, 30 лет, женат", "Женщина, 25 лет, не замужем", "Мужчина, 45 лет, холост", "Женщина, 38 лет, замужем", "Мужчина, 22 года"]
HOBBIES = ["Выживание в дикой природе", "Моделирование", "Охота", "Рыбалка", "Шахматы", "Боевые искусства", "Садоводство", "Радиолюбитель"]
PHOBIAS = ["Клаустрофобия", "Арахнофобия", "Акрофобия (высота)", "Никтофобия (темнота)", "Агорафобия", "Социофобия"]
BAGS = ["Аптечка первой помощи", "Нож и топор", "Рация", "Запас консервов на месяц", "Фильтр для воды", "Семена растений", "Фонарик и батарейки"]
SPECIAL_PERKS = [
    "Имеет абсолютный иммунитет к первому голосованию.",
    "Может один раз за игру посмотреть любую скрытую карту оппонента.",
    "Знает точный состав бункера и ресурсов до начала игры.",
    "Может передать свой голос другому игроку."
]

# Игровое состояние
game_state = {
    "status": "IDLE", # IDLE, REGISTRATION, PLAYING, VOTING
    "players": {},    # {user_id: {"name": str, "username": str, "cards": {...}, "revealed": [...]}}
    "registered_users": set(),
    "bunker_capacity": 0,
    "current_round": 0,
    "reg_task": None  # Ссылка на фоновую задачу таймера регистрации
}

# ================= КОМАНДА /SETTINGS =================
@router.message(Command("settings"))
async def cmd_settings(message: Message):
    if message.chat.id != TARGET_CHAT_ID:
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⏱ Время раунда: {current_settings['round_time']} сек", callback_data="set_time")],
        [InlineKeyboardButton(text=f"⏳ Время реги: {current_settings['reg_time'] // 60} мин", callback_data="set_reg_time")],
        [InlineKeyboardButton(text="🔄 Сбросить настройки по умолчанию", callback_data="reset_settings")]
    ])
    
    await message.answer("⚙️ **Панель управления игрой «Бункер»:**\nНастройте параметры текущего чата:", reply_markup=keyboard, parse_mode="Markdown")

@router.callback_query(F.data == "reset_settings")
async def callback_reset_settings(callback: CallbackQuery):
    global current_settings
    current_settings = DEFAULT_SETTINGS.copy()
    await callback.answer("Настройки сброшены до значений по умолчанию!", show_alert=True)
    try:
        await callback.message.edit_text("⚙️ **Панель управления игрой «Бункер»:**\nНастройки успешно сброшены до дефолтных.", parse_mode="Markdown")
    except Exception:
        pass

# ================= ОТКРЫТИЕ РЕГИСТРАЦИИ (/registration) =================
@router.message(Command("registration"))
async def cmd_registration(message: Message):
    if message.chat.id != TARGET_CHAT_ID:
        return
    
    if game_state["status"] != "IDLE":
        await message.answer("Игра уже идет или регистрация уже открыта!")
        return

    game_state["status"] = "REGISTRATION"
    game_state["registered_users"] = set()
    game_state["players"] = {}

    # Запускаем фоновый таймер автоматического завершения регистрации
    game_state["reg_task"] = asyncio.create_task(registration_timer(message.chat.id, current_settings["reg_time"]))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Войти в бункер", callback_data="join_bunker")]
    ])

    await message.answer(
        f"🛑 **Ведётся набор в игру «Бункер»!**\nУ вас есть {current_settings['reg_time'] // 60} минут, чтобы занять место.\n\nЗарегистрированные:\n*Пока никого*",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# Фоновый таймер регистрации
async def registration_timer(chat_id: int, duration: int):
    try:
        await asyncio.sleep(duration)
        if game_state["status"] == "REGISTRATION":
            await bot.send_message(chat_id, "⏳ Время регистрации истекло! Используйте `/start_bunker` для старта игры.", parse_mode="Markdown")
    except asyncio.CancelledError:
        pass

# ================= ПРОДЛЕНИЕ РЕГИСТРАЦИИ (/extend_reg) =================
@router.message(Command("extend_reg"))
async def cmd_extend_reg(message: Message):
    if message.chat.id != TARGET_CHAT_ID:
        return
    
    if game_state["status"] != "REGISTRATION":
        await message.answer("Регистрация сейчас не проводится!")
        return

    if game_state["reg_task"]:
        game_state["reg_task"].cancel()

    extension_time = 300  # Дополнительные 5 минут
    game_state["reg_task"] = asyncio.create_task(registration_timer(message.chat.id, extension_time))

    await message.answer("⏱ Регистрация продлена еще на 5 минут!", parse_mode="Markdown")

# ================= ОТМЕНА РЕГИСТРАЦИИ (/cancel_registration) =================
@router.message(Command("cancel_registration"))
async def cmd_cancel_registration(message: Message):
    if message.chat.id != TARGET_CHAT_ID:
        return
    
    if game_state["status"] != "REGISTRATION":
        await message.answer("Нет активной регистрации для отмены.")
        return

    if game_state["reg_task"]:
        game_state["reg_task"].cancel()

    game_state["status"] = "IDLE"
    game_state["registered_users"] = set()
    game_state["players"] = {}

    await message.answer("🛑 Регистрация на игру была отменена.", parse_mode="Markdown")

# ================= ВХОД В ИГРУ ПО КНОПКЕ =================
@router.callback_query(F.data == "join_bunker")
async def callback_join_bunker(callback: CallbackQuery):
    user = callback.from_user
    if game_state["status"] != "REGISTRATION":
        await callback.answer("Регистрация закрыта или игра не идет!", show_alert=True)
        return

    if user.id in game_state["registered_users"]:
        await callback.answer("Вы уже в списке участников!", show_alert=True)
        return

    game_state["registered_users"].add(user.id)
    
    username_link = f"http://t.me/{user.username}" if user.username else f"tg://user?id={user.id}"
    display_name = f"[{user.full_name}]({username_link})"
    
    game_state["players"][user.id] = {
        "name": display_name,
        "raw_name": user.full_name,
        "username": user.username,
        "cards": {
            "profession": random.choice(PROFESSIONS),
            "health": random.choice(HEALTH_CONDITIONS),
            "bio": random.choice(BIO_LIST),
            "hobby": random.choice(HOBBIES),
            "phobia": random.choice(PHOBIAS),
            "bag": random.choice(BAGS),
            "perk": random.choice(SPECIAL_PERKS)
        },
        "revealed": []
    }

    await callback.answer("Вы успешно зарегистрированы в игре!")
    
    players_list_str = "\n".join([f"• {p['name']}" for p in game_state["players"].values()])
    total_count = len(game_state["players"])
    
    text = f"🛑 **Ведётся набор в игру «Бункер»**\nЗарегистрировались:\n{players_list_str}\n\n**Итого:** {total_count} чел."
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Войти в бункер", callback_data="join_bunker")]
    ])
    
    try:
        await callback.message.edit_text(text=text, reply_markup=keyboard, parse_mode="Markdown")
    except Exception:
        pass

# ================= ЗАПУСК ИГРЫ (/start_bunker) =================
@router.message(Command("start_bunker"))
async def cmd_start_bunker(message: Message):
    if message.chat.id != TARGET_CHAT_ID:
        return
    
    if game_state["status"] != "REGISTRATION":
        await message.answer("Сначала откройте регистрацию командой `/registration`!", parse_mode="Markdown")
        return

    if len(game_state["players"]) < current_settings["min_players"]:
        await message.answer(f"Недостаточно игроков! Нужно минимум {current_settings['min_players']}.", parse_mode="Markdown")
        return

    if game_state["reg_task"]:
        game_state["reg_task"].cancel()

    game_state["status"] = "PLAYING"
    game_state["bunker_capacity"] = max(1, len(game_state["players"]) // 2)
    game_state["current_round"] = 1

    # Раздаем стартовые карты игрокам в ЛС (например, Профессию)
    for user_id, p_data in game_state["players"].items():
        try:
            card_text = (
                f"🎴 **Ваша карточка персонажа в игре «Бункер»:**\n\n"
                f"💼 **Профессия:** {p_data['cards']['profession']}\n"
                f"❤️ *Остальные карты будут открываться по ходу раундов.*"
            )
            await bot.send_message(user_id, card_text, parse_mode="Markdown")
        except Exception:
            # Если боту не написали в ЛС заранее
            await message.answer(f"⚠️ Не удалось отправить карточку в ЛС игроку {p_data['name']}. Попросите его написать боту в ЛС и перезапустите игру.", parse_mode="Markdown")

    await message.answer(
        f"💥 **Катастрофа произошла!**\nВместимость бункера: **{game_state['bunker_capacity']} мест** из {len(game_state['players'])} участников.\n\nКарты разданы в ЛС! Игра началась, Раунд 1.",
        parse_mode="Markdown"
    )

# ================= КОМАНДА /INFO ДЛЯ ЧАТА =================
@router.message(Command("info"))
async def cmd_info(message: Message):
    if message.chat.id != TARGET_CHAT_ID:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: `/info @username`", parse_mode="Markdown")
        return
    
    target_username = args[1].lstrip('@')
    
    found_player = None
    for p_data in game_state["players"].values():
        if p_data["username"] == target_username:
            found_player = p_data
            break
            
    if not found_player:
        await message.answer("Игрок не найден или не участвует в текущей игре.")
        return
        
    revealed_text = "\n".join([f"• {item}" for item in found_player["revealed"]]) if found_player["revealed"] else "Пока ничего не открыто."
    await message.answer(f"📊 Открытая информация об игроке {found_player['name']}:\n{revealed_text}", parse_mode="Markdown")

# Запуск поллинга
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
