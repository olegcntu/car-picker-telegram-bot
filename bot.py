import os
from telebot import *
from rules import *
import psycopg2 as ps
from psycopg2 import Error

terms = [-1, -1, -1, -1, -1]
N = 0
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))
username = "noname"
try:
    connection = ps.connect(user="postgres", password=os.getenv("DB_PASSWORD"), host="127.0.0.1", port="5432", database="cars")
    cursor = connection.cursor()
except (Exception, Error) as error:
    print("Error!!! Cannot connect to PostgreSQL", error)


@bot.message_handler(commands=['start'])
def start(message):
    mess = 'Привіт, ' + message.from_user.first_name + '! Ну що, нумо підбирати тобі круту тачку? ' \
                                                       'Якщо готовий, то натискай на /quiz 😎'
    bot.send_message(message.chat.id, mess.format(message.from_user.first_name))


@bot.message_handler(commands=['help'])
def send_help(message):
    mess = "Якщо хочеш пройти тестування - клікай на /quiz, якщо тобі треба переглянути результати - " \
           "/results 😉"
    bot.send_message(message.chat.id, mess)


@bot.message_handler(commands=['quiz'])
def quiz(message):
    global terms
    terms = [-1, -1, -1, -1, -1]
    global N
    global username
    username = message.from_user.first_name
    N = 0
    question(message)


def question(message):
    if N == 0:
        mess = "Ви взагалі знайомі з ПДР?"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Що таке ПДР?", callback_data='quiz_0'))
        markup.add(types.InlineKeyboardButton("Зробимо вигляд, що так", callback_data='quiz_1'))
        bot.send_message(message.chat.id, mess, reply_markup=markup)
    if N == 1:
        mess = "Оцініть наскільки Вам важливий зовнішній вигляд автомобіля від 0 до 5. " \
               "0 – мені все одно, головне щоб їздила, 5 – машина повинна виглядати круто, щоб всі заздрили!"
        bot.send_message(message.chat.id, mess)
        bot.register_next_step_handler(message, get_answer)
    if N == 2:
        mess = "Оцініть наскільки Ви спокійний водій від 0 до 5. " \
               "0 – дуже спокійний та акуратний, 5 – я агресивний та люблю швидкість!"
        bot.send_message(message.chat.id, mess)
        bot.register_next_step_handler(message, get_answer)
    if N == 3:
        mess = "Скільки Ви готові платити за ремонт машини? Оцініть від 0 до 5. " \
               "0 – на ремонт грошей нема, 5 – для моєї крихітки нічого не шкода!"
        bot.send_message(message.chat.id, mess)
        bot.register_next_step_handler(message, get_answer)
    if N == 4:
        mess = "І останнє питання… розмір має значення?"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Так", callback_data='quiz_yes'))
        markup.add(types.InlineKeyboardButton("Ні", callback_data='quiz_no'))
        bot.send_message(message.chat.id, mess, reply_markup=markup)


def get_answer(message):
    global terms
    global N
    txt = str(message.text.lower())
    if not txt.isnumeric():
        print("error input =", message.text)
        bot.send_message(message.chat.id, 'Відповідь повинна бути цілим числом від 0 до 5.')
        bot.register_next_step_handler(message, get_answer)
        return
    term = int(txt)
    print(N, 'question:', term)
    if 0 < term > 10:
        print("error input =", message.text)
        bot.send_message(message.chat.id, 'Відповідь повинна бути цілим числом від 0 до 5.')
        bot.register_next_step_handler(message, get_answer)
    else:
        terms[N] = term
        N += 1
        question(message)


