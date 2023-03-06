#기본관리
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from ..models import Notice
from django.db.models import Q

@login_required(login_url='common:login')
def index(request):
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')  # 검색어
    # 작성일시 기준 최신 순으로 정렬
    notice_list = Notice.objects.order_by('-create_time')
    if not request.user.company_id.locate == '성남시':
        notice_list = notice_list.filter(locate__exact=request.user.company_id.locate)
    if kw:
        notice_list = notice_list.filter(
            Q(subject__icontains=kw) |  # 제목 검색
            Q(content__icontains=kw) |  # 내용 검색
            Q(reply__content__icontains=kw) |  # 댓글 내용 검색
            Q(reply__author__username__icontains=kw)  # 댓글 글쓴이 검색
        ).distinct()
    # 페이지당 10개씩 보여주는 기능
    paginator = Paginator(notice_list, 10)  
    page_obj = paginator.get_page(page)
    context = {'notice_list': page_obj, 'page': page, 'kw': kw}
    return render(request, 'board/notice_list.html', context)

@login_required(login_url='common:login')
def detail(request,notice_id):
    notice = get_object_or_404(Notice,pk=notice_id)
    context = {'notice': notice}
    return render(request, 'board/notice_detail.html', context)