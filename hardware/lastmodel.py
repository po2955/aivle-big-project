import requests
import serial
import time
import pynmea2
from datetime import datetime
from flask import Flask     # flask 모듈을 불러움
import RPi.GPIO as GPIO     # 라즈베리파이 GPIO 관련 모듈을 불러옴
# gps 없는 상황에서 사용
from nogps import gps
# gps 있는 상황에서 사용
# from yesgps import gp
GPIO.setmode(GPIO.BCM)

white_pin = 16
yellow_pin = 20
red_pin = 21
GPIO.setup(white_pin, GPIO.OUT)    # 각각 LED 핀들을 출력으로 설정
GPIO.setup(yellow_pin, GPIO.OUT)  
GPIO.setup(red_pin, GPIO.OUT)   
global level
app = Flask(__name__)       # Flask라는 이름의 객체 생성
@app.route('/')             # 기본 주소
def hello():                # 해당 주소에서 실행되는 함수 정의
   return "LED 제어 주소"    
   # 반드시 return이 있어야하며, 해당 값을 화면에 보여줌

@app.route('/white_on')       # IP주소:port/red_on 을 입력하면 나오는 페이지
def white_on():               # 해당 페이지의 뷰함수 정의
   GPIO.output(white_pin, GPIO.HIGH)  
   GPIO.output(yellow_pin, GPIO.LOW) 
   GPIO.output(red_pin, GPIO.LOW)
   global level
   global b
   level = 0
   b = 0
   print('white on!!!  no car  level = ',level)
   return "no car"              # 뷰함수의 리턴값

@app.route('/yellow_on')     # IP주소:port/green_on 을 입력하면 나오는 페이지
def yellow_on():             # 해당 페이지의 뷰함수 정의
   GPIO.output(yellow_pin, GPIO.HIGH) # 초록 LED 핀에 HIGH 신호 인가(LED 켜짐)
   GPIO.output(white_pin, GPIO.LOW) 
   GPIO.output(red_pin, GPIO.LOW)
   global level
   global b
   level = 1
   b = 0
   print('yellow on!!!car in 56m   level = ',level)
   return "car in 56m"    

@app.route('/red_on')      
def red_on():              
   GPIO.output(red_pin, GPIO.HIGH)
   GPIO.output(white_pin, GPIO.LOW)  
   GPIO.output(yellow_pin, GPIO.LOW) 
   global level
   global a
   global b
   level = 2
   if b == 0:
       gps(level,a)
       b = 1
       a = a+1
   print('red on!!!  car in 30m   level = ',level)
   return "car in 28m"

@app.route('/off')          # IP주소:port/off 를 입력하면 나오는 페이지
def off():                  # 해당 페이지의 뷰함수 정의
   GPIO.output(white_pin, GPIO.LOW)   # 각각의 LED핀에 LOW 신호를 인가하여 LED 끔
   GPIO.output(yellow_pin, GPIO.LOW) 
   GPIO.output(red_pin, GPIO.LOW)
   global b
   b = 0
   return "all LED off"    

if __name__ == "__main__":# 웹사이트를 호스팅하여 접속자에게 보여주기 위한 부분
   a=1
   b=0
   app.run(host="172.30.1.93", port = "4000")
