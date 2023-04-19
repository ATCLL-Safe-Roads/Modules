import datetime

print(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+1))).__str__())
