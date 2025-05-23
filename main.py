print("Запуск main.py...")

import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import Message
from strategies import analyze_all_strategies
from utils import is_volatile, calculate_volatility, get_signal_history_text, get_education_text, get_bot_info_text
from tradingview_ta import TA_Handler, Interval
from datetime import datetime

API_TOKEN = "8162392833:AAHFd_ywFuZ-3RD-JppxId64oJgFMticBE0"

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()

user_pair = {}
user_timeframe = {}
signal_history = []
min_reliability_threshold = 50
volatility_filter = set()

main_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="🚀Сигнал🚀")],
        [types.KeyboardButton(text="Выбрать валюту"), types.KeyboardButton(text="Таймфрейм")],
        [types.KeyboardButton(text="История"), types.KeyboardButton(text="Обучение")],
        [types.KeyboardButton(text="Волатильность"), types.KeyboardButton(text="Надёжность")],
        [types.KeyboardButton(text="Анализатор В/П"), types.KeyboardButton(text="Автопоиск лучшего момента")],
        [types.KeyboardButton(text="ℹ️ Информация"), types.KeyboardButton(text="⚙️ Настройки")]
    ],
    resize_keyboard=True
)

pair_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="EURUSD"), types.KeyboardButton(text="GBPUSD")],
        [types.KeyboardButton(text="USDJPY"), types.KeyboardButton(text="AUDUSD")],
        [types.KeyboardButton(text="EURJPY"), types.KeyboardButton(text="OTC:EURUSD")],
        [types.KeyboardButton(text="OTC:GBPUSD")]
    ],
    resize_keyboard=True
)

timeframe_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="1m"), types.KeyboardButton(text="5m"), types.KeyboardButton(text="15m")]
    ],
    resize_keyboard=True
)

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот для поиска лучших торговых сигналов.\nВыберите действие:", reply_markup=main_keyboard)

@router.message(lambda m: m.text == "Выбрать валюту")
async def select_currency_button(message: Message):
    await message.answer("Выберите валютную пару:", reply_markup=pair_keyboard)

@router.message(lambda m: m.text in ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY", "OTC:EURUSD", "OTC:GBPUSD"])
async def select_pair(message: Message):
    user_pair[message.chat.id] = message.text
    await message.answer(f"Вы выбрали валютную пару: {message.text}", reply_markup=main_keyboard)

@router.message(lambda m: m.text == "Таймфрейм")
async def select_timeframe_button(message: Message):
    await message.answer("Выберите таймфрейм:", reply_markup=timeframe_keyboard)

@router.message(lambda m: m.text in ["1m", "5m", "15m"])
async def select_tf(message: Message):
    user_timeframe[message.chat.id] = message.text
    await message.answer(f"Вы выбрали таймфрейм: {message.text}", reply_markup=main_keyboard)

@router.message(lambda m: m.text == "🚀Сигнал🚀")
async def cmd_signal(message: Message):
    pair = user_pair.get(message.chat.id, "EURUSD")
    tf = user_timeframe.get(message.chat.id, "1m")

    await message.answer("Ищу лучший момент для входа, подождите...")

    try:
        interval_map = {
            "1m": Interval.INTERVAL_1_MINUTE,
            "5m": Interval.INTERVAL_5_MINUTES,
            "15m": Interval.INTERVAL_15_MINUTES
        }

        handler = TA_Handler(
            symbol=pair.replace("OTC:", ""),
            screener="forex",
            exchange="FX_IDC",
            interval=interval_map.get(tf, Interval.INTERVAL_1_MINUTE)
        )

        analysis = handler.get_analysis()

        if message.chat.id in volatility_filter and not is_volatile(analysis):
            await message.answer("Рынок недостаточно волатилен для торговли. Попробуйте позже.")
            return

        decision, match_count, details = analyze_all_strategies(analysis)

        if decision != "none" and (match_count * 10) >= min_reliability_threshold:
            now = datetime.now().strftime("%d.%m.%Y %H:%M")
            signal_text = (
                f"<b>Направление:</b> {'Покупка (вверх)' if decision == 'buy' else 'Продажа (вниз)'}\n"
                f"<b>Надёжность сигнала:</b> {match_count * 10}%\n"
                f"<b>Валютная пара:</b> {pair}\n"
                f"<b>Таймфрейм:</b> {tf}\n"
                f"<b>Совпавшие стратегии:</b> {details}\n"
                f"<b>Время сигнала:</b> {now}"
            )
            await message.answer(signal_text)
            signal_history.append((pair, tf, decision, "ожидается результат"))
        else:
            await message.answer("Сейчас нет подходящего сигнала. Подождите немного и попробуйте снова.")

    except Exception as e:
        logging.error(f"Ошибка в команде сигнала: {e}")
        await message.answer("Произошла ошибка при анализе сигнала.")

@router.message(lambda m: m.text == "История")
async def cmd_history(message: Message):
    text = get_signal_history_text(signal_history)
    await message.answer(text)

@router.message(lambda m: m.text == "Обучение")
async def cmd_education(message: Message):
    await message.answer(get_education_text())

@router.message(lambda m: m.text == "ℹ️ Информация")
async def cmd_info(message: Message):
    await message.answer(get_bot_info_text())

@router.message(lambda m: m.text == "Волатильность")
async def toggle_volatility_filter(message: Message):
    if message.chat.id in volatility_filter:
        volatility_filter.remove(message.chat.id)
        await message.answer("Фильтр по волатильности выключен.")
    else:
        volatility_filter.add(message.chat.id)
        await message.answer("Фильтр по волатильности включён.")

@router.message(lambda m: m.text == "Надёжность")
async def adjust_reliability(message: Message):
    global min_reliability_threshold
    min_reliability_threshold = (min_reliability_threshold + 10) % 110
    await message.answer(f"Минимальная надёжность сигнала теперь: {min_reliability_threshold}%")

@router.message(lambda m: m.text == "Анализатор В/П")
async def vp_analyzer(message: Message):
    await message.answer("Функция анализа валютной пары пока в разработке.")

@router.message(lambda m: m.text == "Автопоиск лучшего момента")
async def auto_entry(message: Message):
    await message.answer("Функция автопоиска лучшего момента пока в разработке.")

@router.message(lambda m: m.text == "⚙️ Настройки")
async def settings(message: Message):
    await message.answer("Настройки пока в разработке.")

async def remove_webhook():
    await bot.delete_webhook(drop_pending_updates=True)
    print("Webhook успешно удалён")

async def main():
    logging.basicConfig(level=logging.INFO)
    await remove_webhook()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
