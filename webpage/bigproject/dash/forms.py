from django import forms
from safe.models import Accident

class AccidentForm(forms.ModelForm):
    class Meta:
        model = Accident
        fields = ['subject', 'content']
        labels = {
            'subject': '제목',
            'content': '내용',
        }
