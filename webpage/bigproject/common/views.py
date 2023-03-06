from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .decorators import login_message_required, admin_required, logout_message_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
# from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, FormView, TemplateView
from django.views.generic import View
# from django.contrib.auth.views import PasswordResetConfirmView
from .models import User
from .forms import CsRegisterForm, LoginForm, CheckPasswordForm, RecoveryIdForm, RecoveryPwForm, CustomSetPasswordForm, CustomPasswordChangeForm, CustomUserChangeForm
from django.http import HttpResponse
import json
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from .helper import send_mail, email_auth_num
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, Http404
from board.models import Notice
from django.forms.utils import ErrorList
from django.views.decorators.http import require_GET, require_POST
from django.core.exceptions import PermissionDenied


from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.tokens import default_token_generator
from datetime import datetime
# from ipware.ip import get_ip


# 메인화면(로그인 후)
@login_message_required
def main_view(request):
    notice_list = Notice.objects.order_by('-user_id')[:5]

    context = {
        'notice_list' : notice_list,
    }
    return render(request, 'common/main.html', context)


# 로그인
@method_decorator(logout_message_required, name='dispatch')
class LoginView(FormView):
    template_name = 'common/login.html'
    form_class = LoginForm
    success_url = '/common/main/'

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            self.request.session['username'] = username
            login(self.request, user)

            # Session Maintain Test

            remember_session = self.request.POST.get('remember_session', False)
            if remember_session:
                settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False

            # try:
            #     remember_session = self.request.POST['remember_session']
            #     if remember_session:
            #         settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
            # except MultiValueDictKeyError:
            #     settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True
            
        return super().form_valid(form)


# 로그아웃
def logout_view(request):
    logout(request)
    return redirect('/')


# 회원가입 약관동의
@method_decorator(logout_message_required, name='dispatch')
class AgreementView(View):
    def get(self, request, *args, **kwargs):
        request.session['agreement'] = False
        return render(request, 'common/agreement.html')

    def post(self, request, *args, **kwarg):
        if request.POST.get('agreement1', False) and request.POST.get('agreement2', False):
            request.session['agreement'] = True
            if request.POST.get('csregister') == 'csregister':       
                return redirect('/common/csregister/')
            else:
                return redirect('/common/register/')
        else:
            messages.info(request, "약관에 모두 동의해주세요.")
            return render(request, 'common/agreement.html')   


# 회원가입 인증메일 발송 안내 창
def register_success(request):
    if not request.session.get('register_auth', False):
        raise PermissionDenied
    request.session['register_auth'] = False

    return render(request, 'common/register_success.html')


# 회원가입 
class CsRegisterView(CreateView):
    model = User
    template_name = 'common/register_cs.html'
    form_class = CsRegisterForm

    def get(self, request, *args, **kwargs):
        if not request.session.get('agreement', False):
            raise PermissionDenied
        request.session['agreement'] = False

        url = settings.LOGIN_REDIRECT_URL
        if request.user.is_authenticated:
            return HttpResponseRedirect(url)
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        # messages.success(self.request, "회원가입 성공.")
        self.request.session['register_auth'] = True
        messages.success(self.request, '회원님의 입력한 Email 주소로 인증 메일이 발송되었습니다. 인증 후 로그인이 가능합니다.')
        # return settings.LOGIN_URL
        return reverse('common:register_success')

    def form_valid(self, form):
        self.object = form.save()

        # 회원가입 인증 메일 발송
        # ISSUE - https 통신오류 -> http 프로토콜 수정
        send_mail(
            '[Safe Guard] {}님의 회원가입 인증메일 입니다.'.format(self.object.username),
            [self.object.email],
            html=render_to_string('common/register_email.html', {
                'user': self.object,
                'uid': urlsafe_base64_encode(force_bytes(self.object.pk)).encode().decode(),
                'domain': self.request.META['HTTP_HOST'],
                'token': default_token_generator.make_token(self.object),
            }),
        )
        return redirect(self.get_success_url())

"""
# 일반 회원가입
class RegisterView(CsRegisterView):
    template_name = 'common/register.html'
    form_class = RegisterForm
"""

# 이메일 인증 활성화
def activate(request, uid64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uid64))
        current_user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
        messages.error(request, '메일 인증에 실패했습니다.')
        return redirect('common:login')

    if default_token_generator.check_token(current_user, token):
        current_user.is_active = True
        current_user.save()

        messages.info(request, '메일 인증이 완료 되었습니다. 회원가입을 축하드립니다!')
        return redirect('common:login')

    messages.error(request, '메일 인증에 실패했습니다.')
    return redirect('common:login')


