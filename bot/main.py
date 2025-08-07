import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8482163056:AAGYMcCmHUxvrzDXkBESZPGV_kGiUVHZh4I")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://64023b94ce51.ngrok-free.app")

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class UserState(StatesGroup):
    waiting_for_profile = State()

@dp.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    """Handle /start command"""
    user = message.from_user
    
    # Create web app button
    webapp = WebAppInfo(url=WEBAPP_URL)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Открыть приложение", web_app=webapp)]
        ]
    )
    
    welcome_text = f"""
👋 Привет, {user.first_name}!

Добро пожаловать в Social Rent - социальную сеть для поиска жилья и соседей!

🔍 Здесь вы можете:
• Создать профиль с вашими предпочтениями
• Найти людей, ищущих жилье в том же районе
• Лайкать профили и находить соседей
• Просматривать понравившиеся объявления вместе
• Общаться с подходящими кандидатами

Нажмите кнопку ниже, чтобы начать!
    """
    
    await message.answer(
        welcome_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.message(Command("help"))
async def help_command(message: Message):
    """Handle /help command"""
    help_text = """
🆘 <b>Помощь по использованию Social Rent</b>

<b>Основные функции:</b>
1️⃣ <b>Создание профиля</b> - укажите ваши предпочтения по жилью
2️⃣ <b>Поиск соседей</b> - находите людей с пересекающимися зонами поиска  
3️⃣ <b>Система лайков</b> - лайкайте понравившиеся профили
4️⃣ <b>Матчи</b> - при взаимных лайках откроется контакт для общения
5️⃣ <b>Просмотр объявлений</b> - смотрите что нравится вашим матчам

<b>Команды бота:</b>
/start - открыть приложение
/help - показать эту справку
/profile - быстрый доступ к профилю

<b>Как это работает:</b>
• Вы указываете станцию метро и радиус поиска
• Система находит людей, чьи зоны поиска пересекаются с вашей
• При взаимных лайках вы получаете контакт для общения в Telegram
• Можете просматривать какие объявления понравились вашим матчам
    """
    
    await message.answer(help_text, parse_mode="HTML")

@dp.message(Command("profile"))
async def profile_command(message: Message):
    """Quick access to profile"""
    webapp = WebAppInfo(url=f"{WEBAPP_URL}#/profile")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 Мой профиль", web_app=webapp)]
        ]
    )
    
    await message.answer(
        "👤 Нажмите кнопку ниже для редактирования профиля:",
        reply_markup=keyboard
    )

@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    """Handle data from web app"""
    try:
        data = json.loads(message.web_app_data.data)
        
        if data.get("type") == "profile_updated":
            await message.answer("✅ Профиль успешно обновлен!")
        elif data.get("type") == "match_found":
            match_user = data.get("user", {})
            await message.answer(
                f"🎉 У вас новый матч!\n"
                f"Пользователь: {match_user.get('first_name', 'Новый пользователь')}\n"
                f"Теперь вы можете общаться!"
            )
        elif data.get("type") == "contact_request":
            await message.answer("📞 Контактные данные переданы в приложение")
        
    except json.JSONDecodeError:
        logger.error(f"Invalid web app data: {message.web_app_data.data}")
        await message.answer("❌ Произошла ошибка при обработке данных")

@dp.message()
async def handle_other_messages(message: Message):
    """Handle other messages"""
    webapp = WebAppInfo(url=WEBAPP_URL)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Открыть приложение", web_app=webapp)]
        ]
    )
    
    await message.answer(
        "Для использования Social Rent откройте веб-приложение:",
        reply_markup=keyboard
    )

async def main():
    """Main function"""
    logger.info("Starting Social Rent bot...")
    
    # Delete webhook to use polling
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")