@bot.message_handler(commands=['results'])
def results(message):
    global username
    username = message.from_user.first_name
    car_im = 'error.png'
    mess = "Твій результат:\n\n"
    try:
        global cursor
        cursor.execute("select * from quiz where chat_id = %s and user_name = %s order by id desc limit 1",
                       (message.chat.id, username))
        for data in cursor:
            if data[3] == 0:
                mess += 'Знання ПДР: відсутнє\n'
            else:
                mess += 'Знання ПДР: щось знаєш\n'
            mess += 'Бажання випендрюватися тачкою - ' + str(data[4])
            mess += '\nРівень урівноваженості - ' + str(data[5])
            mess += '\nНаявність грошей - ' + str(data[6])
            if data[7] == 0:
                mess += '\nРозмір не має значення\n'
            else:
                mess += '\nРозмір має значення\n'
            mess += '\nОцінка - ' + str(data[8])
            mess += '\n' + get_car_description(str(data[9]))
            car_im = str(data[9])
            if car_im == 'BM' or car_im == 'BX':
                car_im += '.png'
            else:
                car_im += '.jpg'
        photo = open(car_im, 'rb')
        connection.commit()
        bot.send_message(message.chat.id, mess)
        bot.send_photo(message.chat.id, photo)
    except (Exception, Error) as error:
        print("Error!!! Cannot connect to PostgreSQL", error)


def get_car_description(car):
    result = ''
    if car == 'TS':
        result = 'Маленька іграшкова машинка 😎'
    elif car == 'TB':
        result = 'Велика іграшкова машинка 😎'
    elif car == 'RL':
        result = 'Renault Logan 😎'
    elif car == 'RS':
        result = 'Renault Sandero 😎'
    elif car == 'BM':
        result = 'BMW M5 😎'
    elif car == 'BX':
        result = 'BMW X5 😎'
    elif car == 'AMG':
        result = 'Mercedes-Benz AMG 😎'
    elif car == 'GLE':
        result = 'Mercedes-Benz GLE 😎'
    elif car == 'MA':
        result = 'Maserati 😎'
    elif car == 'LM':
        result = 'Lamborghini Urus 😎'
    return result


def register_answers(message):
    fs.set_variable('x1', terms[0])
    fs.set_variable('x2', terms[1])
    fs.set_variable('x3', terms[2])
    fs.set_variable('x4', terms[3])
    fs.set_variable('x5', terms[4])
    m = fs.Mamdani_inference()
    y = m.get('y')
    print('y mamdani =', y)
    car = get_car(y)
    print("car = ", car)
    try:
        global cursor
        chat_id = message.chat.id
        insert_q = """ insert into quiz (chat_id, user_name, x1, x2, x3, x4, x5, y, car) 
                            values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(insert_q, (chat_id, username, terms[0], terms[1], terms[2], terms[3], terms[4], y, car))
        connection.commit()
    except (Exception, Error) as error:
        print("Error!!! Cannot connect to PostgreSQL", error)

    car_im = car
    if car_im == 'BM' or car_im == 'BX':
        car_im += '.png'
    else:
        car_im += '.jpg'
    photo = open(car_im, 'rb')
    mess = "Результат опитування: " + str(y) + "\n" + get_car_description(
        car) + "\nПочинай збирати $ на цю крихітку  😎"
    bot.send_message(message.chat.id, mess)
    bot.send_photo(message.chat.id, photo)


@bot.callback_query_handler(func=lambda m: True)
def callback_handler(call):
    print('callback_handler {0}'.format(call))
    bot.answer_callback_query(callback_query_id=call.id)
    global terms
    global N
    if call.data == 'quiz_0':
        terms[0] = 0
        print("rules = 0")
        N += 1
        question(call.message)
    elif call.data == 'quiz_1':
        terms[0] = 1
        print("rules = 1")
        N += 1
        question(call.message)
    elif call.data == 'quiz_yes':
        terms[4] = 1
        print("size = 1")
        N += 1
        register_answers(call.message)
    elif call.data == 'quiz_no':
        terms[4] = 0
        print("size = 0")
        N += 1
        register_answers(call.message)
    else:
        print('callback_handler else {0}'.format(call.data))


bot.polling(none_stop=True)
