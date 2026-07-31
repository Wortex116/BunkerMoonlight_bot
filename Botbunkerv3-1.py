import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Твой токен
TOKEN = "8656111650:AAG0Sl1Fgwr3T5y6uK5emD0vJz-tKgini3A"

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# ================= НАСТРОЙКИ ПО УМОЛЧАНИЮ =================
DEFAULT_SETTINGS = {
    "round_time": 120,
    "min_players": 4,
    "max_players": 20,
    "reg_time": 300,
}

current_settings = DEFAULT_SETTINGS.copy()

# ================= БАЗЫ ДАННЫХ =================
DISASTERS = [
    "Ядерная война и глобальная ядерная зима",
    "Высокотехнологичный искусственный интеллект захватил контроль над планетой",
    "Смертоносный биологический вирус с летальностью 99.8%",
    "Падение массивного астероида, вызвавшие многолетнее затмение атмосферы",
    "Глобальное изменение климата и таяние ледников, затопившее сушу",
    "Вторжение инопланетной цивилизации и токсичная атмосфера",
    "Апокалипсис из-за глобального зомби-вируса",
    "Взрыв супервулкана, закрывший солнце пеплом на десятилетия",
    "Тотальный энергетический коллапс и выжженная магнитная буря",
    "Падение орбитальной станции на поверхность Земли"
]

BUNKER_CONDITIONS = [
    {"shelter": "Элитный подземный бункер корпорации", "years": "3 года", "food": "Запасы гидропоники и консервов", "features": "Есть собственная оранжерея и генератор на уране"},
    {"shelter": "Заброшенный военный объект времен Холодной войны", "years": "1 год", "food": "Армейские сухпайки с истекающим сроком", "features": "Нарушена система вентиляции, требуется ремонт"},
    {"shelter": "Научно-исследовательская станция в вечной мерзлоте", "years": "5 лет", "food": "Запасы сублимированной еды", "features": "Суровый холод снаружи, автономный геотермальный источник"},
    {"shelter": "Бункер глубокого залегания под правительственным зданием", "years": "10 лет", "food": "Огромные склады долгосрочного хранения", "features": "Есть медицинский отсек и запасы медикаментов"},
    {"shelter": "Станция метро глубокого заложения", "years": "2 года", "food": "Продовольственные склады метрополитена", "features": "Слышны странные звуки из технических тоннелей"}
]

PROFESSIONS = [
    "Инженер-механик", "Врач-хирург", "Психотерапевт", "Программист", "Агроном", 
    "Электрик", "Шеф-повар", "Учитель биологии", "Пожарный-спасатель", "Военный связист",
    "Химик-технолог", "Эколог", "Строитель-монтажник", "Автомеханик", "Фермер",
    "Сантехник", "Ветеринар", "Фармацевт", "Стоматолог", "Психиатр",
    "Пилот гражданской авиации", "Морской капитан", "Альпинист-инструктор", "Спецназовец в отставке", "Спасатель МЧС",
    "Ядерный физик", "Геолог-разведчик", "Метеоролог", "Биоинженер", "Криптограф",
    "Продюсер", "Маркетолог", "Журналист-расследователь", "Переводчик-синхронист", "Историк-археолог",
    "Архитектор", "Библиотекарь", "Священнослужитель", "Юрист по международному праву", "Экономист",
    "Бармен", "Парикмахер-стилист", "Тату-мастер", "Флорист", "Промышленный альпинист",
    "Слесарь-инструментальщик", "Токарь-фрезеровщик", "Крановщик", "Сварщик высшего разряда", "Машинист поезда"
]

