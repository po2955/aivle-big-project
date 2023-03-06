import requests
import serial
import time
import pynmea2
from datetime import datetime
from flask import Flask     # flask 모듈을 불러움
import RPi.GPIO as GPIO     # 라즈베리파이 GPIO 관련 모듈을 불러옴
from multiprocessing import Process

def gps(level,a):
    REQUEST_URL = 'http://192.168.137.128:8000/gps/'
    URL = 'http://192.168.137.128:8000/admin/login/?next=/admin/'
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
        for i in range(10):
            now = datetime.now()
            port = "/dev/serial0"
            ser=serial.Serial(port, baudrate=9600, timeout = 0.5)
            dataout = pynmea2.NMEAStreamReader()
            newdata=ser.readline().decode('utf-8')
                
            if newdata[0:6] == "$GNGGA":
                newmsg = pynmea2.parse(newdata)
                times = str(now.strftime('%Y-%m-%d %H:%M:%S'))
                lat = newmsg.latitude
                lng = newmsg.longitude
                alarmid = str(atimes) + '_' + 'a' + str(a)
                print(times, lat, lng, level, alarmid)

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

