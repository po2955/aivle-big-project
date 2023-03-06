from django.db import models
from common.models import Company

# 감정 탐지 db
class Emotion(models.Model):
    #user_id = models.CharField(max_length=200)  # user id : Forign key? [추후 변경]
    company_id = models.ForeignKey(Company,on_delete=models.CASCADE) # 소속 위탁업체 (Forign key?) [추후 변경]
    date = models.DateTimeField()  # 시간
    text = models.CharField(max_length=200)  # 예측 텍스트
    predict = models.FloatField()  # 예측 %값
    feel = models.BooleanField()  # 긍부정
    
    def __str__(self):
        return self.text
