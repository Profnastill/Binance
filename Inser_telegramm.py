
"""
name @Rgraf_bot
This is a echo bot.
It echoes any incoming text messages.
"""
import datetime
import logging
import win32com
import balance_mod
import balance_mod
import io
#import win32clipboard as clip
import xlwings as xw
#import excel2img
from PIL import ImageGrab,Image
from aiogram import Bot, Dispatcher, types
import candle_graf_class
#from aiogram.dispatcher import FSMContext
from  aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup



API_TOKEN = '1764118035:AAFUZrAiipYSIyvfcGNAYXVWPxrBb8jXG_s'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)



# создаём форму и указываем поля
class Form(StatesGroup):
    asset = State()


def save_img1():
    book = xw.Book(r"C:\Users\Давид\PycharmProjects\Binance\data_book.xlsx")
    sheet_name = str(datetime.date.today())
    print(sheet_name)
    sht = book.sheets(sheet_name)
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


@dp.message_handler(regexp='table')
async def table_signal(message: types.Message):
    #await  bot.delete_message(message.chat.id,message_id=message.message_id)
    await message.delete()
    save_img1()
    with open('test.png', 'rb') as photo:
        await bot.send_photo(message.chat.id, photo, caption='Таблица сигнала')


@dp.message_handler(regexp='find')
async def find_asset_signal(message: types.Message):
    await  bot.send_message(message.chat.id,"Введите название инструмента")
    await Form.asset.set()

# Сюда приходит ответ с именем
@dp.message_handler(state=Form.asset)
async def process_name(message: types.Message):
    day=720
    print(message.text)
    start = candle_graf_class.graf_delta_cls(day, message.text)
    start.wk = {0: 0.4, 1: 0.45, 2: 0.15}
    start.fun_graf_delta(message.chat.values)
    signal_table = candle_graf_class.graf_delta_cls.last_signals()  # значения последних сигналов
    print(signal_table)



@dp.message_handler(commands="test1")
async def cmd_test1(message: types.Message):
    await message.reply("Проверка успешна")

@dp.message_handler(commands="balance")
async def cmd_test1(message: types.Message):
    data_tb=balance_mod.main()
    #photo = img_excel()
    await bot.send_message(data_tb)
    # await bot.send_photo(chat_id, photo)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

    #save_img1()
