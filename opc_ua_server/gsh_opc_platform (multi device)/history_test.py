import psutil
import time


def seconds_elapsed():
    return time.time() - psutil.boot_time()


print(seconds_elapsed())