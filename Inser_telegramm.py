
"""
name @Rgraf_bot
Биржевой телеграмм бот

"""
import datetime
import logging

import pandas as pd
import balance_mod
import dataframe_image as dfi# Создание картинок из таблицы


#import win32clipboard as clip
#import xlwings as xw
#import excel2img
#from PIL import ImageGrab,Image
from aiogram import Bot, Dispatcher, types
import candle_graf_class
from aiogram.dispatcher import FSMContext
from  aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage


API_TOKEN = '1764118035:AAFUZrAiipYSIyvfcGNAYXVWPxrBb8jXG_s'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp=Dispatcher(bot,storage=MemoryStorage())



# создаём форму и указываем поля
class Form(StatesGroup):
    wait_asset = State()#Состояни ожидания ввода названия

r"""
Не нужные модули для вставки таблицы из excel

def save_img1():
    book = xw.Book(r"C:\Users\Давид\PycharmProjects\Binance\data_book.xlsx")

    sheet_name = str(datetime.date.today())
    print(sheet_name)
    try:
        sht = book.sheets(sheet_name)
    except:
        None
    else:
        ret=sht.range('L1:Q35').api.CopyPicture(Format= 2)  # 2 copies as when it is printed
        print(ret)
        sht.api.Paste()
        pic = sht.pictures[0]
        pic.api.Copy()
        img = ImageGrab.grabclipboard()
        img.save('test.png')  # You can obviously save this as whatever filename you want
        pic.delete()
        print("----вставка таблицы")

def save_img1_():
    book = xw.Book(r"C:\Users\Давид\PycharmProjects\Binance\data_book.xlsx")
    sheet_name = str(datetime.date.today())
    print(sheet_name)
    sht = book.sheets(sheet_name)
    ret=sht.range('L1:Q35').api.CopyPicture(Appearance=2)  # 2 copies as when it is printed
    img = ImageGrab.grabclipboard()
    img_bytes=io.BytesIO()
    print(img)
    img.save('test.png')  # You can obviously save this as whatever filename you want
    print("----вставка таблицы")
"""

@dp.message_handler(regexp='table')
async def table_signal(message: types.Message):
    #await  bot.delete_message(message.chat.id,message_id=message.message_id)
    await message.delete()
    #save_img1()
    name="signal.png"
    with open(name, 'rb') as photo:
        await bot.send_photo(message.chat.id, photo, caption='Таблица сигнала')

@dp.message_handler(regexp='*')
async def find_asset_signal(message: types.Message):
    None



@dp.message_handler(regexp='find')
async def find_asset_signal(message: types.Message):
    await  bot.send_message(message.chat.id,"Введите название инструмента")
    await Form.wait_asset.set()


# Сюда приходит ответ с именем
@dp.message_handler(state=Form.wait_asset)
async def process_name(message: types.Message, state:FSMContext):
    await  state.update_data(asset=message.text.upper())
    data= await  state.get_data()
    print ("--",data)
    await message.delete()
    day=720
    print(message.text)

    start = candle_graf_class.graf_delta_cls(day, data["asset"])
    start.wk = {0: 0.4, 1: 0.45, 2: 0.15}
    start.fun_graf_delta(data["asset"])
    signal_table = candle_graf_class.graf_delta_cls.last_signals()  # значения последних сигналов
    print("---")
    print(signal_table)
    signal_table.reset_index(inplace=True,drop=True)
    signal_table=signal_table.style

    dfi.export(signal_table,"take_signal.png")
    with open('take_signal.png', 'rb') as photo:
        await bot.send_photo(message.chat.id, photo, caption='Значение сигнала')

    await state.reset_state(with_data=True)
    await state.finish()# Завершаем состояние

@dp.message_handler(commands="test1")
async def cmd_test1(message: types.Message):
    print("test1")
    await message.reply("Проверка успешна")

@dp.message_handler(regexp="balance")
async def cmd_test2(message: types.Message):
    """Функция вставки баланса в телегу"""
    cl_data=balance_mod.fun_1(balance_mod.table)# Создаем класс для расчета баланса
    data_tb=cl_data.table
    data_tb:pd.DataFrame
    data_tb2=cl_data._balance()#Вытаскиваем баланс
    print(data_tb)
    dtb_style=data_tb.style.background_gradient()
    dtb_style2=data_tb2.style.background_gradient()
    dfi.export(dtb_style,"balance.png")
    dfi.export(dtb_style2, "balance2.png")
    with open('balance.png', 'rb') as photo:
        await bot.send_photo(message.chat.id, photo, caption='Баланс')
    with open('balance2.png', 'rb') as photo:
        await bot.send_photo(message.chat.id, photo, caption='Баланс суммарный')

    # await bot.send_photo(chat_id, photo)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

    #save_img1()
