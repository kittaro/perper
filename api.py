import telebot

TOKEN = '1172054191:AAGvD0PA_F2BFcExfhNbnbq5r1FBQVHjCdQ'  #Токен бота
CHANNEL_ID = '@sassybaka1488'  #ID канала

bot = telebot.TeleBot(TOKEN)

while True:
    message = input ()
    #("Текст сообщения: ")
    image_path = input ()
    #("Путь к изображению ('skip' для пропуска): ")

    if image_path.lower() != 'skip':
        with open(image_path, 'rb') as photo:
            bot.send_photo(CHANNEL_ID, photo, caption=message)
    else:
        bot.send_message(CHANNEL_ID, message)
