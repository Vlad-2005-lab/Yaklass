# -*- coding: utf-8 -*-

import datetime
import requests
from bs4 import BeautifulSoup
import datetime
import schedule
import threading
import telebot
from emoji import emojize
from telebot import types
from data.users import User
from data import db_session
import time

db_session.global_init("db/users.sqlite")
history = True
bot = telebot.TeleBot(open("static/token.txt", mode="r", encoding="utf-8").read())
count = 0
sek = 0


def tconv(x):
    return time.strftime("%H:%M:%S %d.%m.%Y", time.localtime(x))


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


def keyboard_creator(list_of_names):
    returned_k = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
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


def buttons_creator(dict_of_names, how_many_rows=7):
    returned_k = types.InlineKeyboardMarkup(row_width=how_many_rows)
    for i in dict_of_names.keys():
        if type(dict_of_names[i]) is dict:
            count = 0
            for o in dict_of_names[i].keys():
                count += 1
                exec(
                    f"""button{count} = types.InlineKeyboardButton(text='{o}', callback_data='{dict_of_names[i][o]}')""")
            s = []
            for p in range(1, count + 1):
                s.append(f"button{p}")
            exec(f"""returned_k.add({', '.join(s)})""")
        else:
            exec(f"""button = types.InlineKeyboardButton(text='{i}', callback_data='{dict_of_names[i]}')""")
            exec(f"""returned_k.add(button)""")
    return returned_k


def request_to_yaklass(tg_id):
    try:
        session = db_session.create_session()
        user = session.query(User).filter(User.tg_id == tg_id).first()
        url = 'https://www.yaklass.ru/Account/Login'
        # with open('test.html', 'w', encoding="utf-8") as output_file:
        #     for i in r.text.split("\n"):
        #         output_file.writelines(i)
        session = requests.Session()
        user_agent_val = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 OPR/73.0.3856.415 (Edition Yx GX 03)"""
        r = session.get(url, headers={
            'User-Agent': user_agent_val
        })
        session.headers.update({'Referer': url})
        session.headers.update({'User-Agent': user_agent_val})
        _xsrf = session.cookies.get('_xsrf', domain="yaklass.ru")
        post_request = session.post(url, {
            'backUrl': 'https://www.yaklass.ru/Account/Login',
            'username': user.login,
            'password': user.password,
            '_xsrf': _xsrf,
            'remember': 'yes'
        })
        url = "https://www.yaklass.ru/testwork"
        r = session.get(url, headers={
            'User-Agent': user_agent_val
        })
        with open("ysklass.html", "w", encoding="utf-8") as f:
            for string in r.text.split("\n"):
                f.writelines(string)
        text = r.text
        soup = BeautifulSoup(text, features="lxml")
        table = soup.find_all('tr', {'class': 'statusUnchecked'})
        countt = 0
        _len = 0
        jobs = []
        for work in table:
            if work.find('td', {'class': "status left"}).get('title') != 'Закончена' or 1:
                dates = work.find_all('input', {'class': 'utc-date-time'})
                time1 = datetime.datetime.fromtimestamp(int(dates[1].get('value')))
                time2 = datetime.datetime.now()
                jobs.append({'name': work.find('a').text,
                             'href': work.find("a").get("href"),
                             'time': str(time1 - time2)})
            else:
                countt += 1
            _len += 1
        if _len == countt:
            # return "К радости у вас нет работ"
            return jobs
        else:
            return jobs
    except Exception as er:
        print(er)
        return 'К сожалению вы ввели неправильный логин или пароль, давайте попробуеб ещё, введите логин:'


def test():
    global sek
    sek += 1
    print(sek * 5)


def start_chek():
    # schedule.every(30).minutes.do(request_to_yaklass)
    schedule.every(5).seconds.do(test)
    # schedule.every(30).minutes.do(request_to_yaklass)
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


@bot.message_handler(commands=["help"])
def help_bot(message):
    session = db_session.create_session()
    user = session.query(User).filter(User.tg_id == message.from_user.id).first()


@bot.message_handler(commands=["start"])
def start(message):
    session = db_session.create_session()
    user = session.query(User).filter(User.tg_id == message.from_user.id).first()
    try:
        if user.login != '':
            return
        else:
            user.place = 'login'
            session.commit()
            return bot.send_message(message.from_user.id,
                                    f"Привет, этот бот создан для напоминания о работах на Яклассе."
                                    f"Но для этого нам нужен логин и пароль от вашего Якласса."
                                    f"Если вы согласны, то введите логин:")
    except Exception:
        user = User()
        user.tg_id = message.from_user.id
        user.count = 0
        user.login = ""
        user.password = ""
        user.place = 'login'
        session.add(user)
        session.commit()
    bot.send_message(message.from_user.id, f"Привет, этот бот создан для напоминания о работах на Яклассе."
                                           f"Но для этого нам нужен логин и пароль от вашего Якласса."
                                           f"Если вы согласны, то введите логин:")


@bot.message_handler(content_types=['text'])
def hz(message):
    session = db_session.create_session()
    user = session.query(User).filter(User.tg_id == message.from_user.id).first()
    if user.place == 'login':
        user.login = message.text.lower()
        bot.send_message(message.from_user.id, f"Хорошо, теперь введите пароль:")
        user.place = 'password'
        session.commit()
    elif user.place == 'password':
        user.password = message.text
        bot.send_message(message.from_user.id, f"Хорошо, теперь проверим, подождите чуть-чуть......")
        user.place = 'login'
        answer = request_to_yaklass(message.from_user.id)
        if answer == 'К сожалению вы ввели неправильный логин или пароль, давайте попробуеб ещё, введите логин:':
            user.place = 'login'
            bot.send_message(message.from_user.id, f"К сожалению вы ввели неправильный логин или пароль, "
                                                   f"давайте попробуеб ещё, введите логин:")
        elif answer == 'К радости у вас нет работ':
            user.place = 'menu'
            bot.send_message(message.from_user.id, f"К радости у вас нет работ.")
        elif type(answer) is list:
            text = [f"К сожалению у вас есть работы:", ""]
            for i in answer:
                text.append(f"Название: {i['name']}")
                text.append(f"Оставшееся время: {i['time']}")
                text.append(f"Ссылка: {i['href']}")
                text.append("")
            text = text[: -1]
            print(text)
            bot.send_message(message.from_user.id, "\n".join(text), reply_markup=buttons_creator({"1": {"Обновить": "update"}}))
        session.commit()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('\033[35mОшибка, мы не смогли решить её.\033[0m')
