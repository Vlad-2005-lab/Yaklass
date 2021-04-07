# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import datetime
import schedule
import threading
import telebot
from emoji import emojize
from datetime import timezone
from telebot import types
from telebot.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import yadisk
from data.users import User
from data import db_session
import time
from static import *
import pytz
import random

history = True
bot = telebot.TeleBot(open("static/token.txt", mode="r", encoding="utf-8").read())
yandex_disk = yadisk.YaDisk(token=str(open("static/yandex_disk_token.txt", mode="r", encoding="utf-8").read()))
try:
    yandex_disk.download("users.sqlite", "db/users.sqlite")
except Exception:
    yandex_disk.upload("db/users.sqlite", "users.sqlite")
db_session.global_init("db/users.sqlite")
timezones = ["Asia/Yekaterinburg"]
count = 0


def myincode(text):
    """
    text - your text
    function return str
    """
    string = str(text)
    answer = []
    sdvig = random.choice([i for i in range(101, 10000)]) ** 3 + 2147483647
    sdvig2 = random.choice([i for i in range(len(string))])
    for i in string:
        answer.append(f"{sdvig2}{ord(i) + sdvig}")
    answer.insert(sdvig2, f"{sdvig2}{sdvig}")
    ta = "0x".join([str(i) for i in answer])
    return ta


def mydecode(text):
    """
    !!!this funstion for text after function "mycode"!!!
    funcrion return str
    """
    ta = str(text)
    answer = []
    data = ta.split("0x")
    count = 0
    a = len(data)
    while a > 0:
        count += 1
        a //= 10
    idd = int(data[0][: count])
    while idd >= len(data):
        idd //= 10
    s = int(data[idd][count:])
    data.pop(idd)
    for i in data:
        i = i[count:]
        answer.append(chr(int(i) - s))
    answer = "".join([str(i) for i in answer])
    return answer


def tconv(x):
    return time.strftime("%H:%M:%S %d.%m.%Y", time.localtime(x))


def update_yandex_disk():
    if yandex_disk.exists("users.sqlite"):
        yandex_disk.remove("users.sqlite")
    yandex_disk.upload("db/users.sqlite", "users.sqlite")


def tranclate(string):
    return str(string).replace("year", "год").replace("years", "лет").replace("month", "месяц").replace("months", "год")


def log(message=None, where='ne napisal', full=False, comments="None"):
    global count, history
    count += 1
    if history:
        history = False
        print("""\033[33mWriting history started:\033[30m""")
    elif full:
        try:
            print(f"""\033[33m{"-" * 100}
time: \033[36m{tconv(message.date)}\033[33m
log №{count}
from: {where}
full: {full}
id: \033[36m{message.from_user.id}\033[33m
username: \033[36m{message.from_user.username}\033[33m
first_name(имя): \033[36m{message.from_user.first_name}\033[33m
last_name(фамилия): \033[36m{message.from_user.last_name}\033[33m
text: {message.text}
message: \033[35m{message}\033[33m
comments: \033[31m{comments}\033[33m""")
        except Exception as er:
            print(f"""\033[31m{"-" * 100}\n!ошибка, лог №{count}\n message: {message}
where: {where}
full: {full}\033
comments: {comments}
error: {er}[0m""")
    else:
        try:
            print(f"""\033[33m{"-" * 100}
time: \033[36m{tconv(message.date)}\033[33m
log №{count}
from: {where}
full: {full}
id: \033[36m{message.from_user.id}\033[33m
username: \033[36m{message.from_user.username}\033[33m
first_name(имя): \033[36m{message.from_user.first_name}\033[33m
last_name(фамилия): \033[36m{message.from_user.last_name}\033[33m
text: \033[35m{message.text}\033[33m
comment: {comments}\033[0m""")
        except Exception as er:
            print(f"""\033[31m!ошибка! Лог №{count}\n message: {message}
time: \033[36m{datetime.datetime.now()}\033[33m
where: {where}
full: {full}
comments: {comments}
error: {er}\033[0m""")