HEALTH_CONDITIONS = [
    "Здоров", "Бронхиальная астма (нужен ингалятор)", "Больное сердце (риск при нагрузках)", 
    "Ампутирована левая рука ниже локтя", "Сахарный диабет (требует инсулин)", 
    "Полная глухота на одно ухо", "Слабое зрение (носить сильные очки)", "Аллергия на пенициллин",
    "Хронический гастрит", "Переломы ребер в прошлом (зажили с деформацией)",
    "ВИЧ-положительный (нужна терапия)", "Хронический гепатит B", "Эпилепсия (редкие приступы)",
    "Гипертония (скачки давления)", "Плоскостопие 3 степени", "Аллергия на лактозу и глютен",
    "Отсутствие селезенки", "Туберкулез в закрытой форме", "Синдром Туретта (редкие тики)",
    "Искривление позвоночника", "Частые мигрени", "Аллергия на пчелиный яд", "Хронический бронхит",
    "Ампутирована правая стопа", "Тяжелая форма псориаза", "Бессонница хроническая",
    "Камни в почках", "Синдром хронической усталости", "Частые носовые кровотечения",
    "Травма коленного сустава (хромота)", "Аллергия на цитрусовые", "Аллергия на шерсть животных",
    "Остеохондроз", "Повышенная утомляемость", "Тяжелая форма дальтонизма",
    "Отсутствие зубов (нужны протезы)", "Травма челюсти (трудно говорить)", "Частые панические атаки",
    "Аллергия на холод", "Пониженное давление (гипотония)", "Аллергия на пыльцу",
    "Хронический отит", "Заикание при волнении", "Тяжелая форма лучевой болезни в анамнезе",
    "Аллергия на бытовую химию", "Синдром раздраженного кишечника", "Аллергия на орехи",
    "Нарушение координации движений", "Хронический синусит", "Аллергия на красную рыбу"
]

BIO_GENDERS = ["Мужчина", "Женщина"]
BIO_STATUSES = [
    "женат, 2 детей", "замужем, 1 ребенок", "холост, детей нет", "не замужем, детей нет",
    "вдовец, 3 детей", "вдова, детей нет", "в разводе, 1 ребенок", "женат, детей нет",
    "замужем, 3 детей", "в разводе, 2 детей", "холост, есть приемный ребенок",
    "не замужем, беременна", "женат, ждет пополнения", "вдовец, детей нет",
    "гражданский брак, детей нет", "гражданский брак, 2 детей", "холост, заядлый чайлдфри",
    "замужем, чайлдфри", "вдовец, 1 ребенок", "в разводе, детей нет",
    "женат, 4 детей", "замужем, 2 детей", "холост, опекун младшего брата",
    "не замужем, опекун сестры", "в разводе, выплачивает алименты", "женат, взрослые дети",
    "замужем, взрослые дети", "холост, живет с родителями", "не замужем, живет одна",
    "вдовец, взрослые дети", "вдова, взрослые дети", "гражданский брак, 1 ребенок",
    "холост, содержит приют для животных", "не замужем, волонтер", "в разводе, делит опеку",
    "женат, дети за границей", "замужем, дети учатся в другом городе", "холост, путешественник",
    "не замужем, карьеристка", "вдовец, пенсионер", "вдова, пенсионерка",
    "молодой специалист, холост", "молодая мать-одиночка", "отец-одиночка, 2 детей",
    "отец-одиночка, 1 ребенок", "в разводе, оформляет опеку", "женат, совместный бизнес с супругой",
    "замужем, муж военный", "холост, бывший спортсмен", "не замужем, творческая личность"
]

HOBBIES = [
    "Выживание в дикой природе и туризм", "Моделирование радиоэлектроники", "Охота и рыболовство", 
    "Шахматы и стратегические игры", "Боевые искусства (карате/айкидо)", "Садоводство и пермакультура", 
    "Радиолюбительство", "Вязание и шитье одежды", "Альпинизм", "Пчеловодство", 
    "Коллекционирование оружия", "Сладкоежка (любит печь торты и варить карамель)", "Керамика и гончарное дело",
    "Игра на гитаре и укулеле", "Историческая реконструкция", "Резьба по дереву", "Астрономия и наблюдение в телескоп",
    "Спортсмен-марафонец", "Коллекционирование марок и монет", "Изготовление ножей ручной работы",
    "Йога и медитация", "Танцы (сальса, танго)", "Стендап-комик", "Кулинария народов мира",
    "Виноделие и самогоноварение дома", "Изготовление кожаных изделий", "Настольные ролевые игры (D&D)",
    "Сбор грибов и ягод", "Аквариумистика", "Разведение экзотических растений", "Создание сайтов и код",
    "Ремонт старой техники", "Фотография и видеомонтаж", "Писательство фантастических рассказов",
    "Рисование маслом и акварелью", "Кастомизация одежды", "Изготовление свечей ручной работы",
    "Игра в покер и блекджек", "Фокусы и иллюзии", "Скалолазание", "Тяжелая атлетика",
    "Философия и чтение классики", "Изучение иностранных языков", "Коллекционирование виниловых пластинок",
    "Дизайн интерьеров", "Мыловарение", "Создание миниатюрных макетов", "Уход за аквариумными рыбками",
    "Моделирование кораблей в бутылках", "Игра на барабанной установке"
]

