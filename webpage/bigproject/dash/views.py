from django.shortcuts import render, HttpResponse
import folium
import json

from safe.models import Alarm, Accident
from common.models import Company, User, Group
from emotion.models import Emotion
from board.models import Reply,Notice
import datetime

from kiwipiepy import Kiwi

# Create your views here.
def mainboard(request):
    now = datetime.datetime.now()
    datas = {'data': []}
    dists = ['수정구','분당구','중원구']
    m_labels = []
    emo_list = []
    for dist_id in dists:
        company_list = Company.objects.filter(locate__exact=dist_id)
        group_list = Group.objects.filter(company_id__in=company_list)
        alarm_list = Alarm.objects.filter(group_id__in=group_list).order_by('-date')
        m_labels = []
        m_chart = []
        for i in range(15):
            m = now - datetime.timedelta(days=i)
            m_labels.append(m.strftime("%m월 %d일"))
            
            m_start = m.strftime("%Y-%m-%d 00:00:00")
            m_end = m.strftime("%Y-%m-%d 23:59:59")
            
            m_alarm = alarm_list.filter(date__range=[m_start, m_end]).count()
            m_chart.append(m_alarm)
        m_labels.reverse()
        m_chart.reverse()
        datas['data'].append([dist_id, m_chart])
        
        # 텍스트 AI - 감정
        num_of_users = 0
        for company in company_list:
            num_of_users += company.workers
        emos = Emotion.objects.filter(company_id__in=company_list)
        done = emos.count()
        if done == 0:
            percent = 0
        else:
            percent = int((emos.filter(feel__exact=True).count()/done)*100)
        emo_list.append({'workers':num_of_users, 'name':dist_id, 'done':done, 'percent':percent})
    datas['emo_list'] = emo_list
    datas['label'] = m_labels
    datas['dists'] = dists
    return render(request, 'dash/mainboard.html',datas)

# 실시간 알람 알림
def alertalarm(request):
    dist_id = request.user.address
    company_list = Company.objects.filter(locate__exact=dist_id)
    group_list = Group.objects.filter(company_id__in=company_list)
    temp = Alarm.objects.filter(group_id__in=group_list).order_by('-date')
    
    now = datetime.datetime.now()
    limit = now-datetime.timedelta(seconds=30) # 지금 시간 기준 30초(변경 가능) 내에 온 알림이 존재하면 팝업 띄움.
    start = limit.strftime("%Y-%m-%d %H:%M:%S")
    end = now.strftime("%Y-%m-%d %H:%M:%S")
    alarm = temp.filter(date__range=[start, end])
    
    if alarm:
        alarm = alarm[0]
        context = {'message': "알람이 도착했습니다! <br> 시간:" +str(alarm.date.time())+"<br> 그룹:"+str(alarm.group_id) }
    else:
        context = {'message': ""}
    return HttpResponse(json.dumps(context), content_type="application/json")