def keyboard_creator(list_of_names, one_time=True):
    """
    :param list_of_names: list; это список с именами кнопок(['1', '2'] будет каждая кнопка в ряд)
    [['1', '2'], '3'] первые 2 кнопки будут на 1 линии, а 3 снизу)
    :param one_time: bool; скрыть клаву после нажатия или нет
    :return: готовый класс клавиатуры в низу экрана
    """
    returned_k = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time)
    for i in list_of_names:
        if isinstance(i, list):
            string = ""
            for o in range(len(i) - 1):
                string += f"'{i[o]}', "
            string += f"'{i[-1]}'"
            exec(f"""returned_k.row({string})""")
            continue
        exec(f"""returned_k.row('{i}')""")
    return returned_k


def buttons_creator(dict_of_names, how_many_rows=8):
    """
    :param dict_of_names: dict; это словарь, первые ключи могут быть любыми, они разделяют кнопки на ряды, а значениями
           этих ключей
           являются другие словари. Первый их аргумент это текст кнопки, а 2 это callback_data(то что будет передаваться
           в
           коллбек). Например: {
                                   '1': {
                                       'текст первой кнопки': 'нажали на кнопку 1',
                                       'текст второй кнопки': 'нажали на кнопку 2'
                                       },
                                   '2': {
                                       'текст третьей кнопки': 'нажали на кнопку 3'
                                       }
                               }
    :param how_many_rows: int; это максимальное количество кнопок в ряду
    :return: готовый класс кнопок под сообщением
    """
    returned_k = types.InlineKeyboardMarkup(row_width=how_many_rows)
    for i in dict_of_names.keys():
        if type(dict_of_names[i]) is dict:
            count1 = 0
            for o in dict_of_names[i].keys():
                count1 += 1
                exec(
                    f"""button{count1} = types.InlineKeyboardButton(text='{o}', 
                    callback_data='{dict_of_names[i][o]}')""")
            s = []
            for p in range(1, count1 + 1):
                s.append(f"button{p}")
            exec(f"""returned_k.add({', '.join(s)})""")
        else:
            exec(f"""button = types.InlineKeyboardButton(text='{i}', callback_data='{dict_of_names[i]}')""")
            exec(f"""returned_k.add(button)""")
    return returned_k


def request_to_yaklass(tg_id):
    global timezones
    try:
        session = db_session.create_session()
        user = session.query(User).filter(User.tg_id == tg_id).first()
        url = 'https://www.yaklass.ru/Account/Login'
        # with open('test.html', 'w', encoding="utf-8") as output_file:
        #     for i in r.text.split("\n"):
        #         output_file.writelines(i)
        session = requests.Session()
        user_agent_val = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) 