# 비밀번호 수정
@login_message_required
def password_edit_view(request):
    if request.method == 'POST':
        password_change_form = CustomPasswordChangeForm(request.user, request.POST)
        if password_change_form.is_valid():
            user = password_change_form.save()
            update_session_auth_hash(request, user)
            # logout(request)
            messages.success(request, "비밀번호를 성공적으로 변경하였습니다.")
            return redirect('common:profile')
    else:
        password_change_form = CustomPasswordChangeForm(request.user)

    return render(request, 'common/profile_password.html', {'password_change_form':password_change_form})


# 아이디찾기
@method_decorator(logout_message_required, name='dispatch')
class RecoveryIdView(View):
    template_name = 'common/recovery_id.html'
    recovery_id = RecoveryIdForm

    def get(self, request):
        if request.method=='GET':
            form_id = self.recovery_id(None)
        return render(request, self.template_name, { 'form_id':form_id, })


# 비밀번호찾기
@method_decorator(logout_message_required, name='dispatch')
class RecoveryPwView(View):
    template_name = 'common/recovery_pw.html'
    recovery_pw = RecoveryPwForm

    def get(self, request):
        if request.method=='GET':
            form_pw = self.recovery_pw(None)
            return render(request, self.template_name, { 'form_pw':form_pw, })


# 아이디찾기 AJAX 통신
def ajax_find_id_view(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    result_id = User.objects.get(name=name, email=email)
       
    return HttpResponse(json.dumps({"result_id": result_id.username}, cls=DjangoJSONEncoder), content_type = "application/json")    


# 비밀번호찾기 AJAX 통신
def ajax_find_pw_view(request):
    username = request.POST.get('username')
    name = request.POST.get('name')
    email = request.POST.get('email')
    result_pw = User.objects.get(username=username, name=name, email=email)

    if result_pw:
        auth_num = email_auth_num()
        result_pw.auth = auth_num 
        result_pw.save()

        send_mail(
            '[Safy Guard] 비밀번호 찾기 인증메일입니다.',
            [email],
            html=render_to_string('common/recovery_email.html', {
                'auth_num': auth_num,
            }),
        )
    # print(auth_num)
    return HttpResponse(json.dumps({"result": result_pw.username}, cls=DjangoJSONEncoder), content_type = "application/json")


# 비밀번호찾기 인증번호 확인
def auth_confirm_view(request):
    # if request.method=='POST' and 'auth_confirm' in request.POST:
    username = request.POST.get('username')
    input_auth_num = request.POST.get('input_auth_num')
    user = User.objects.get(username=username, auth=input_auth_num)
    # login(request, user)
    user.auth = ""
    user.save()
    request.session['auth'] = user.username  
    
    return HttpResponse(json.dumps({"result": user.username}, cls=DjangoJSONEncoder), content_type = "application/json")

        
# 비밀번호찾기 새비밀번호 등록
@logout_message_required
def auth_pw_reset_view(request):
    if request.method == 'GET':
        if not request.session.get('auth', False):
            raise PermissionDenied

    if request.method == 'POST':
        session_user = request.session['auth']
        current_user = User.objects.get(username=session_user)
        # del(request.session['auth'])
        login(request, current_user)

        reset_password_form = CustomSetPasswordForm(request.user, request.POST)
        
        if reset_password_form.is_valid():
            user = reset_password_form.save()
            messages.success(request, "비밀번호 변경완료! 변경된 비밀번호로 로그인하세요.")
            logout(request)
            return redirect('common:login')
        else:
            logout(request)
            request.session['auth'] = session_user
    else:
        reset_password_form = CustomSetPasswordForm(request.user)

    return render(request, 'common/password_reset.html', {'form':reset_password_form})

# 프로필 보기
@login_message_required
def profile_view(request):
    if request.method == 'GET':
        return render(request, 'common/profile.html')


# 프로필 수정
@login_message_required
def profile_update_view(request):
    if request.method == 'POST':
        user_change_form = CustomUserChangeForm(request.POST, instance = request.user)
        if user_change_form.is_valid():
            user_change_form.save()
            messages.success(request, '회원정보가 수정되었습니다.')
            return render(request, 'common/profile.html')
    else:
        user_change_form = CustomUserChangeForm(instance = request.user)
        return render(request, 'common/profile_update.html', {'user_change_form':user_change_form})
    
# 회원탈퇴
@login_message_required
def profile_delete_view(request):
    if request.method == 'POST':
        password_form = CheckPasswordForm(request.user, request.POST)
        
        if password_form.is_valid():
            request.user.delete()
            logout(request)
            messages.success(request, "회원탈퇴가 완료되었습니다.")
            return redirect('/')
    else:
        password_form = CheckPasswordForm(request.user)

    return render(request, 'common/profile_delete.html', {'password_form':password_form})

# 개인정보 처리방침
def pipp_view(request):
    return render(request, 'common/pipp.html')

# 이용약관
def tac_view(request):
    return render(request, 'common/tac.html')