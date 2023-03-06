from django.db import models
from common.models import Group
    
# AI 모델관리
class AI_Model(models.Model):
    model_id=models.CharField(max_length=200,primary_key=True) #모델아이디
    #path=models.FilePathField()
    version=models.CharField(max_length=200) #모델버전
    explain=models.TextField() #모델설명
    config=models.FileField(null=True,blank=True) #yolov4 필수 필요
    class_txt=models.FileField(null=True,blank=True) #yolov4 필수 필요
    Image=models.ImageField(null=True,blank=True) #yolov4 필수 필요
    weights=models.FileField(null=True,blank=True) #yolov4 필수 필요, yolov5 model file
    
    def __str__(self):
        return self.model_id

# 알람
class Alarm(models.Model):
    date=models.DateTimeField(null=True,blank=True) #알람 발생일
    alarm_level=models.IntegerField() #알람 단계
    alarm_id=models.CharField(max_length=200,primary_key=True)
    group_id =models.ForeignKey(Group,on_delete=models.CASCADE)
    model_id=models.ForeignKey(AI_Model,on_delete=models.CASCADE) #사용모델
    longitude=models.FloatField(null=True,blank=True) 
    latitude=models.FloatField(null=True,blank=True)
    
    def __str__(self):
        return self.alarm_id
    
# 사고
class Accident(models.Model):
    accident_id=models.CharField(max_length=200,primary_key=True)
    date=models.DateTimeField(null=True,blank=True) #사고발생일
    injury=models.IntegerField() #다친+죽은 사람 수
    cause=models.TextField() #원인 ---- time으로 되어있어서 수정함
    group_id =models.ForeignKey(Group,on_delete=models.CASCADE)
    locate=models.CharField(max_length=200) #구
    
    def __str__(self):
        return self.accident_id
