from django.shortcuts import render
# Create your views here.

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import StreamingHttpResponse
import cv2

#import numpy as np
import torch
import time
import json
from datetime import datetime

#import webbrowser

from .models import AI_Model
import requests

#import threading
#from time import sleep
import asyncio

yolo_link = r'C:\Bigproject\bp_gw\yolov5'

@login_required(login_url='common:login')
def main(request):
    return render(request, 'common/main.html')

def robo(request):
    return render(request,'safe/robo_index.html')

def sanitationWorker(request):
    return render(request,'safe/sanitationWorker.html')

def car(request):
    return render(request, 'safe/car_index.html')

DISTANCE_STD = 178 #cm
CAR_WIDTH = 180 # 레퍼런스 차 너비 180cm
# TRUCK_WIDTH = 200 #레퍼런스 트럭 사진의 트럭 너비
NMS_THRESHOLD = 0.3
CONFIDENCE_THRESHOLD = 0.5

COLORS = [(255,0,0),(255,0,255),(0, 255, 255), (255, 255, 0)]
FONTS = cv2.FONT_HERSHEY_COMPLEX
FONT_COLOR =(0,255,0)
class_names = []

#장고 쉘을 이용한 모델로드
model_list=AI_Model.objects.all().values()
worker_model=model_list[0] # 환경미화원 모델
car_model=model_list[1] # 자동차 모델

with open(car_model['class_txt'], "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]

yoloNet = cv2.dnn.readNet(car_model['weights'],car_model['config'],)
yoloNet.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
yoloNet.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)

model = cv2.dnn_DetectionModel(yoloNet)
model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)
model2 = torch.hub.load(yolo_link, 'custom', path=worker_model['weights'], source='local')  # yolov5n - yolov5x6 or custom
model2.conf=0.7

def detect_object(image):
    classes, scores, boxes = model.detect(image, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
    data_list =[]
    for (classid, score, box) in zip(classes, scores, boxes):
        color= COLORS[int(classid) % len(COLORS)]
        label = f"{class_names[classid[0]]} : {score}"

        if classid == 2 or classid == 7 or classid == 3 or classid == 5:
            data_list .append([class_names[classid[0]], box[2], (box[0], box[1]-2)]) #data_list  [클래스이름, 바운딩박스 폭, ( 좌상단 좌표)]
            cv2.rectangle(image, box, color,2)
            #cv2.putText(image, label, (box[0], box[1]-11), FONTS, 0.5, color, 2)
    return data_list

def find_focal_length(measured_distance, real_width, width_in_frame):
    focal_length = (width_in_frame * measured_distance) / real_width #초점 거리 = 픽셀 * 물체와의 거리 / 실제 폭
    return focal_length

def find_distance(focal_length, real_object_width, width_in_frame): #초점거리, 실제 폭, 사진 속에서의 폭(픽셀)
    distance = (real_object_width * focal_length) / width_in_frame #물체와의 거리 = 실제 폭 * 초점거리 / 픽셀
    return distance

std_car = cv2.imread(car_model['Image']) #차 레퍼런스 이미지
std_car_data = detect_object(std_car) #
std_car_width_in_frame = std_car_data[0][1] #사진 속 픽셀너비
std_truck_data = detect_object(std_car)
std_truck_width_in_frame = std_truck_data[0][1]
focal_car = find_focal_length(DISTANCE_STD, CAR_WIDTH, std_car_width_in_frame)
prevtime = 0
danger = cv2.imread('danger8.png')
size = 200
danger = cv2.resize(danger, (size, size))
img2gray = cv2.cvtColor(danger, cv2.COLOR_BGR2GRAY)
ret, mask = cv2.threshold(img2gray, 1, 255, cv2.THRESH_BINARY)

def stream():
    cap = cv2.VideoCapture("http://172.30.1.6:8082")
    #cap=cv.VideoCapture(0)
    global j
    
    while True:
        ret, frame = cap.read()
        if frame and time==0:
            roi = frame[100:-100, 100:-100]
            data = detect_object(roi)

            for d in data:
                #print(d)
                if d[0] =='truck' or d[0] =='car' or d[0] =='motorbike' or d[0] =='bus':
                    distance = find_distance(focal_car, CAR_WIDTH, d[1])
                    x, y = d[2]
                    dis=round(distance/0.01,2) #차량 거리 계산
                    #cv.putText(roi, f'Dis: {dis} m', (x+3,y+15), FONTS, 0.48, GREEN, 2)
                    if dis <= 28 :#경고
                        async def redon():
                            resp = requests.get('http://172.30.1.93:4000/red_on')
                        asyncio.run(redon())
                        print('찐 빨강')
                        j = 0

                    elif dis > 28 and dis <= 56  :#주의
                    # led controll
                        async def yellowon():
                            resp = requests.get('http://172.30.1.93:4000/yellow_on')
                        asyncio.run(yellowon())
                        print("찐 노랑")
                        j = 0

        if not ret:
            print("error: failed to capture image")
            break
        image_bytes = cv2.imencode('.jpg', frame)[1].tobytes()

        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + image_bytes + b'\r\n\r\n')

def stream2():
    cap = cv2.VideoCapture("http://172.30.1.40:8081")
    #cap=cv.VideoCapture(0) #web test
    #detect time
    global time
    global j
    time=0
    j=0
    k=0
    #detect 예외처리 -> 12번 count되면 no detect로 인식
    global detect_count
    detect_count=0

    while True:
        #now=datetime.now()
        ret, frame = cap.read() #비디오 보여지는 창
        results = model2([frame], size=640)
        frame = results.render()[0]
        result=results.pandas().xyxy[0].to_json(orient="records") #detect 결과
        result=json.loads(result) #json 처리

        if result==[]: #환경미화원이 탐지 안되면
            if time < 12:
                time = time + 1

            elif (time >= 12) and (k == 0):
                async def off():
                    resp = requests.get('http://172.30.1.93:4000/off')
                asyncio.run(off())
                print("off")
                j = 0
                k = 1

        else:
            for d in result:
                if (d['name']=='-' ) and (float(d['confidence'])>=0.7): #환경미화원이면서 confidecne score가 0.6이상
                    time=0
                    k = 0
                    detect_count=0

                    if j == 0:
                        async def whiteon():
                            resp = requests.get('http://172.30.1.93:4000/white_on')
                        asyncio.run(whiteon())
                        print("환경미화원탐지")
                        j = 1

        if not ret:
            print("error: failed to capture image")
            break
        image_bytes = cv2.imencode('.jpg', frame)[1].tobytes()

        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + image_bytes + b'\r\n\r\n')

   

def video_feed(request):
    return StreamingHttpResponse(stream(),content_type = 'multipart/x-mixed-replace; boundary=frame')
def video_feed2(request):
    return StreamingHttpResponse(stream2(), content_type = 'multipart/x-mixed-replace; boundary=frame')