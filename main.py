import requests
import telebot
from telebot import types
from config import TOKEN


amount = 0
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    global amount
    amount = 0
    bot.send_message(message.chat.id, 'Привет! Я бот для конвертации валют. Введите сумму для конвертации:\n')
    bot.register_next_step_handler(message, selection)

def selection(message):
    global amount
    try:
        amount = float(message.text.strip())
    except ValueError:    
        bot.send_message(message.chat.id, 'Вы ввели некорректные данные.\n Попробуйте еще раз.')
        bot.register_next_step_handler(message, selection)
        return
    
    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_1 = types.InlineKeyboardButton('USD/RUB', callback_data='USD/RUB')
        btn_2 = types.InlineKeyboardButton('EUR/USD', callback_data='EUR/USD')
        btn_3 = types.InlineKeyboardButton('CNY/USD', callback_data='CNY/USD')
        btn_4 = types.InlineKeyboardButton('Cвоё значение', callback_data='else')
        markup.add(btn_1, btn_2, btn_3, btn_4)
        bot.send_message(message.chat.id, 'Выберите валюту:', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Вы ввели некорректные данные.\n Попробуйте еще раз.')
        bot.register_next_step_handler(message, selection)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global amount
    if call.data != 'else':
        quote, base  = call.data.upper().split('/')
        url = f'https://min-api.cryptocompare.com/data/price?fsym={quote}&tsyms={base}'
        response = requests.get(url)
        data = response.json()
        rate  = data[base]
        res = amount * rate
        bot.send_message(call.message.chat.id, f'{amount} {quote} = {round(res, 2)} {base}')
        bot.send_message(call.message.chat.id, 'Введите сумму для конвертации:\n')
        bot.register_next_step_handler(call.message, selection)
    else:
        bot.send_message(call.message.chat.id, f'Введите желаемую валюту через /:')
        bot.register_next_step_handler(call.message, my_cur)

def my_cur(message):
    global amount
    try:
        quote, base  = message.text.upper().split('/')
    except ValueError as ex:
        bot.send_message(message.chat.id, f'Такой валюты нет.\n Попробуйте еще раз.\n{ex}')
        bot.register_next_step_handler(message, my_cur)
        return
    try:         
        url = f'https://min-api.cryptocompare.com/data/price?fsym={quote}&tsyms={base}'
        response = requests.get(url)
        data = response.json()
        rate  = data[base]
    except KeyError as ex:  
        bot.send_message(message.chat.id, f'Такой валюты нет.\n Попробуйте еще раз.\n{ex}')
        bot.register_next_step_handler(message, my_cur)
        return 
    res = amount * rate
    bot.send_message(message.chat.id, f'{amount} {quote} = {round(res, 2)} {base}')
    bot.send_message(message.chat.id, 'Введите сумму для конвертации:\n')
    bot.register_next_step_handler(message, selection)

bot.polling()
