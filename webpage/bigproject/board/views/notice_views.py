# 공지관리
from django.shortcuts import render, get_object_or_404,redirect
from django.utils import timezone
from django.contrib import messages

from django.views.generic.edit import FormView
from django.urls import reverse_lazy

from django.views.generic.detail import SingleObjectMixin
from django.http import FileResponse
from django.core.files.storage import FileSystemStorage
from board.models import Notice
from django.views.generic import View
# Create your views here.

from ..models import Notice
from ..forms import NoticeForm
from django.contrib.auth.decorators import login_required

@login_required(login_url='common:login')
def notice_create(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.create_time = timezone.now()
            notice.locate = request.user.address
            notice.user_id = request.user  # 로그인 계정 저장
            if request.FILES:
                notice.file = request.FILES['file']
            
            notice.save()
            return redirect('board:index')
    else:
        form = NoticeForm()
    context = {'form': form}
    return render(request, 'board/notice_form.html', context)

@login_required(login_url='common:login')
def notice_modify(request, notice_id):
    notice = get_object_or_404(Notice, pk=notice_id)
    if request.user != notice.user_id:
        messages.error(request, '수정 권한이 없습니다')
        return redirect('board:detail', notice_id=notice.id)
    if request.method == "POST":
        form = NoticeForm(request.POST, instance=notice)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.modify_date = timezone.now()  # 수정일시 저장
            notice.save()
            return redirect('board:detail', notice_id=notice.id)
    else:
        form = NoticeForm(instance=notice)
    context = {'form': form}
    return render(request, 'board/notice_form.html', context)

@login_required(login_url='common:login')
def notice_delete(request, notice_id):
    notice = get_object_or_404(Notice, pk=notice_id)
    if request.user != notice.user_id:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('board:detail', notice_id=notice.id)
    notice.delete()
    return redirect('board:index')


class FileDownloadView(SingleObjectMixin, View):
    def get(self, request, notice_id):
        object = get_object_or_404(Notice, pk=notice_id)
        file_path = object.file.path
        #file_type = object.content_type  # django file object에 content type 속성이 없어서 따로 저장한 필드
        fs = FileSystemStorage(file_path)
        response = FileResponse(fs.open(file_path, 'rb')) #, content_type=file_type)
        response['Content-Disposition'] = f'file; filename={object.get_filename()}'
        return response