from django import forms
from django.contrib.auth.hashers import check_password
from .models import User, Company
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, SetPasswordForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from .choice import *


def phone_validator(value):
	if len(str(value)) != 11:
		raise forms.ValidationError('정확한 핸드폰 번호를 입력해주세요.')

# 로그인 폼
class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
        attrs={'class': 'form-control',}), 
        error_messages={
            'required': '아이디을 입력해주세요.'
        },
        max_length=32,
        label='아이디'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
        attrs={'class': 'form-control',}), 
        error_messages={
            'required': '비밀번호를 입력해주세요.'
        },
        label='비밀번호'
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            try:
               user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.add_error('username', '아이디가 존재하지 않습니다.')
                return
            
            if not check_password(password, user.password):
                self.add_error('password', '비밀번호가 틀렸습니다.')

# 회원탈퇴 비밀번호확인 폼
class CheckPasswordForm(forms.Form):
    password = forms.CharField(label='비밀번호', widget=forms.PasswordInput(
        attrs={'class': 'form-control',}), 
    )
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = self.user.password
        
        if password:
            if not check_password(password, confirm_password):
                self.add_error('password', '비밀번호가 일치하지 않습니다.')


# 아이디찾기 폼
class RecoveryIdForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput,
    )
    email = forms.EmailField(
        widget=forms.EmailInput,
    )

    class Meta:
        fields = ['name', 'email']

    def __init__(self, *args, **kwargs):
        super(RecoveryIdForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = '이름'
        self.fields['name'].widget.attrs.update({
            # 'placeholder': '이름을 입력해주세요',
            'class': 'form-control',
            'id': 'form_name',
        })
        self.fields['email'].label = '이메일'
        self.fields['email'].widget.attrs.update({
            # 'placeholder': '이메일을 입력해주세요',
            'class': 'form-control',
            'id': 'form_email' 
        })


# 비밀번호찾기 폼
class RecoveryPwForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput,
    )
    name = forms.CharField(
        widget=forms.TextInput,
    )
    email = forms.EmailField(
        widget=forms.EmailInput,
    )
    class Meta:
        fields = ['username', 'name', 'email']

    def __init__(self, *args, **kwargs):
        super(RecoveryPwForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = '아이디'
        self.fields['username'].widget.attrs.update({
            # 'placeholder': '아이디을 입력해주세요',
            'class': 'form-control',
            'id': 'pw_form_id',
        })
        self.fields['name'].label = '이름'
        self.fields['name'].widget.attrs.update({
            # 'placeholder': '이름을 입력해주세요',
            'class': 'form-control',
            'id': 'pw_form_name',
        })
        self.fields['email'].label = '이메일'
        self.fields['email'].widget.attrs.update({
            # 'placeholder': '이메일을 입력해주세요',
            'class': 'form-control',
            'id': 'pw_form_email',
        })


# 비밀번호찾기 새 비밀번호 입력 폼
class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].label = '새 비밀번호'
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': '새 비밀번호',
        })
        self.fields['new_password2'].label = '새 비밀번호 확인'
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': '새 비밀번호 확인',
        })


# 비밀번호 변경 폼
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].label = '기존 비밀번호'
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'autofocus': False,
            'style': 'margin-top:-15px;'
        })
        self.fields['new_password1'].label = '새 비밀번호'
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
        })
        self.fields['new_password2'].label = '새 비밀번호 확인'
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
        })

# 회원가입 폼
def phone_validator(value):
    if len(str(value)) != 11:
        raise forms.ValidationError('정확한 핸드폰 번호를 입력해주세요.')


class CsRegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CsRegisterForm, self).__init__(*args, **kwargs)

        self.fields['username'].label = '아이디'
        self.fields['username'].widget.attrs.update({
            # 'class': 'form-control col-sm-10',
            'class': 'form-control',
            'autofocus': False,
            # 'placeholder': '아이디를 입력해주세요.',
        })
        self.fields['password1'].label = '비밀번호'
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': '비밀번호를 입력해주세요.',
        })
        self.fields['password2'].label = '비밀번호 확인'
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': '비밀번호를 다시 입력해주세요.',
        })
        self.fields['email'].label = '이메일'
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': '회원가입 후 입력하신 메일로 본인인증 메일이 전송됩니다.',
        })
        self.fields['name'].label = '이름'
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': "아이디, 비밀번호 찾기에 이용됩니다.",
        })
        self.fields['phone'].label = '핸드폰번호'
        self.fields['phone'].validators = [phone_validator]
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': "'-'를 제외한 숫자로 입력해주세요",
        })
        self.fields['address'].label = '주소'
        self.fields['address'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': "아이디, 비밀번호 찾기에 이용됩니다.",
        })
        """        
        self.fields['company_id'].label = '회사'
        self.fields['company_id'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': "아이디, 비밀번호 찾기에 이용됩니다.",
        })
    
        """
    """    
    company_id = forms.ChoiceField(choices=COMPANY_CHOICES, label='회사명', widget=forms.Select(
    attrs={'class': 'form-control',}), 
    )
    """ 
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'name', 'phone', 'address', 'company_id']

    def save(self, commit=True):
        user = super(CsRegisterForm, self).save(commit=False)
        user.is_active = False
        user.save()

        return user
    
"""
# 일반 회원가입 폼
class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        self.fields['username'].label = '아이디'
        self.fields['username'].widget.attrs.update({
            # 'class': 'form-control col-sm-10',
            'class': 'form-control',
            'autofocus': False,
            # 'placeholder': '아이디를 입력해주세요.',
        })
        self.fields['password1'].label = '비밀번호'
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': '비밀번호를 입력해주세요.',
        })
        self.fields['password2'].label = '비밀번호 확인'
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': '비밀번호를 다시 입력해주세요.',
        })
        self.fields['email'].label = '이메일'
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': '회원가입 후 입력하신 메일로 본인인증 메일이 전송됩니다.',
        })
        self.fields['name'].label = '이름'
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': "아이디, 비밀번호 찾기에 이용됩니다.",
        })
        self.fields['phone'].label = '핸드폰번호'
        self.fields['phone'].validators = [phone_validator]
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': "'-'를 제외한 숫자로 입력해주세요",
        })
        self.fields['address'].label = '주소'
        self.fields['address'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': "아이디, 비밀번호 찾기에 이용됩니다.",
        })
        self.fields['company_id'].label = '회사이름'
        self.fields['company_id'].validators = [company_id_validator]
        self.fields['company_id'].widget.attrs.update({
            'class': 'form-control',
            # 'placeholder': "회사이름을 입력해주세요",
        })

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'name', 'phone', 'address', 'company_id']

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.is_active = False
        user.save()

        return user
"""

# 회원정보 수정 폼
class CustomUserChangeForm(UserChangeForm):
    password = None        
    phone = forms.CharField(label='연락처', widget=forms.TextInput(
        attrs={'class': 'form-control', 'maxlength':'11', 'oninput':"maxLengthCheck(this)",}), 
    )        
    name = forms.CharField(label='이름', widget=forms.TextInput(
        attrs={'class': 'form-control', 'maxlength':'8',}), 
    )        
    address = forms.CharField(label='주소', widget=forms.TextInput(
        attrs={'class': 'form-control', 'maxlength':'100', 'oninput':"maxLengthCheck(this)",}), 
    )

    class Meta:
        model = get_user_model()
        fields = ['phone', 'name', 'address', 'company_id']

