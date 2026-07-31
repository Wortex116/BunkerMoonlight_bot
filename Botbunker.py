import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message

# Твой токен
TOKEN = "8656111650:AAG0Sl1Fgwr3T5y6uK5emD0vJz-tKgini3A"

# Разрешенный чат (в супергруппах ID обычно начинается с -100, 
# если твой чат обычный или с минусом, поправь при необходимости)
ALLOWED_CHAT_ID = -1003839393171  # Если у чата ID без минуса и не супергруппа, замени на 3839393171

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Состояние игры в памяти
game_state = {
    "is_active": False,
    "players": {},  # user_id: { "name": ..., "card": {...} }
    "bunker": {}
}

# --- БАЗА ДАННЫХ ДЛЯ ГЕНЕРАЦИИ (Словари и списки) ---
BUNKER_DATA = {
    "catastrophes": [
        "Ядерная война", "Глобальная пандемия вируса", "Падение метеорита", 
        "Восстание искусственного интеллекта", "Экологическая катастрофа (утечка токсинов)"
    ],
    "area": [30, 50, 75, 100, 120],  # кв.м
    "time": ["1 год", "3 года", "5 лет", "10 лет", "Бункер автономный навсегда"],
    "food": ["Запасы еды и воды на исходе", "Гидропонная ферма с дефектом", "Полный запас синтетической еды", "Консервы на 10 лет"],
    "specials": [
        "Есть лаборатория для создания вакцины", "Сейф с оружием и патронами", 
        "Сломана система вентиляции (кислород на исходе)", "Есть библиотека со всеми знаниями человечества"
    ]
}

CHARACTER_DATA = {
    "professions": [
        "Врач-хирург", "Инженер-механик", "Программист", "Повар", "Агроном", 
        "Пожарный", "Психолог", "Строитель", "Электрик", "Биолог", "Военный", "Уборщик"
    ],
    "health": [
        "Абсолютно здоров", "Астма", "Хроническая бессонница", "Сахарный диабет", 
        "Слабое сердце", "Аллергия на антибиотики", "Плохое зрение (-6)"
    ],
    "hobby": [
        "Выживание в дикой природе", "Игра на гитаре", "Радиолюбитель", "Охота и рыбалка", 
        "Альпинизм", "Шахматы", "Рукоделие", "Ремонт бытовой техники"
    ],
    "phobia": [
        "Клаустрофобия", "Боязнь темноты", "Арахнофобия (пауки)", "Боязнь микробов", 
        "Акрофобия (высота)", "Никаких фобий нет"
    ],
    "trait": [
        "Альтруист", "Эгоист", "Лжец (в карточке может быть ложь)", "Агрессивный", 
        "Стрессоустойчивый", "Паникер", "Дипломат"
    ],
    "baggage": [
        "Аптечка первой помощи", "Нож и веревка", "Семена редких растений", 
        "Фонарик с динамо-машиной", "Рация", "Запас консервов на 3 дня", "Резиновая уточка"
    ],
    "secret": [
        "Тайно инфицирован вирусом, но симптомов нет", "Бывший заключенный", 
        "Имеет иммунитет к катастрофе", "Контрабандист, прячет пистолет", "Никаких секретов"
    ]
}

def generate_bunker():
    return {
        "catastrophe": random.choice(BUNKER_DATA["catastrophes"]),
        "area": random.choice(BUNKER_DATA["area"]),
        "time": random.choice(BUNKER_DATA["time"]),
        "food": random.choice(BUNKER_DATA["food"]),
        "special": random.choice(BUNKER_DATA["specials"])
    }

def generate_card():
    return {
        "profession": random.choice(CHARACTER_DATA["professions"]),
        "health": random.choice(CHARACTER_DATA["health"]),
        "hobby": random.choice(CHARACTER_DATA["hobby"]),
        "phobia": random.choice(CHARACTER_DATA["phobia"]),
        "trait": random.choice(CHARACTER_DATA["trait"]),
        "baggage": random.choice(CHARACTER_DATA["baggage"]),
        "secret": random.choice(CHARACTER_DATA["secret"]),
    }


# --- ФИЛЬТР БЕЗОПАСНОСТИ ДЛЯ ГРУППЫ ---
@dp.message(F.chat.type != "private")
async def filter_groups(message: Message):
    # Если сообщение из любой другой группы — бот полностью игнорирует
    if message.chat.id != ALLOWED_CHAT_ID:
        return


# --- КОМАНДЫ ДЛЯ ИГРЫ В ГРУППЕ ---

