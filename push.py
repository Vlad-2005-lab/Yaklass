import datetime

import pytz
import requests
from bs4 import BeautifulSoup

session = requests.Session()
timezones = ["Asia/Yekaterinburg"]
url = 'https://www.yaklass.ru/Account/Login'
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
    'username': "anikanovvlad@yandex.ru",
    'password': "AVI2005",
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
table.extend(table1)
countt = 0
_len = 0
jobs = []
for work in table:
    td = work.find("td", {"class": "score right"})
    print(td.find("span", {"class": "needCheck"}), " ".join(list(str(i.name) for i in td.children)).replace("None", "").split())
    if work.find('td', {'class': "status left"}).get('title') != 'Закончена':
        dates = work.find_all('input', {'class': 'utc-date-time'})
        time1 = datetime.datetime.fromtimestamp(int(dates[1].get('value')), datetime.timezone.utc)
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