Chrome/87.0.4280.141 Safari/537.36 OPR/73.0.3856.415 (Edition Yx GX 03)""".replace('\n', "")
        session.get(url, headers={
            'User-Agent': user_agent_val
        })
        session.headers.update({'Referer': url})
        session.headers.update({'User-Agent': user_agent_val})
        _xsrf = session.cookies.get('_xsrf', domain="yaklass.ru")
        session.post(url, {
            'backUrl': 'https://www.yaklass.ru/Account/Login',
            'username': mydecode(user.login),
            'password': mydecode(user.password),
            '_xsrf': _xsrf,
            'remember': 'yes'
        })
        url = "https://www.yaklass.ru/testwork"
        r = session.get(url, headers={
            'User-Agent': user_agent_val
        })
        # with open("ysklass.html", "w", encoding="utf-8") as f:
        #     for string in r.text.split("\n"):
        #         f.writelines(string)
        text = r.text
        soup = BeautifulSoup(text, features="lxml")
        table = soup.find_all('tr', {'class': 'statusUnchecked'})
        table1 = soup.find_all('tr', {'class': 'statusRunning'})
        countt = 0
        _len = 0
        jobs = []
        for work in table:
            if work.find('td', {'class': "status left"}).get('title') != 'Закончена':
                dates = work.find_all('input', {'class': 'utc-date-time'})
                time1 = datetime.datetime.fromtimestamp(int(dates[1].get('value')), timezone.utc)
                utcmoment_naive = datetime.datetime.utcnow()
                utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
                time2 = utcmoment.astimezone(pytz.timezone(timezones[0]))
                time1 = time1.astimezone(pytz.timezone(timezones[0]))
                if (time1 - time2).days >= 1:
                    jobs.append({'name': work.find('a').text,
                                 'href': f"""https://www.yaklass.ru{work.find("a").get("href")}""",
                                 'time': ", ".join((lambda x: [x.split(", ")[0],
                                                               f"{x.split(', ')[1].split(':')[0]} hours",
                                                               f"{x.split(', ')[1].split(':')[1]} minutes",
                                                               f"{int(x.split(', ')[1].split(':')[2].split('.')[0])} seconds"]
                                                    )(str(time1 - time2))),
                                 'time(d)': time1})
                else:
                    jobs.append({'name': work.find('a').text,
                                 'href': f"""https://www.yaklass.ru{work.find("a").get("href")}""",
                                 'time': ", ".join((lambda x: [f"{x.split(':')[0]} hours",
                                                               f"{x.split(':')[1]} minutes",
                                                               f"{int(x.split(':')[2].split('.')[0])} seconds"]
                                                    )(str(time1 - time2))),
                                 'time(d)': time1})
            else:
                countt += 1
            _len += 1
        for work in table1:
            if work.find('td', {'class': "status left"}).get('title') != 'Закончена':
                dates = work.find_all('input', {'class': 'utc-date-time'})
                time1 = datetime.datetime.fromtimestamp(int(dates[1].get('value')), timezone.utc)
                utcmoment_naive = datetime.datetime.utcnow()
                utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
                time2 = utcmoment.astimezone(pytz.timezone(timezones[0]))
                time1 = time1.astimezone(pytz.timezone(timezones[0]))
                if (time1 - time2).days >= 1:
                    jobs.append({'name': work.find('a').text,
                                 'href': f"""https://www.yaklass.ru{work.find("a").get("href")}""",
                                 'time': ", ".join((lambda x: [x.split(", ")[0],
                                                               f"{x.split(', ')[1].split(':')[0]} hours",
                                                               f"{x.split(', ')[1].split(':')[1]} minutes",
                                                               f"{int(x.split(', ')[1].split(':')[2].split('.')[0])} seconds"]
                                                    )(str(time1 - time2))),
                                 'time(d)': time1})
                else:
                    jobs.append({'name': work.find('a').text,
                                 'href': f"""https://www.yaklass.ru{work.find("a").get("href")}""",
                                 'time': ", ".join((lambda x: [f"{x.split(':')[0]} hours",
                                                               f"{x.split(':')[1]} minutes",
                                                               f"{int(x.split(':')[2].split('.')[0])} seconds"]
                                                    )(str(time1 - time2))),
                                 'time(d)': time1})
            else:
                countt += 1
            _len += 1
        if _len == countt:
            if _len == 0 and countt == 0:
                return Text.return_text_jaklass
            return jobs
        else:
            jobs.sort(key=lambda x: x["time"])
            return jobs
    except Exception as er:
        log(message=None, where="request_to_yaklass", comments=str(er))
        return Text.error_jaklass


@bot.message_handler(commands=["help"])
def help_bot(message):
    # session = db_session.create_session()
    # user = session.query(User).filter(User.tg_id == message.from_user.id).first()
    bot.send_message(message.from_user.id, f"hz")