PHOBIAS = [
    "Клаустрофобия (боязнь замкнутых пространств)", "Арахнофобия (боязнь пауков)", 
    "Акрофобия (боязнь высоты)", "Никтофобия (боязнь темноты)", "Агорафобия (боязнь открытых пространств)", 
    "Социофобия", "Гемофобия (боязнь крови)", "Танатофобия (боязнь смерти)", "Гидрофобия (боязнь воды)",
    "Айхмофобия (боязнь острых предметов)", "Кинофобия (боязнь собак)", "Офидиофобия (боязнь змей)",
    "Энтомофобия (боязнь насекомых)", "Авиафобия (боязнь полетов)", "Пирофобия (боязнь огня)",
    "Ксенофобия (боязнь незнакомцев)", "Бронтофобия (боязнь грозы и молний)", "Аутофобия (боязнь одиночества)",
    "Никтофобия (боязнь темноты)", "Микробофобия (боязнь бактерий и грязи)", "Агерофобия (боязнь старости)",
    "Андрофобия (боязнь мужчин)", "Гинефобия (боязнь женщин)", "Демофобия (боязнь толпы)",
    "Кардиофобия (боязнь болезней сердца)", "Литикофобия (боязнь судебных исков)", "Номофобия (боязнь остаться без телефона)",
    "Педиофобия (боязнь кукол)", "Семафофобия (боязнь сигналов светофора)", "Токсикофобия (боязнь отравления)",
    "Филофобия (боязнь влюбиться)", "Хаплофобия (боязнь прикосновений)", "Эргофобия (боязнь работы)",
    "Алекторофобия (боязнь кукол/птиц)", "Аматофобия (боязнь пыли)", "Анемофобия (боязнь ветра)",
    "Апантропофобия (боязнь людей)", "Атаксиофобия (боязнь беспорядка)", "Бленнофобия (боязнь слизи)",
    "Гелиофобия (боязнь солнца)", "Гоплофобия (боязнь оружия)", "Илиофобия (боязнь грязи)",
    "Катисофобия (боязнь сидеть)", "Копрофобия (боязнь фекалий)", "Лигирофобия (боязнь громких звуков)",
    "Опиофобия (боязнь лекарств)", "Паразитофобия (боязнь паразитов)", "Погонофобия (боязнь бород)",
    "Скопофобия (боязнь быть замеченным)", "Трассофобия (боязнь транспорта)"
]

BAGS = [
    "Аптечка первой помощи расширенная", "Армейский нож и топорик", "Портативная рация с генератором", 
    "Запас консервов на 3 месяца", "Комплект фильтров для очистки воды", "Семена редких сельскохозяйственных культур", 
    "Фонарик Динамо и комплект батареек", "Набор слесарных инструментов", "Книга по выживанию и медицине",
    "Складная палатка и спальный мешок", "Набор для разведения огня (огниво, сухое горючее)",
    "Набор рыболовных снастей и леска", "Охотничьи спички и сухой спирт", "Портативная солнечная батарея",
    "Ультрафиолетовый стерилизатор для воды", "Набор медицинских скальпелей и нитей", "Респираторы с комплектом сменных фильтров",
    "Многофункциональная лопата-мультитул", "Комплект теплой термоодежды", "Набор батареек разных размеров",
    "Ручной водяной насос", "Антибиотики широкого спектра действия (запас)", "Набор для шитья и починки одежды",
    "Веревка альпинистская 50 метров", "Набор гаечных ключей и отверток", "Набор для оказания первой помощи при переломах",
    "Портативная газорежущая горелка", "Набор химических грелок для тела", "Комплект защитных очков и перчаток",
    "Набор для анализа воды и почвы", "Портативный дозиметр радиации", "Запас сахара, соли и специй",
    "Комплект туристической посуды из титана", "Складная ножовка по металлу и дереву", "Набор рыболовных сетей",
    "Комплект светодиодных лент с аккумулятором", "Набор для консервации продуктов", "Портативный мини-холодильник на аккумуляторе",
    "Набор для чистки оружия", "Комплект латексных медицинских перчаток", "Набор для выживания в экстремальных условиях",
    "Портативный очиститель воздуха", "Комплект карт местности и атлас дорог", "Набор инструментов для точной пайки",
    "Портативный прибор ночного видения", "Комплект спасательных термоодеял", "Запас сублимированного кофе и чая",
    "Набор резиновых жгутов для остановки крови", "Портативный мини-проектор с обучающими книгами", "Набор пищевых ароматизаторов и дрожжей"
]

