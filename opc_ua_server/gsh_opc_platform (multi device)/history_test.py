from datetime import timedelta, datetime

current_time = datetime.now().replace(microsecond=0, second=0, minute=0)
added_time = current_time + timedelta(hours=1)
print(added_time)

if datetime.now()>= added_time:
    print("True")
else:
    print("False")