@bot.message_handler(commands=["start"])
def start(message):
    session = db_session.create_session()
    user = session.query(User).filter(User.tg_id == message.from_user.id).first()
    try:
        if user.login:
            answer = request_to_yaklass(message.from_user.id)
            if answer == Text.return_text_jaklass:
                user.place = 'menu'
                # text = [f"{NADO_YDALIT}", f"К радости у вас нет работ."]
                text = [Text.return_text_jaklass]
                return bot.send_message(message.from_user.id, "\n".join(text),
                                        reply_markup=buttons_creator(Buttons.update))
            elif type(answer) is list:
                text = [f"К сожалению у вас есть работы:", ""]
                # text = [f"{NADO_YDALIT}", f"К сожалению у вас есть работы:", ""]
                k = InlineKeyboardMarkup(row_width=1)
                for i in answer:
                    text.append(f"Название: {i['name']}")
                    text.append(f"Оставшееся время: {i['time']}")
                    text.append(f"Ссылка: {i['href']}")
                    text.append("")
                    k.add(InlineKeyboardButton(i['name'], url=i['href']))
                text = text[: -1]
                k.add(InlineKeyboardButton('Обновить', callback_data="update"))
                return bot.send_message(message.from_user.id, "\n".join(text),
                                        reply_markup=k)
        else:
            user.place = 'login'
            session.commit()
            return bot.send_message(message.from_user.id, Text.start, reply_markup=ReplyKeyboardRemove())
    except Exception:
        user = User()
        user.tg_id = message.from_user.id
        user.count = 0
        user.login = ""
        user.password = ""
        user.place = 'login'
        utcmoment_naive = datetime.datetime.utcnow()
        utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
        time2 = utcmoment.astimezone(pytz.timezone(timezones[0]))
        user.last_time = time2.timestamp()
        session.add(user)
        session.commit()
    bot.send_message(message.from_user.id, Text.start, reply_markup=ReplyKeyboardRemove())


def send_answer_yaklass(tg_id):
    sessionn = db_session.create_session()
    user = sessionn.query(User).filter(User.tg_id == tg_id).first()
    answer = request_to_yaklass(tg_id)
    if answer == Text.return_text_jaklass:
        user.place = 'menu'
        # text = [f"{NADO_YDALIT}", f"К радости у вас нет работ."]
        text = [Text.return_text_jaklass]
        bot.send_message(tg_id, "\n".join(text),
                         reply_markup=buttons_creator(Buttons.update))
        bot.send_message(tg_id, Text.main_menu, reply_markup=keyboard_creator(Keyboard.main_menu)
                         )
    elif type(answer) is list:
        text = [Text.bad_news, ""]
        user.place = 'menu'
        k = InlineKeyboardMarkup(row_width=1)
        # text = [f"{NADO_YDALIT}", f"К сожалению у вас есть работы:", ""]
        for i in answer:
            text.append(f"Название: {i['name']}")
            text.append(f"Оставшееся время: {i['time']}")
            text.append(f"Ссылка: {i['href']}")
            k.add(
                InlineKeyboardButton(i['name'] if len(i['name']) <= 30 else i['name'][: 30] + "...", url=i['href']))
            text.append("")
        text = text[: -1]
        k.add(InlineKeyboardButton('Обновить', callback_data="update"))
        bot.send_message(tg_id, "\n".join(text),
                         reply_markup=k)
        bot.send_message(tg_id, Text.main_menu, reply_markup=keyboard_creator(Keyboard.main_menu))


