import requests
import serial
import time
import pynmea2
from datetime import datetime
from flask import Flask     # flask 모듈을 불러움
import RPi.GPIO as GPIO     # 라즈베리파이 GPIO 관련 모듈을 불러옴
def gps(level,a):
#     REQUEST_URL = 'http://192.168.50.91:8000/test/'
    REQUEST_URL = 'http://172.30.1.17:8000/gps/'
    URL = 'http://172.30.1.17:8000/admin/login/?next=/admin/'
#     URL = 'http://192.168.142.128:8000/admin/login/?next=/admin/'
    teamid = 1
    groupid='g1'
    modelid='m1'

    with requests.Session() as s:
        s.get(URL)  # sets cookie
        if 'csrftoken' in s.cookies:
                # Django 1.6 and up
            csrftoken = s.cookies['csrftoken']
        else:
                # older versions
            csrftoken = s.cookies['csrf']

        login_data = dict(username='admin', password='admin', csrfmiddlewaretoken=csrftoken, next='/')
        r = s.post(URL, data=login_data, headers=dict(Referer=URL))
        headers = {'X-CSRFToken':csrftoken}
        cookies = {'csrftoken': csrftoken}
        now = datetime.now()
        times = str(now.strftime('%Y-%m-%d %H:%M:%S'))
        atimes = str(now.strftime('%Y-%m-%d-%H-%M-%S'))
        lat = 37.0001
        lng = 127.0001
        print(times, lat, lng, level)
        alarmid = str(atimes) + '-' + 'a' + str(a)

        json = {
                'Date': times,
                'Latitude': round(lat,8),
                'longitude': round(lng,8),
                'group_id': groupid,
                'alarm_level': level,
                'model_id': modelid,
                'alarm_id': alarmid
                }
        print(json)
        response = s.post(url = REQUEST_URL, data=json, headers=headers, cookies=cookies)