SPECIAL_PERKS = [
    "Имеет абсолютный иммунитет к первому голосованию об изгнании.",
    "Может один раз за игру принудительно посмотреть любую скрытую карту любого игрока.",
    "Знает точный план бункера и расположение секретных складов.",
    "Может перенаправить свой голос на любого другого игрока во время фазы голосования.",
    "В случае ничьей при голосовании его голос имеет двойной вес.",
    "Имеет право один раз за игру заблокировать открытие карты любого оппонента.",
    "Может защитить одного из участников от изгнания в текущем раунде (один раз за игру).",
    "Видит скрытые мотивы и роль одного из случайных игроков в начале игры.",
    "Обладает правом вето на одно голосование за всю игру.",
    "Может поменяться одной из своих нераскрытых карт с изгнанным игроком.",
    "Иммунитет к пропускам хода и штрафам.",
    "Может узнать количество голосов против себя перед финальным подсчетом.",
    "Владеет секретным кодом от оружейного сейфа в бункере.",
    "Имеет скрытую рацию для связи с внешним миром.",
    "Может приказать боту скрыть одну свою характеристику после ее открытия.",
    "Получает право дополнительного голоса на каждом третьем круге голосования.",
    "Может передать свой спецэффект другому выжившему.",
    "Имеет право дважды открывать карту в один раунд.",
    "Знает точную дату и время окончания изоляции бункера.",
    "Может обнулить результаты текущего голосования один раз за партию."
]

# ================= ХРАНИЛИЩЕ ИГР ПО ЧАТАМ =================
chats_games = {}

def get_chat_game(chat_id: int):
    """Получить или создать игровое состояние для чата"""
    if chat_id not in chats_games:
        chats_games[chat_id] = {
            "status": "IDLE",  # IDLE, REGISTRATION, PLAYING, VOTING
            "players": {},
            "registered_users": set(),
            "bunker": {},
            "bunker_capacity": 0,
            "current_round": 0,
            "reg_task": None,
            "voting_data": {},
            "settings": DEFAULT_SETTINGS.copy()  # Настройки для каждого чата
        }
    return chats_games[chat_id]

def get_chat_id_by_game(game):
    """Найти chat_id по объекту игры"""
    for cid, g in chats_games.items():
        if g == game:
            return cid
    return None

