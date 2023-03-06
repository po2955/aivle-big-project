from django.shortcuts import render, HttpResponse
import json
from django.contrib.auth.decorators import login_required
from . import emo_model
from .models import Emotion
from django.utils import timezone

@login_required(login_url='common:login')
def main(request):
    return render(request, 'emotion/main.html')


def record(request):
    path = 'emotion/files/'
    filename = "output"

    # return X
    emo_model.recode(path, filename, seconds = 5)

    # return str(STT 결과 나온 문장)
    sentence = emo_model.google_STT(path, filename)
    if sentence == None:
        sentence = ""
    
    context = {"result":str(sentence)}

    return HttpResponse(json.dumps(context), content_type="application/json") 


def predict(request):
    path = 'emotion/files/'
    filename = "output"
    model_path = 'emotion/files/sentiment_model.h5'

    sentence = emo_model.google_STT(path, filename)
    pred = emo_model.sentiment_analysis(sentence, model_path)

    if round(pred) == 1:
        feel = True
    else:
        feel = False
        
    emotion_data = Emotion()
    emotion_data.user_id = request.user.id
    emotion_data.company_id = request.user.company_id
    emotion_data.text=sentence
    emotion_data.date= timezone.now()
    emotion_data.predict=pred
    emotion_data.feel=feel
    emotion_data.save()
    
    #emotion_data = Emotion.objects.create(
    #    user_id=request.user.id, company_id=request.user.company_id , date=None, text=sentence, predict=pred, feel=feel)
    #emotion_data.save()
    context = {'feel':feel}
    
    return HttpResponse(json.dumps(context), content_type="application/json")  

