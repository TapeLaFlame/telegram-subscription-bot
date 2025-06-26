from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '7831542057:AAErIly1j1xHja_aghLjcpsXH-ixKd59kvw'
ADMIN_ID = None  # ← ВСТАВЬ СЮДА СВОЙ Telegram ID (узнай через @userinfobot)
INVITE_LINK = 'https://t.me/+zsgGJIeNG6wwZmIy'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
user_data = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Подписка 5€ (1 мес)", callback_data="subscribe_5")
    )
    await message.answer("👋 Добро пожаловать!
Выберите тип подписки:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('subscribe'))
async def choose_subscription(callback: types.CallbackQuery):
    amount = callback.data.split('_')[1]
    user_data[callback.from_user.id] = amount
    text = (
        f"💳 Оплатите {amount}€ на карту:

"
        "Карта: 5354 5612 5103 8586

"
        "После оплаты пришлите скриншот или 4 последние цифры карты."
    )
    await callback.message.answer(text)

@dp.message_handler(content_types=['photo', 'text'])
async def handle_payment_proof(message: types.Message):
    amount = user_data.get(message.from_user.id, 'неизвестно')
    user = message.from_user

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            f"✅ Подтвердить {user.first_name} (ID {user.id})",
            callback_data=f"approve_{user.id}"
        )
    )

    caption = (
        f"💰 Пользователь @{user.username or user.first_name} оплатил подписку ({amount}€)
"
        f"🆔 ID: {user.id}"
    )

    if message.content_type == 'photo':
        await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=caption, reply_markup=keyboard)
    else:
        await bot.send_message(chat_id=ADMIN_ID, text=caption + f"
📩 Сообщение: {message.text}", reply_markup=keyboard)

    await message.reply("✅ Спасибо! Заявка на оплату отправлена. Ожидайте подтверждения.")

@dp.callback_query_handler(lambda c: c.data.startswith('approve_'))
async def approve_payment(callback: types.CallbackQuery):
    user_id = int(callback.data.split('_')[1])
    await bot.send_message(user_id, f"✅ Оплата подтверждена!
Вот ссылка на канал: {INVITE_LINK}")
    await callback.answer("Пользователю выслана ссылка.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
