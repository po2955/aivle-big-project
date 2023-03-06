from django.shortcuts import render
import requests
from .models import Alarm

def get_post(request):
    if request.method=='POST':
        if request.POST['longitude']=='':
            alarm_id = request.POST['alarm_id']
            alarm_level = request.POST['alarm_level']
            group_id = request.POST['group_id']
            model_id = request.POST['model_id']
            Date=request.POST['Date']
            longitude = None
            Latitude = None
            alarm=Alarm.objects.create(alarm_id=alarm_id,alarm_level=alarm_level,
                                   group_id_id=group_id,model_id_id=model_id
                                   ,longitude=longitude,latitude=Latitude,date=Date)
            alarm.save()
        else:
            alarm_id = request.POST['alarm_id']
            alarm_level = request.POST['alarm_level']
            group_id = request.POST['group_id']
            model_id = request.POST['model_id']
            Date=request.POST['Date']
            longitude = request.POST['longitude']
            Latitude = request.POST['Latitude']
            alarm=Alarm.objects.create(alarm_id=alarm_id,alarm_level=alarm_level,
                                   group_id_id=group_id,model_id_id=model_id
                                   ,longitude=longitude,latitude=Latitude,date=Date)
            alarm.save()
        data = {
            'alarm_id': alarm_id,
            'alarm_level':alarm_level,
            'group_id':group_id,
            'model_id':model_id,
            'longitude':longitude,
            'Latitude':Latitude,
            'Date':Date,
        }
        # alarm=Alarm.objects.create(alarm_id=alarm_id,alarm_level=alarm_level,
        #                            group_id_id=group_id,model_id_id=model_id
        #                            ,longitude=longitude,latitude=Latitude,date=Date)
        # alarm.save()
        return render(request, 'safe/gps.html', data)