@dp.message(F.chat.id == ALLOWED_CHAT_ID, Command("bunker"))
async def start_lobby(message: Message):
    """Запуск сбора игроков."""
    if game_state["is_active"]:
        await message.answer("⚠️ Игра уже идет или собирается!")
        return

    game_state["is_active"] = True
    game_state["players"] = {}
    game_state["bunker"] = generate_bunker()

    await message.answer(
        "☢️ **Внимание! Набор в Бункер открыт!**\n\n"
        "Катастрофа на подходе. Места внутри ограничены.\n"
        "Напишите `/join`, чтобы занять место среди кандидатов."
    )


@dp.message(F.chat.id == ALLOWED_CHAT_ID, Command("join"))
async def join_game(message: Message):
    """Регистрация игрока."""
    if not game_state["is_active"]:
        await message.answer("❌ Сейчас нет активного набора. Напишите `/bunker` для старта.")
        return
    
    user_id = message.from_user.id
    user_name = message.from_user.full_name

    if user_id in game_state["players"]:
        await message.answer(f"ℹ️ {user_name}, вы уже в списке выживших!")
        return

    # Генерируем карточку для игрока
    card = generate_card()
    game_state["players"][user_id] = {
        "name": user_name,
        "card": card
    }
    
    await message.answer(f"✅ **{user_name}** присоединился к игре! Всего игроков: {len(game_state['players'])}")

    # Отправка карточки в ЛС
    try:
        await bot.send_message(
            user_id,
            "🔐 **Ваша секретная карточка для игры в «Бункер»:**\n\n"
            f"🛠 Профессия:\n"
            f"❤️ Здоровье:\n"
            f"🎯 Хобби:\n"
            f"😱 Фобия:\n"
            f"🧠 Черта характера:\n"
            f"🎒 Багаж:\n"
            f"🤫 Секрет:\n\n"
            "Сохраняйте информацию в тайне и раскрывайте характеристики по ходу игры в чате!"
        )
    except Exception:
        await message.answer(
            f"⚠️ {user_name}, я не смог отправить вам карточку в личные сообщения! "
            f"Пожалуйста, перейдите в диалог со мной и нажмите кнопку **Запустить** (или `/start`)."
        )


@dp.message(F.chat.id == ALLOWED_CHAT_ID, Command("start_game"))
async def begin_game_action(message: Message):
    """Старт самой игры (когда все зашли)."""
    if not game_state["is_active"]:
        await message.answer("Сначала запустите набор через `/bunker`.")
        return

    if len(game_state["players"]) < 2:
        await message.answer("⚠️ Недостаточно игроков для старта (нужно хотя бы 2).")
        return

    bunker = game_state["bunker"]
    players_list = "\n".join([f"• {p['name']}" for p in game_state["players"].values()])

    await message.answer(
        "🚨 **Игра началась! Двери бункера затворяются!** 🚨\n\n"
        "🌍 **Информация о бункере:**\n"
        f"• Катастрофа: {bunker['catastrophe']}\n"
        f"• Площадь: {bunker['area']} кв.м\n"
        f"• Срок отсидки: {bunker['time']}\n"
        f"• Запасы еды: {bunker['food']}\n"
        f"• Особенность: {bunker['special']}\n\n"
        f"👥 **Участники ({len(game_state['players'])}):**\n{players_list}\n\n"
        "Пора начинать обсуждения! Первый раунд: время раскрыть свою **профессию** в чате."
    )


# --- ОБРАБОТКА ЛИЧНЫХ СООБЩЕНИЙ ---

@dp.message(F.chat.type == "private")
async def handle_private(message: Message):
    """Защита ЛС: отвечает только тем, кто в текущей игре."""
    user_id = message.from_user.id
    
    # Если игра не активна или пользователя нет среди участников — бот молча игнорирует
    if not game_state["is_active"] or user_id not in game_state["players"]:
        return

    if message.text == "/start":
        card = game_state["players"][user_id]["card"]
        await message.answer(
            "Привет! Вы зарегистрированы в текущей игре.\n"
            "Вот ваша карточка повторно:\n\n"
            f"🛠 Профессия: {card['profession']}\n"
            f"❤️ Здоровье: {card['health']}\n"
            f"🎯 Хобби: {card['hobby']}\n"
            f"😱 Фобия: {card['phobia']}\n"
            f"🧠 Характер: {card['trait']}\n"
            f"🎒 Багаж: {card['baggage']}\n"
            f"🤫 Секрет: {card['secret']}"
        )
        return

    await message.answer("Ваша карточка уже отправлена выше. Все обсуждения проходят в основном чате группы!")


async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот по «Бункеру» запущен и готов к работе...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
