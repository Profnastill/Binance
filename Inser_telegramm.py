
"""
This is a echo bot.
It echoes any incoming text messages.
"""
import datetime
import logging
import excel2img as eximg
#import portfel_risk_balncer
from datetime import date, timedelta



from aiogram import Bot, Dispatcher, executor, types


API_TOKEN = '1764118035:AAFUZrAiipYSIyvfcGNAYXVWPxrBb8jXG_s'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def img_excel():
    r"C:\Users\Давид\PycharmProjects\Binance\data_book.xlsx"
    sheet_name= str(datetime.date.today())


    path=r"C:\Users\Давид\PycharmProjects\Binance\image.png"
    eximg.export_img(r"C:\Users\Давид\PycharmProjects\Binance\data_book.xlsx", path, "rrr","L1:Q27")
    photo = open(path, 'rb')
    return photo

@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    with open('data/cats.jpg', 'rb') as photo:
        await bot.send_photo(message.chat.id, photo, caption='Cats is here 😺',
                             reply_to_message_id=message.message_id)

'''''''''
@dp.message_handler()
async def echo(message: types.Message):
    await bot.send_message(message.chat.id, message.text)
'''''
@dp.message_handler(commands="test1")
async def cmd_test1(message: types.Message):
    await message.reply("Test 1")

@dp.message_handler(commands="balance")
async def cmd_test1(message: types.Message):
    #data_tb=portfel_risk_balncer.main()
    photo=img_excel()
    await message.reply(photo)
    #await bot.send_photo(chat_id, photo)




async def cmd_test2(message: types.Message):
    await message.reply("Test 211")


dp.register_message_handler(cmd_test2, commands="п")

if __name__ == '__main__':
    #executor.start_polling(dp, skip_updates=True)
    img_excel()
