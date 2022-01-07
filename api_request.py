import requests
from datetime import date, timedelta, datetime
from config import INTRA_TOKEN


def sort_calendar(datajson):
    i = 0

    while i < len(datajson) - 1:
        if datetime.fromisoformat(datajson[i]["start"]) < datetime.fromisoformat(datajson[i + 1]["start"]):
            tmp = datajson[i]
            datajson[i] = datajson[i + 1]
            datajson[i + 1] = tmp
            i = 0
        else:
            i += 1
    return datajson


def api_call_day(start=None, end=None):
    if not start or not end:
        start, end = date.today() + timedelta(days=1)
    print(f"requested date is: {start}")
    data = requests.post(f"https://intra.epitech.eu/{INTRA_TOKEN}/planning/load?format=json&start={start}&end={end}&location=FR/PAR&onlymypromo=true&onlymymodule=true&onlymyevent=true")
    datajson = data.json()
    sorted_calendar = sort_calendar(datajson)
    return sorted_calendar
