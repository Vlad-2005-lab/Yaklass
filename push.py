from datetime import datetime, timezone
import pytz

utcmoment_naive = datetime.utcnow()
utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)

# print "utcmoment_naive: {0}".format(utcmoment_naive) # python 2
print("utcmoment_naive: {0}".format(utcmoment_naive))
print("utcmoment:       {0}".format(utcmoment))

localFormat = "%Y-%m-%d %H:%M:%S"

timezones = ["Asia/Yekaterinburg"]

for tz in timezones:
    localDatetime = utcmoment.astimezone(pytz.timezone(tz))
    utcmoment_naive = datetime.utcnow()
    utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
    time2 = utcmoment.astimezone(pytz.timezone(timezones[0]))
    print(time2)
    print(datetime.now(timezone.utc) - time2)