# ================= ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ГЕНЕРАЦИИ =================
def generate_unique_cards(existing_players):
    """Генерирует уникальные карты для игрока"""
    used_professions = {p["cards"]["profession"] for p in existing_players.values()}
    used_health = {p["cards"]["health"] for p in existing_players.values()}
    used_bios = {p["cards"]["bio"] for p in existing_players.values()}
    used_hobbies = {p["cards"]["hobby"] for p in existing_players.values()}
    used_phobias = {p["cards"]["phobia"] for p in existing_players.values()}
    used_bags = {p["cards"]["bag"] for p in existing_players.values()}
    used_perks = {p["cards"]["perk"] for p in existing_players.values()}

    avail_prof = [x for x in PROFESSIONS if x not in used_professions]
    profession = random.choice(avail_prof) if avail_prof else random.choice(PROFESSIONS)

    avail_health = [x for x in HEALTH_CONDITIONS if x not in used_health]
    health = random.choice(avail_health) if avail_health else random.choice(HEALTH_CONDITIONS)

    while True:
        gender = random.choice(BIO_GENDERS)
        age = random.randint(20, 65)
        status = random.choice(BIO_STATUSES)
        bio_str = f"{gender}, {age} лет, {status}"
        if bio_str not in used_bios:
            break

    avail_hobby = [x for x in HOBBIES if x not in used_hobbies]
    hobby = random.choice(avail_hobby) if avail_hobby else random.choice(HOBBIES)

    avail_phobia = [x for x in PHOBIAS if x not in used_phobias]
    phobia = random.choice(avail_phobia) if avail_phobia else random.choice(PHOBIAS)

    avail_bag = [x for x in BAGS if x not in used_bags]
    bag = random.choice(avail_bag) if avail_bag else random.choice(BAGS)

    avail_perk = [x for x in SPECIAL_PERKS if x not in used_perks]
    perk = random.choice(avail_perk) if avail_perk else random.choice(SPECIAL_PERKS)

    return {
        "profession": profession,
        "health": health,
        "bio": bio_str,
        "hobby": hobby,
        "phobia": phobia,
        "bag": bag,
        "perk": perk
    }

# ================= КОМАНДА /SETTINGS =================
@router.message(Command("settings"))
async def cmd_settings(message: Message):
    if message.chat.type not in ["group", "supergroup"]:
        await message.answer("❌ Эту команду можно использовать только в групповых чатах!")
        return
    
    chat_id = message.chat.id
    game = get_chat_game(chat_id)
    settings = game["settings"]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⏱ Время раунда: {settings['round_time']} сек", callback_data=f"set_time_{chat_id}")],
        [InlineKeyboardButton(text=f"⏳ Время реги: {settings['reg_time'] // 60} мин", callback_data=f"set_reg_time_{chat_id}")],
        [InlineKeyboardButton(text="🔄 Сбросить настройки по умолчанию", callback_data=f"reset_settings_{chat_id}")]
    ])
    
    await message.answer("⚙️ **Панель управления игрой «Бункер»:**\nНастройте параметры текущего чата:", reply_markup=keyboard, parse_mode="Markdown")

@router.callback_query(F.data.startswith("reset_settings_"))
async def callback_reset_settings(callback: CallbackQuery):
    chat_id = int(callback.data.split("_")[2])
    game = get_chat_game(chat_id)
    game["settings"] = DEFAULT_SETTINGS.copy()
    await callback.answer("Настройки сброшены до значений по умолчанию!", show_alert=True)
    try:
        await callback.message.edit_text("⚙️ **Панель управления игрой «Бункер»:**\nНастройки успешно сброшены до дефолтных.", parse_mode="Markdown")
    except Exception:
        pass