@bot.message_handler(content_types=['text'])
def hz(message):
    sessionn = db_session.create_session()
    user = sessionn.query(User).filter(User.tg_id == message.from_user.id).first()
    if user.place == 'login':
        user.login = myincode(message.text)
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(message.chat.id, message.message_id - 1)
        bot.send_message(message.from_user.id, Text.enter_password, reply_markup=ReplyKeyboardRemove())
        user.place = 'password'
        sessionn.commit()
    elif user.place == 'password':
        user.password = myincode(message.text)
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(message.chat.id, message.message_id - 1)
        bot.send_message(message.from_user.id, Text.chek)
        user.place = 'login'
        sessionn.commit()
        answer = request_to_yaklass(message.from_user.id)
        if answer == Text.error_jaklass:
            user.place = 'login'
            return bot.send_message(message.from_user.id, f"К сожалению вы ввели неправильный логин или пароль, "
                                                          f"давайте попробуеб ещё, введите логин:")
        elif answer == Text.return_text_jaklass:
            user.place = 'menu'
            # text = [f"{NADO_YDALIT}", f"К радости у вас нет работ."]
            text = [Text.return_text_jaklass]
            bot.send_message(message.from_user.id, "\n".join(text),
                             reply_markup=buttons_creator(Buttons.update))
            bot.send_message(message.from_user.id, Text.main_menu, reply_markup=keyboard_creator(Keyboard.main_menu))
        elif type(answer) is list:
            text = [Text.bad_news, ""]
            user.place = 'menu'
            # text = [f"{NADO_YDALIT}", f"К сожалению у вас есть работы:", ""]
            k = InlineKeyboardMarkup(row_width=1)
            for i in answer:
                text.append(f"Название: {i['name']}")
                text.append(f"Оставшееся время: {i['time']}")
                text.append(f"Ссылка: {i['href']}")
                text.append("")
                k.add(
                    InlineKeyboardButton(i['name'] if len(i['name']) <= 30 else i['name'][: 30] + "...", url=i['href']))
            text = text[: -1]
            k.add(InlineKeyboardButton('Обновить', callback_data="update"))
            bot.send_message(message.from_user.id, "\n".join(text),
                             reply_markup=k)
            bot.send_message(message.from_user.id, Text.main_menu, reply_markup=keyboard_creator(Keyboard.main_menu))
        utcmoment_naive = datetime.datetime.utcnow()
        utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
        time = utcmoment.astimezone(pytz.timezone(timezones[0]))
        user.last_time = int(time.timestamp())
        sessionn.commit()
        update_yandex_disk()
    elif user.place == 'menu':
        if message.text == Keyboard.main_menu[0][0]:
            user.place = 'login'
            sessionn.commit()
            return bot.send_message(message.from_user.id, Text.login, reply_markup=ReplyKeyboardRemove())
        elif message.text == Keyboard.main_menu[0][1]:
            send_answer_yaklass(message.from_user.id)
        else:
            bot.send_message(message.from_user.id, Text.error, reply_markup=ReplyKeyboardRemove())
            bot.send_message(message.from_user.id, Text.main_menu, reply_markup=keyboard_creator(Keyboard.main_menu))


@bot.callback_query_handler(func=lambda call: str(call.data).isdigit() or call.data in ['update'])
def callback_worker(call):
    db = db_session.create_session()
    user = db.query(User).filter(User.tg_id == call.message.chat.id)
    answer = request_to_yaklass(call.message.chat.id)
    if call.data == "update":
        if answer == 'К радости у вас нет работ':
            user.place = 'menu'
            text = [f"К радости у вас нет работ."]
            bot.edit_message_text("\n".join(text), call.message.chat.id, call.message.message_id,
                                  reply_markup=buttons_creator({"1": {"Обновить": "update"}}))
        elif type(answer) is list:
            text = [f"К сожалению у вас есть работы:", ""]
            # text = [f"{NADO_YDALIT}", f"К сожалению у вас есть работы:", ""]
            k = InlineKeyboardMarkup(row_width=1)
            for i in answer:
                text.append(f"Название: {i['name']}")
                text.append(f"Оставшееся время: {i['time']}")
                text.append(f"Ссылка: {i['href']}")
                text.append("")
                k.add(
                    InlineKeyboardButton(i['name'] if len(i['name']) <= 30 else i['name'][: 30] + "...", url=i['href']))
            text = text[: -1]
            k.add(InlineKeyboardButton('Обновить', callback_data="update"))
            bot.edit_message_text("\n".join(text), call.message.chat.id, call.message.message_id,
                                  reply_markup=k)


