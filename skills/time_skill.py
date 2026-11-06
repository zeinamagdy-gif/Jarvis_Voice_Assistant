import datetime
from . import skill


@skill("what time", "the time")
def tell_time(text):
    return "It is " + datetime.datetime.now().strftime("%I:%M %p")


@skill("what date", "what day", "today's date")
def tell_date(text):
    return "Today is " + datetime.datetime.now().strftime("%A, %B %d")