# ================= ОТКРЫТИЕ РЕГИСТРАЦИИ =================
@router.message(Command("registration"))
async def cmd_registration(message: Message):
    if message.chat.type not in ["group", "supergroup"]:
        await message.answer("❌ Эту команду можно использовать только в групповых чатах!")
        return
    
    chat_id = message.chat.id
    game = get_chat_game(chat_id)
    settings = game["settings"]
    
    if game["status"] != "IDLE":
        await message.answer("❌ Игра уже идет или регистрация уже открыта!")
        return

    game["status"] = "REGISTRATION"
    game["registered_users"] = set()
    game["players"] = {}

    game["reg_task"] = asyncio.create_task(registration_timer(chat_id, settings["reg_time"]))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Войти в бункер", callback_data=f"join_bunker_{chat_id}")]
    ])

    await message.answer(
        f"🛑 **Ведётся набор в игру «Бункер»!**\nУ вас есть {settings['reg_time'] // 60} минут, чтобы занять место.\n\nЗарегистрированные:\n*Пока никого*",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def registration_timer(chat_id: int, duration: int):
    try:
        await asyncio.sleep(duration)
        game = get_chat_game(chat_id)
        if game["status"] == "REGISTRATION":
            await bot.send_message(chat_id, "⏳ Время регистрации истекло! Используйте `/start_bunker` для старта игры.", parse_mode="Markdown")
    except asyncio.CancelledError:
        pass

# ================= ПРОДЛЕНИЕ РЕГИСТРАЦИИ =================
@router.message(Command("extend_reg"))
async def cmd_extend_reg(message: Message):
    if message.chat.type not in ["group", "supergroup"]:
        return
    
    chat_id = message.chat.id
    game = get_chat_game(chat_id)
    settings = game["settings"]
    
    if game["status"] != "REGISTRATION":
        await message.answer("❌ Регистрация сейчас не проводится!")
        return

    if game["reg_task"]:
        game["reg_task"].cancel()

    game["reg_task"] = asyncio.create_task(registration_timer(chat_id, 300))
    await message.answer("⏱ Регистрация продлена еще на 5 минут!", parse_mode="Markdown")

# ================= ОТМЕНА РЕГИСТРАЦИИ =================
@router.message(Command("cancel_registration"))
async def cmd_cancel_registration(message: Message):
    if message.chat.type not in ["group", "supergroup"]:
        return
    
    chat_id = message.chat.id
    game = get_chat_game(chat_id)
    
    if game["status"] != "REGISTRATION":
        await message.answer("❌ Нет активной регистрации для отмены.")
        return

    if game["reg_task"]:
        game["reg_task"].cancel()

    game["status"] = "IDLE"
    game["registered_users"] = set()
    game["players"] = {}

    await message.answer("🛑 Регистрация на игру была отменена.", parse_mode="Markdown")

# ================= ВХОД В ИГРУ ПО КНОПКЕ =================
@router.callback_query(F.data.startswith("join_bunker_"))
async def callback_join_bunker(callback: CallbackQuery):
    chat_id = int(callback.data.split("_")[2])
    game = get_chat_game(chat_id)
    user = callback.from_user

    if game["status"] != "REGISTRATION":
        await callback.answer("❌ Регистрация закрыта или игра не идет!", show_alert=True)
        return

    if user.id in game["registered_users"]:
        await callback.answer("⚠️ Вы уже в списке участников!", show_alert=True)
        return

    game["registered_users"].add(user.id)
    
    username_link = f"http://t.me/{user.username}" if user.username else f"tg://user?id={user.id}"
    display_name = f"[{user.full_name}]({username_link})"
    
    unique_cards = generate_unique_cards(game["players"])

    game["players"][user.id] = {
        "name": display_name,
        "raw_name": user.full_name,
        "username": user.username,
        "cards": unique_cards,
        "revealed": [],
        "is_alive": True
    }

    await callback.answer("✅ Вы успешно зарегистрированы в игре!")
    
    players_list_str = "\n".join([f"• {p['name']}" for p in game["players"].values()])
    total_count = len(game["players"])
    
    text = f"🛑 **Ведётся набор в игру «Бункер»**\nЗарегистрировались:\n{players_list_str}\n\n**Итого:** {total_count} чел."
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Войти в бункер", callback_data=f"join_bunker_{chat_id}")]
    ])
    
    try:
        await callback.message.edit_text(text=text, reply_markup=keyboard, parse_mode="Markdown")
    except Exception:
        pass

