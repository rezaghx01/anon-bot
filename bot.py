from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.client.default import DefaultBotProperties
import asyncio

from database import init_db, is_blocked, block_user, save_message

# ⚙️ اطلاعات مهم
BOT_TOKEN = '8099162599:AAF30ait9DyHr0xYrWSV5uyN9Gi8vfV1sYg'
ADMIN_ID = 5845195008

# ساخت Bot
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# ساخت Dispatcher بدون bot (در Aiogram 3.7+)
dp = Dispatcher()

# شروع دیتابیس
init_db()

print("✅ ربات راه‌اندازی شد (Bot object ساخته شد)")

@dp.message(Command("mylink"))
async def send_invite_link(message: Message):
    user = message.from_user
    user_name = user.first_name or "User"
    bot_info = await bot.get_me()
    invite_link = f"https://t.me/{bot_info.username}?start={user_name}_{user.id}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📨 ارسال پیام ناشناس", url=invite_link)
        ]
    ])

    await message.answer(
        f"🔗 <b>لینک اختصاصی تو ساخته شد!</b>\n\n"
        f"از طریق این دکمه، بقیه می‌تونن ناشناس برات پیام بفرستن:",
        reply_markup=kb,
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("help"))
async def show_help(message: Message):
    await message.answer(
        "❓ <b>راهنمای ربات پیام ناشناس</b>\n\n"
        "🔹 /mylink — دریافت لینک اختصاصی برای دریافت پیام ناشناس\n"
        "🔹 فقط یه پیام بفرست تا بره برای علی یا کسی که لینک مخصوصشه.\n"
        "🔹 علی می‌تونه بهت ناشناس جواب بده یا بلاکت کنه.\n\n"
        "✨ با خیال راحت پیام بفرست، هیچ‌کس نمی‌فهمه کی هستی!",
        parse_mode=ParseMode.HTML
    )

@dp.message(CommandStart(deep_link=True))
async def start_with_param(message: Message, command: CommandStart):
    name = command.args or "Ali"
    print(f"👤 {message.from_user.full_name} وارد شد با پارامتر: {name}")
    await message.answer(
        f"سلام 😊\n"
        f"تو داری یه پیام ناشناس برای <b>{name}</b> می‌فرستی.\n"
        f"بدون اینکه هویتت مشخص بشه، هرچی دوست داری بنویس!\n\n"
        f"📩 فقط یه پیام بفرست تا {name} ببینه."
    )

@dp.message(CommandStart())
async def start_default(message: Message):
    print(f"👤 {message.from_user.full_name} استارت زد (بدون پارامتر)")
    await message.answer(
        "سلام 😊\n"
        "تو داری یه پیام ناشناس برای <b>Ali</b> می‌فرستی.\n"
        "بدون اینکه هویتت مشخص بشه، هرچی دوست داری بنویس!\n\n"
        "📩 فقط یه پیام بفرست تا علی ببینه."
    )

@dp.message()
async def anonymous_message(message: Message):
    user = message.from_user
    print(f"📩 پیام جدید از {user.full_name} ({user.id}): {message.text}")

    if is_blocked(user.id):
        print(f"⛔️ کاربر {user.id} بلاک شده بود")
        await message.answer("❌ متأسفم، شما بلاک شدی و نمی‌تونی پیام بدی.")
        return

    save_message(user.id, message.text)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📤 پاسخ", callback_data=f"reply:{user.id}"),
            InlineKeyboardButton(text="🚫 بلاک", callback_data=f"block:{user.id}")
        ]
    ])

    text_to_admin = (
        f"📨 <b>پیام جدید:</b>\n\n"
        f"<b>👤 نام:</b> {user.full_name}\n"
        f"<b>🆔 آیدی عددی:</b> <code>{user.id}</code>\n"
        f"<b>🔗 یوزرنیم:</b> @{user.username if user.username else 'ندارد'}\n\n"
        f"<b>💬 متن پیام:</b>\n{message.text}"
    )

    await bot.send_message(chat_id=ADMIN_ID, text=text_to_admin, reply_markup=kb)
    await message.answer("✅ پیامت با موفقیت ارسال شد.")

@dp.callback_query()
async def handle_callback(query: types.CallbackQuery):
    data = query.data
    print(f"⚙️ دریافت callback: {data}")
    if data.startswith("block:"):
        user_id = int(data.split(":")[1])
        block_user(user_id)
        await query.answer("❌ کاربر بلاک شد.")
        await query.message.edit_text(query.message.text + "\n\n🚫 <b>این کاربر بلاک شد.</b>")
    elif data.startswith("reply:"):
        user_id = int(data.split(":")[1])
        await query.message.answer(f"✏️ پاسخ خودت به این کاربر رو بنویس (آیدی: <code>{user_id}</code>)")
        dp.message.register(reply_to_user, user_id=user_id)
        await query.answer("📝 منتظر پیام شما هستم...")

async def reply_to_user(message: Message, user_id: int):
    await bot.send_message(chat_id=user_id, text=f"📩 پاسخ ناشناس از علی:\n\n{message.text}")
    await message.answer("✅ پاسخ با موفقیت ارسال شد.")

# اجرای ربات
async def main():
    print("📡 شروع polling... منتظر پیام‌ها هستم")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
