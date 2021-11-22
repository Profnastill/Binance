"""
name @Rgraf_bot
Биржевой телеграмм бот

"""
import logging
from datetime import date, timedelta
import dataframe_image as dfi  # Создание картинок из таблицы
import pandas as pd
# import win32clipboard as clip
import xlwings as xw
# import excel2img
# from PIL import ImageGrab,Image
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

import balance_mod
import candle_graf_class

API_TOKEN = '1764118035:AAFUZrAiipYSIyvfcGNAYXVWPxrBb8jXG_s'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp = Dispatcher(bot, storage=MemoryStorage())


# создаём форму и указываем поля
class Form(StatesGroup):
    wait_asset = State()  # Состояни ожидания ввода названия


@dp.message_handler(regexp='table_old')
async def table_signal(message: types.Message):
    # await  bot.delete_message(message.chat.id,message_id=message.message_id)
    await message.delete()
    # save_img1()
    name = "signal.png"
    with open(name, 'rb') as photo:
        await bot.send_photo(message.chat.id, photo, caption='Таблица сигнала')


async def main(data, message):
    """
    Функия запуска поиска с указанными параметрами
    :param data:
    :param message:
    :return:
    """

    id = message.chat.id
    print()
    day = 720
    print(message.text)
    message.delete()
    data = data.upper()
    start = candle_graf_class.graf_delta_cls(day, data)
    candle_graf_class.graf_delta_cls.__tcur_time = date.today()
    # start.wk = {0: 0.4, 1: 0.45, 2: 0.15}# Можно изменить веса по желанию
    start.fun_graf_delta(data)
    signal_table = candle_graf_class.graf_delta_cls.last_signals()  # значения последних сигналов
    print("---")
    print(signal_table)
    signal_table.reset_index(inplace=True, drop=True)
    if len(signal_table) > 0:
        signal_table = signal_table.style
        dfi.export(signal_table, "picture/take_table_signal.png")
        with open('picture/take_table_signal.png', 'rb') as photo:
            await bot.send_photo(message.chat.id, photo, caption='Значение сигнала')
    else:
        await bot.send_message(id, "Инструмент не найден")

async def get_help(message):
    await bot.send_message(message.chat.id,"BOT COMMAND HELP \n table_all= Поиск по портфель \n table_all1 =Поиск по Портфель2 \n find tiker= поиск по названию инструмента")


async def main_get_table(message, portfel):
    """
    Функия запуска поиска с указанными параметрами всей таблицы
    :return:
    """
    xlbook = xw.Book(r"C:\Users\Давид\PycharmProjects\Binance\data_book.xlsx")
    sheet = xlbook.sheets(portfel)
    table = sheet.range('A1').options(pd.DataFrame, expand='table', index=False).value

    # tableable = table[0:2]
    # ВНИМАНИЕ! строкой ниже Биток должен быть всегда первыми иначе фильтр работать не будет
    base_table = pd.DataFrame(
        {'asset': ["RTSI.ME", 'BTC', 'DX-Y.NYB', "GC=F", 'BZ=F', 'RUB=X']})  # добавляем базовые значения
    table: pd.DataFrame = pd.concat([base_table, table], ignore_index=True,
                                    sort=False)  # Добавляем базовые инструменты для сравнения
    table.drop_duplicates(subset=['asset'], inplace=True)  # Удаляем дублирования инструментов
    day = 720  # Дни поиска
    # table = table[0:3]
    for asset in table['asset']:
        start = candle_graf_class.graf_delta_cls(day, asset)
        candle_graf_class.graf_delta_cls.__tcur_time = date.today()
        # start.wk = {0: 0.4, 1: 0.45, 2: 0.15}
        start.wk = {0: 0.25, 1: 0.4, 2: 0.35}
        start.fun_graf_delta(asset)
        signal_table = start.last_signals()
        signal_table.drop_duplicates(subset=['asset'], inplace=True)
        signal_table = signal_table.reset_index(drop=True)

    if len(signal_table) > 0:
        signal_table = signal_table.style
        dfi.export(signal_table, f"picture/take_signal_{portfel}.png")
        with open(f"picture/take_signal_{portfel}.png", 'rb') as photo:
            await bot.send_photo(message.chat.id, photo, caption='Значение сигнала')
    else:
        await bot.send_message(id, "Инструмент не найден")
    del (table)
    del (signal_table)
    candle_graf_class.data_save = candle_graf_class.data_tb_save_cls()  # Перегружаем память для очистки прошлой таблицы


@dp.message_handler()
async def find_asset_signal(message: types.Message):
    # await bot.send_message(message.from_user.id, message.text)
    """ Отслеживает все команды"""
    # message.text.upper()
    text_msg = message.text.split()
    print("----" * 10, text_msg)

    if text_msg[0].upper() == "FIND" and len(text_msg) >= 2:
        data = text_msg[1].upper()
        await main(data, message)
    elif text_msg[0].upper() == "TABLE_ALL":
        await main_get_table(message, 'Портфель')
    elif text_msg[0].upper() == "TABLE_ALL1":
        await main_get_table(message, 'Портфель2')
    elif text_msg[0].upper() == "HELP":
        await get_help(message)
    else:
        return


@dp.message_handler(regexp='find')
async def find_asset_signal(message: types.Message):
    """стырый вариант через форму"""
    await  bot.send_message(message.chat.id, "Введите название инструмента")
    await Form.wait_asset.set()


# Сюда приходит ответ с именем
@dp.message_handler(state=Form.wait_asset)
async def process_name(message: types.Message, state: FSMContext):
    await  state.update_data(asset=message.text.upper())
    data = await  state.get_data()
    print("--", data)
    message = data['asset']
    await main(data, message)
    await message.delete()
    await state.reset_state(with_data=True)
    await state.finish()  # Завершаем состояние


@dp.message_handler(commands="test1")
async def cmd_test1(message: types.Message):
    print("test1")
    await message.reply("Проверка успешна")


@dp.message_handler(regexp="balance")
async def cmd_test2(message: types.Message):
    """Функция вставки баланса в телегу"""
    cl_data = balance_mod.fun_1(balance_mod.table)  # Создаем класс для расчета баланса
    data_tb = cl_data.table
    data_tb: pd.DataFrame
    data_tb2 = cl_data._balance()  # Вытаскиваем баланс
    print(data_tb)
    dtb_style = data_tb.style.background_gradient()
    dtb_style2 = data_tb2.style.background_gradient()
    dfi.export(dtb_style, "picture/balance.png")
    dfi.export(dtb_style2, "picture/balance2.png")
    with open('picture/balance.png', 'rb') as photo:
        await bot.send_photo(message.chat.id, photo, caption='Баланс')
    with open('picture/balance2.png', 'rb') as photo:
        await bot.send_photo(message.chat.id, photo, caption='Баланс суммарный')

    # await bot.send_photo(chat_id, photo)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

    # save_img1()
