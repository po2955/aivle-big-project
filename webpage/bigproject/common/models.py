from django.db import models
# Create your models here.
from django.contrib.auth.models import AbstractUser

# 하청회사
class Company(models.Model):
    company_id = models.CharField(max_length=200,primary_key=True) #회사 아이디, # PK값
    name = models.CharField(max_length=200) #회사 이름
    address = models.CharField(max_length=200) #회사 주소
    phone = models.CharField(max_length=200,null=True,blank=True) #전화번호
    start_date = models.DateTimeField(null=True, blank=True) #계약시작일
    exp_date=models.DateTimeField(null=True,blank=True) #계약만료일
    locate=models.CharField(max_length=200) #구
    workers = models.IntegerField(null=True,blank=True) # 근로자 수
    
    def __str__(self):
        return self.name

# 사용자 table
class User(AbstractUser):
    #user_id=models.CharField(max_length=200,primary_key=True) # 기본 모델 상속받아서 int로 자동 생성됨 (추후 수정)
    name=models.CharField(max_length=200) 
    #id=models.CharField(max_length=200) #-> 기본 모듈에서 아이디는 username 변수로 기능함
    password=models.CharField(max_length=200)
    address=models.CharField(max_length=200) # 어느 구 소속인지?
    phone=models.CharField(max_length=200)
    company_id=models.ForeignKey(Company,on_delete=models.CASCADE) #하청회사 아이디 / 슈퍼 유저 생성시 오류
    #group_id =models.ForeignKey(Group,on_delete=models.CASCADE) -> 상호 참조 오류
    auth = models.CharField(max_length=10, null=True)
    
    def __str__(self):
        return self.username
    
#근로그룹
class Group(models.Model):
    group_id=models.CharField(max_length=200,primary_key=True)
    job=models.CharField(max_length=200) #직무
    detail_locate=models.TextField(blank=True,null=True) #상세경로
    user_id=models.ForeignKey(User,on_delete=models.CASCADE) #근로자 아이디
    company_id=models.ForeignKey(Company,on_delete=models.CASCADE) #하청회사 아이디
    current=models.IntegerField() #현재인지 아닌지
    
    def __str__(self):
        return self.group_id

# 근로
class Working(models.Model):
    working_id=models.CharField(max_length=200,primary_key=True)
    group_id =models.ForeignKey(Group,on_delete=models.CASCADE)
    date=models.DateTimeField(null=True,blank=True)
    
    def __str__(self):
        return self.working_id
