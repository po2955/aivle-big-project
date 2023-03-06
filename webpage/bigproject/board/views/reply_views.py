#댓글관리

from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.utils import timezone
from django.contrib import messages

# Create your views here.

from ..models import Notice, Reply
from ..forms import  ReplyForm
from django.contrib.auth.decorators import login_required

@login_required(login_url='common:login')
def reply_create(request, notice_id):
    notice = get_object_or_404(Notice,pk=notice_id)
    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.create_time = timezone.now()
            reply.notice_id = notice
            reply.user_id = request.user  # 로그인 계정 저장
            reply.save()
            return redirect('{}#reply_{}'.format(
                resolve_url('board:detail', notice_id=notice.id), reply.id))
    else:
        form = ReplyForm()
    context = {'notice': notice, 'form': form}
    return render(request, 'board/notice_detail.html', context)

@login_required(login_url='common:login')
def reply_modify(request, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)
    if request.user != reply.user_id:
        messages.error(request, '수정권한이 없습니다')
        return redirect('board:detail', reply_id=reply.notice_id.id)
    if request.method == "POST":
        form = ReplyForm(request.POST, instance=reply)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.modify_date = timezone.now()
            reply.save()
            return redirect('{}#reply_{}'.format(
                resolve_url('board:detail', notice_id=reply.notice_id.id), reply.id))
    else:
        form = ReplyForm(instance=reply)
    context = {'reply': reply, 'form': form}
    return render(request, 'board/reply_form.html', context)

@login_required(login_url='common:login')
def reply_delete(request, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)
    if request.user != reply.user_id:
        messages.error(request, '삭제권한이 없습니다')
    else:
        reply.delete()
    return redirect('board:detail', notice_id=reply.notice_id.id)