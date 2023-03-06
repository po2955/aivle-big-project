from django.db import models
from common.models import Company, User
import os


# 공지사항
class Notice(models.Model):
    #company_id=models.ForeignKey(Company,on_delete=models.CASCADE) #공지를 확인할 수 있는 하청
    locate = models.CharField(max_length=200) # 어느 구 공지인지?
    subject = models.CharField(max_length=200) #제목
    content = models.TextField() #내용
    create_time = models.DateTimeField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE) #작성자 id
    modify_date = models.DateTimeField(null=True, blank=True) #수정일
    file = models.FileField(upload_to="uploads/",null=True, blank=True) # 파일 업로드 (...)
    
    def __str__(self):
        return self.subject
    def get_filename(self):
        return os.path.basename(self.file.name)
    
#댓글
class Reply(models.Model):
    notice_id= models.ForeignKey(Notice,on_delete=models.CASCADE)
    content = models.TextField()
    create_time = models.DateTimeField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    modify_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.content

