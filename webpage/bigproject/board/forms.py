from django import forms
from .models import Notice, Reply

class NoticeForm(forms.ModelForm):
    upload = forms.FileField(label='첨부 파일', required=False, widget=forms.FileInput(attrs={'class': 'form'}))
    class Meta:
        model = Notice
        fields = ['subject', 'content','file']

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']
        labels = {
            'content': '댓글 내용',
        }