# ================= ЗАПУСК ИГРЫ =================
@router.message(Command("start_bunker"))
async def cmd_start_bunker(message: Message):
    if message.chat.type not in ["group", "supergroup"]:
        return
    
    chat_id = message.chat.id
    game = get_chat_game(chat_id)
    settings = game["settings"]
    
    if game["status"] != "REGISTRATION":
        await message.answer("❌ Сначала откройте регистрацию командой `/registration`!", parse_mode="Markdown")
        return

    total_players = len(game["players"])
    if total_players < settings["min_players"]:
        await message.answer(f"❌ Недостаточно игроков! Нужно минимум {settings['min_players']} участников.", parse_mode="Markdown")
        return

    if game["reg_task"]:
        game["reg_task"].cancel()

    game["status"] = "PLAYING"
    game["bunker_capacity"] = max(1, total_players // 2)
    game["bunker"] = {
        "disaster": random.choice(DISASTERS),
        "data": random.choice(BUNKER_CONDITIONS)
    }
    game["current_round"] = 1

    # Раздаём карты
    for user_id, p_data in game["players"].items():
        try:
            prof = p_data['cards']['profession']
            p_data["revealed"].append(f"Профессия: {prof}")
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👁 Открыть след. карту", callback_data=f"reveal_next_card_{chat_id}")]
            ])
            
            await bot.send_message(
                user_id,
                f"🎴 **Игра началась!** Ваш персонаж:\n\n💼 **Профессия:** {prof}\n\n*Нажмите кнопку ниже для открытия карт в последующих раундах.*",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        except Exception as e:
            await message.answer(f"⚠️ Не удалось отправить сообщение игроку {p_data['name']}. Убедитесь, что бот запущен у него в ЛС.", parse_mode="Markdown")

    bunker_info = game["bunker"]
    await message.answer(
        f"💥 **Катастрофа произошла!**\n\n"
        f"🌍 **Катаклизм:** {bunker_info['disaster']}\n"
        f"🛡 **Убежище:** {bunker_info['data']['shelter']}\n"
        f"⏳ **Срок изоляции:** {bunker_info['data']['years']}\n"
        f"🥫 **Еда и ресурсы:** {bunker_info['data']['food']}\n"
        f"⚙️ **Особенность:** {bunker_info['data']['features']}\n\n"
        f"👥 Всего участников: {total_players} | 🕳 **Мест в бункере: {game['bunker_capacity']}**\n\n"
        f"🔔 **Раунд 1 начался!** У вас есть время на обсуждение.",
        parse_mode="Markdown"
    )

# ================= ОТКРЫТИЕ КАРТ В ЛС =================
@router.callback_query(F.data.startswith("reveal_next_card_"))
async def callback_reveal_card(callback: CallbackQuery):
    chat_id = int(callback.data.split("_")[3])
    user_id = callback.from_user.id
    
    game = get_chat_game(chat_id)
    
    if user_id not in game["players"]:
        await callback.answer("❌ Вы не участник активной игры!", show_alert=True)
        return

    p_data = game["players"][user_id]
    cards = p_data["cards"]
    
    rounds_keys = [
        ("health", "❤️ Здоровье"),
        ("bio", "🧬 Биология (пол, возраст, семья)"),
        ("hobby", "🎨 Хобби"),
        ("phobia", "⚠️ Фобия"),
        ("bag", "🎒 Багаж"),
        ("perk", "✨ Спецсвойство")
    ]
    
    current_revealed_count = len(p_data["revealed"]) - 1  # -1 потому что профессия уже открыта
    if current_revealed_count >= len(rounds_keys):
        await callback.answer("✅ Вы уже открыли все свои карты!", show_alert=True)
        return

    next_key, label = rounds_keys[current_revealed_count]
    card_value = cards[next_key]
    
    reveal_string = f"{label.split()[1].capitalize()}: {card_value}"
    if reveal_string not in p_data["revealed"]:
        p_data["revealed"].append(reveal_string)

    await callback.answer(f"✅ Открыто: {label}!")
    
    all_rev_text = "\n".join([f"• {item}" for item in p_data["revealed"]])
    try:
        await callback.message.edit_text(
            f"🎴 **Ваш персонаж в игре «Бункер»:**\n\n{all_rev_text}",
            parse_mode="Markdown"
        )
    except Exception:
        pass

# ================= ГОЛОСОВАНИЕ =================
@router.message(Command("vote"))
async def cmd_vote_trigger(message: Message):
    if message.chat.type not in ["group", "supergroup"]:
        return
    
    chat_id = message.chat.id
    game = get_chat_game(chat_id)
    
    if game["status"] != "PLAYING":
        await message.answer("❌ Сейчас фаза голосования недоступна.")
        return

    game["status"] = "VOTING"
    game["voting_data"] = {}

    await message.answer("🗳 **Фаза голосования началась!**\nКаждому оставшемуся участнику отправлена инструкция в личные сообщения.", parse_mode="Markdown")

    for uid, p in game["players"].items():
        if not p["is_alive"]:
            continue
        
        keyboard_buttons = []
        for target_id, target_data in game["players"].items():
            if target_id != uid and target_data["is_alive"]:
                keyboard_buttons.append([InlineKeyboardButton(
                    text=f"Выгнать: {target_data['raw_name']}", 
                    callback_data=f"vote_to_{chat_id}_{target_id}"
                )])

        if keyboard_buttons:
            kb = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            try:
                await bot.send_message(uid, "🚪 **Время голосования!**\nКого вы хотите выгнать из убежища?", reply_markup=kb, parse_mode="Markdown")
            except Exception:
                pass

@router.callback_query(F.data.startswith("vote_to_"))
async def callback_vote_handler(callback: CallbackQuery):
    parts = callback.data.split("_")
    chat_id = int(parts[2])
    target_id = int(parts[3])
    voter_id = callback.from_user.id

    game = get_chat_game(chat_id)
    
    if voter_id not in game["players"] or not game["players"][voter_id]["is_alive"]:
        await callback.answer("❌ Вы не можете голосовать!", show_alert=True)
        return

    game["voting_data"][voter_id] = target_id
    await callback.answer("✅ Ваш голос принят!")
    try:
        await callback.message.edit_text("✅ Ваш голос успешно учтен. Ожидайте результатов.")
    except Exception:
        pass

    # Проверяем, проголосовали ли все
    alive_players = [uid for uid, p in game["players"].items() if p["is_alive"]]
    if len(game["voting_data"]) >= len(alive_players):
        votes_count = {}
        for v_target in game["voting_data"].values():
            votes_count[v_target] = votes_count.get(v_target, 0) + 1

        if votes_count:
            max_votes = max(votes_count.values())
            candidates_to_kick = [uid for uid, count in votes_count.items() if count == max_votes]

            if len(candidates_to_kick) == 1:
                kicked_id = candidates_to_kick[0]
                game["players"][kicked_id]["is_alive"] = False
                kicked_name = game["players"][kicked_id]["name"]

                game["status"] = "PLAYING"
                
                alive_remaining = [p for p in game["players"].values() if p["is_alive"]]
                
                if len(alive_remaining) <= game["bunker_capacity"]:
                    survivors_str = "\n".join([f"• {p['name']}" for p in alive_remaining])
                    await bot.send_message(
                        chat_id,
                        f"🚨 По результатам голосования изгнан игрок: {kicked_name}!\n\n"
                        f"🏆 **Игра окончена!** Места в бункере заполнены. Выжившие:\n{survivors_str}",
                        parse_mode="Markdown"
                    )
                    game["status"] = "IDLE"
                else:
                    await bot.send_message(
                        chat_id,
                        f"🚨 По результатам голосования из бункера изгнан игрок: {kicked_name}!\n\n"
                        f"Осталось живых: {len(alive_remaining)}. Мест в бункере: {game['bunker_capacity']}.\n"
                        f"Игра продолжается!",
                        parse_mode="Markdown"
                    )
            else:
                game["status"] = "PLAYING"
                await bot.send_message(chat_id, "⚖️ Ничья при голосовании! Никто не изгнан в этом раунде. Продолжаем обсуждение.", parse_mode="Markdown")

# ================= КОМАНДА /INFO =================
@router.message(Command("info"))
async def cmd_info(message: Message):
    if message.chat.type not in ["group", "supergroup"]:
        return
    
    chat_id = message.chat.id
    game = get_chat_game(chat_id)
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: `/info @username`", parse_mode="Markdown")
        return
    
    target_username = args[1].lstrip('@')
    
    found_player = None
    for p_data in game["players"].values():
        if p_data["username"] == target_username:
            found_player = p_data
            break
            
    if not found_player:
        await message.answer("❌ Игрок не найден или не участвует в текущей игре этого чата.")
        return
        
    revealed_text = "\n".join([f"• {item}" for item in found_player["revealed"]]) if found_player["revealed"] else "Пока ничего не открыто."
    status_icon = "🟢 В игре" if found_player["is_alive"] else "🔴 Изгнан"
    await message.answer(f"📊 Информация об игроке {found_player['name']} ({status_icon}):\n{revealed_text}", parse_mode="Markdown")

# ================= ЗАПУСК =================
async def main():
    print("🤖 Бот «Бункер» запущен и готов к работе!")
    print("Поддерживается работа в нескольких чатах одновременно.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