def district(request,dist_id):
    datas = {}
    datas['dist_id'] = dist_id
    
    # ==============  업체 별 현황 - 바 차트 & 근로자 긍부정   =============
    company_list = Company.objects.filter(locate__exact=dist_id)
    co_labels = []
    chart_company = []
    emo_list = []
    
    kiwi = Kiwi()
    kiwi.prepare()
    good_li = {}
    bad_li = {}
    not_use = ['많','거','중','오늘','것','어제','하','좋','힘들','모르',
               '사','개','들','남기','오']
    
    for company in company_list:
        num_of_users = company.workers
        co_labels.append(company.name)
        chart_company.append(num_of_users)
        
        # ============텍스트 AI - 감정
        emos = Emotion.objects.filter(company_id__exact=company.company_id)
        done = emos.count()
        if done == 0:
            percent = 0
        else:
            percent = int((emos.filter(feel__exact=True).count()/done)*100)
        emo_list.append({'workers':num_of_users, 'name':company.name, 'done':done, 'percent':percent})
        
        # ============단어 순위 [[진행중]] 
        for e in emos:
            token = kiwi.tokenize(e.text)
            for t in token:
                if t.tag in ('NNG','NNB','VV','VA') and (t.form not in not_use):
                    if e.feel : #긍정
                        if t.form not in good_li.keys():
                            good_li[t.form] = 0
                        good_li[t.form] += 1
                    else: # 부정
                        if t.form not in bad_li.keys():
                            bad_li[t.form] = 0
                        bad_li[t.form] += 1
    good_li = list(good_li.items())
    good_li.sort(key=lambda x:x[1], reverse=True)
    if len(good_li) > 10:
        good_li = good_li[:10]
        
    bad_li = list(bad_li.items())
    bad_li.sort(key=lambda x:x[1], reverse=True)
    if len(bad_li) > 10:
        bad_li = bad_li[:10]

    datas['good_li'] = good_li
    datas['bad_li'] = bad_li
    datas['emo_list'] = emo_list
    datas['co_labels'] = co_labels
    datas['chart_company'] = chart_company
    datas['company_list'] = company_list
    
    # ====================== map 그리기 ======================
    
    # 해당 구에 속해있는 그룹들
    group_list = Group.objects.filter(company_id__in=company_list)
    
    # 일시 기준 최신 순으로 모든 알람 정렬 
    # to-do : 일정 기간만 넣기 (현 시점으로는 데이터가 몇 개 없어서 전부로 진행함) [추후 수정]
    alarm_list = Alarm.objects.filter(group_id__in=group_list).order_by('-date')
    
    start = False
    #알람마다 마커 추가. GPS 값 없으면 표시되지 않음.
    for alarm in alarm_list:
        if alarm.latitude and alarm.latitude:
            la = alarm.latitude
            lo = alarm.longitude
            if start == False:
                # 제일 최근 알람 기준으로 맵 시작점 세팅
                m = folium.Map(location=[la, lo],zoom_start=14, height=400)
                folium.TileLayer('cartodbpositron').add_to(m)
                start = True
            pop = alarm.date # 마커 클릭 시 나타나는 팝업. 일단 알람 시각으로 지정함. [추후 수정]
            folium.Marker([la, lo], popup=pop, 
                    icon = (folium.Icon(icon= "info", prefix="fa", color="red"))).add_to(m)
    if not alarm_list:
        m = folium.Map(location=[37.3823, 127.1196],zoom_start=14, height=400)
        folium.TileLayer('cartodbpositron').add_to(m)

    maps = m._repr_html_()
    
    datas['map'] = maps
    datas['alarm_list'] = alarm_list
    
    # ====================== 사고 가져오기 ======================
    # 일시 기준 최신 순으로 모든 사고 정렬 
    # to-do : 일정 기간만 넣기 (현 시점으로는 데이터가 몇 개 없어서 전부로 진행함) [추후 수정]
    acc_list = Accident.objects.filter(locate__exact=dist_id).order_by('-date')
    
    datas['acc_list'] = acc_list
    
    # =====================최근 댓글 목록(3개) ====================
    notice_list = Notice.objects.filter(user_id__exact=request.user)
    notice_list = notice_list.filter(locate__exact=dist_id)
    reply_list = Reply.objects.filter(notice_id__in=notice_list).order_by('-create_time')
    
    if len(reply_list) > 3:
        reply_list = reply_list[:3]
    elif len(reply_list) == 0:
        reply_list = None
    
    datas['reply_list'] = reply_list
    
    # ==============  시간 별 알람 현황 (12시간) - 라인 차트   =============
    now = datetime.datetime.now()
    h_labels = []
    chart_alarm = []
    for i in range(12):
        h = now - datetime.timedelta(hours=i)
        h_labels.append(str(h.hour)+"시")
        
        hour_start = h.strftime("%Y-%m-%d %H:00:00")
        hour_end = h.strftime("%Y-%m-%d %H:59:59")
        
        hour_alarm = alarm_list.filter(date__range=[hour_start, hour_end]).count()
        chart_alarm.append(hour_alarm)
    h_labels.reverse()
    chart_alarm.reverse()
    
    datas['h_labels'] = h_labels
    datas['chart_alarm'] = chart_alarm
    
    # ==============  일 별 알람 현황 (30일) - 라인 차트   =============
    d_labels = []
    day_chart = []
    for i in range(15):
        d = now - datetime.timedelta(days=i)
        d_labels.append(d.strftime("%m월 %d일"))
        
        day_start = d.strftime("%Y-%m-%d 00:00:00")
        day_end = d.strftime("%Y-%m-%d 23:59:59")
        
        day_alarm = alarm_list.filter(date__range=[day_start, day_end]).count()
        day_chart.append(day_alarm)
    d_labels.reverse()
    day_chart.reverse()
    
    datas['d_labels'] = d_labels
    datas['day_chart'] = day_chart
    
    return render(request, 'dash/district.html',datas)

def company_table(request,dist_id):
    company_list = Company.objects.filter(locate__exact=dist_id)
    data = {'dist_id':dist_id, 'company_list':company_list}
    return render(request, 'dash/company_table.html', data)

def alarm_table(request,dist_id):
    company_list = Company.objects.filter(locate__exact=dist_id)
    group_list = Group.objects.filter(company_id__in=company_list)
    alarm_list = Alarm.objects.filter(group_id__in=group_list).order_by('-date')
    data = {'dist_id':dist_id, 'alarm_list':alarm_list}
    return render(request, 'dash/alarm_table.html', data)

def accident_table(request,dist_id):
    acc_list = Accident.objects.filter(locate__exact=dist_id).order_by('-date')
    data = {'dist_id':dist_id, 'acc_list':acc_list}
    return render(request, 'dash/accident_table.html', data)

def status_table(request,dist_id):
    company_list = Company.objects.filter(locate__exact=dist_id)
    emo_list  = Emotion.objects.filter(company_id__in=company_list)
    data = {'dist_id':dist_id, 'emo_list':emo_list}
    return render(request, 'dash/status_table.html', data)

"""
def acc_create(request):
    if request.method == 'POST':
        form = AccidentForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.create_time = timezone.now()
            notice.author = request.user  # 로그인 계정 저장
            notice.save()
            return redirect('board:index')
    else:
        form = NoticeForm()
    context = {'form': form}
    return render(request, 'dash/accident_table.html')
"""