def update():
    print(datetime.datetime.now(timezone.utc).astimezone(pytz.timezone(timezones[0])))
    try:
        sessionn = db_session.create_session()
        users = sessionn.query(User).all()
        for user in users:
            try:
                last_time = datetime.datetime.strptime(str(user.last_time), '%Y-%m-%d %H:%M:%S.%f%z')
            except Exception:
                last_time = datetime.datetime.fromtimestamp(float(user.last_time), timezone.utc)
            answer = request_to_yaklass(user.tg_id)
            if type(answer) is list:
                text = [Text.bad_news, ""]
                # user.place = 'menu'
                min_time = answer[0]["time(d)"]
                utcmoment_naive = datetime.datetime.utcnow()
                utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
                time_now = utcmoment.astimezone(pytz.timezone(timezones[0]))
                k = InlineKeyboardMarkup(row_width=1)
                if (min_time - time_now).days >= 1 and (time_now - last_time).days >= 1:
                    for i in answer:
                        text.append(f"Название: {i['name']}")
                        text.append(f"Оставшееся время: {i['time']}")
                        text.append(f"Ссылка: {i['href']}")
                        text.append("")
                        k.add(
                            InlineKeyboardButton(i['name'] if len(i['name']) <= 30 else i['name'][: 30] + "...",
                                                 url=i['href']))
                    text = text[: -1]
                    k.add(InlineKeyboardButton('Обновить', callback_data="update"))
                    bot.send_message(user.tg_id, "\n".join(text),
                                     reply_markup=k)
                    bot.send_message(user.tg_id, Text.main_menu, reply_markup=keyboard_creator(Keyboard.main_menu))
                    user.last_time = time_now
                elif (min_time - time_now).days < 1 and (min_time - time_now).seconds >= 5 * 60 * 60 and (
                        time_now - last_time).seconds >= 60 * 60:
                    for i in answer:
                        text.append(f"Название: {i['name']}")
                        text.append(f"Оставшееся время: {i['time']}")
                        text.append(f"Ссылка: {i['href']}")
                        text.append("")
                        k.add(
                            InlineKeyboardButton(i['name'] if len(i['name']) <= 30 else i['name'][: 30] + "...",
                                                 url=i['href']))
                    text = text[: -1]
                    k.add(InlineKeyboardButton('Обновить', callback_data="update"))
                    bot.send_message(user.tg_id, "\n".join(text),
                                     reply_markup=k)
                    bot.send_message(user.tg_id, Text.main_menu, reply_markup=keyboard_creator(Keyboard.main_menu))
                    user.last_time = time_now
                elif (min_time - time_now).seconds < 5 * 60 * 60 and (
                        time_now - last_time).seconds >= 30 * 60:
                    for i in answer:
                        text.append(f"Название: {i['name']}")
                        text.append(f"Оставшееся время: {i['time']}")
                        text.append(f"Ссылка: {i['href']}")
                        text.append("")
                        k.add(
                            InlineKeyboardButton(i['name'] if len(i['name']) <= 30 else i['name'][: 30] + "...",
                                                 url=i['href']))
                    text = text[: -1]
                    k.add(InlineKeyboardButton('Обновить', callback_data="update"))
                    bot.send_message(user.tg_id, "\n".join(text),
                                     reply_markup=k)
                    bot.send_message(user.tg_id, Text.main_menu, reply_markup=keyboard_creator(Keyboard.main_menu))
                    user.last_time = time_now
                sessionn.commit()
    except Exception as er:
        print("oshibka:", er)


def start_chek():
    schedule.every().minute.do(update)
    while True:
        schedule.run_pending()
        time.sleep(1)


def tg_bot_start():
    for i in range(10):
        try:
            print('\033[0mStarted.....')
            log()
            bot.infinity_polling()
        except Exception as err:
            print('\033[31mCrashed.....')
            print(f"Error: {err}")
            time.sleep(10)
            print('\033[35mRestarting.....')


def main():
    x = threading.Thread(target=start_chek)
    x.start()
    x = threading.Thread(target=tg_bot_start)
    x.start()


try:
    main()
except Exception:
    print('\033[35mОшибка, мы не смогли решить её.\033[0m')
