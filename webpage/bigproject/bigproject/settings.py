from pathlib import Path
import os
import json
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/
secret_file = os.path.join(BASE_DIR, 'secrets.json')

with open(secret_file) as f:
     secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
     try:
         return secrets[setting]
     except KeyError:
         error_msg = "Set the {0} environment variable".format(setting)

         raise ImproperlyConfigured(error_msg)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'safe.apps.SafeConfig',
    'board.apps.BoardConfig',
    'common.apps.CommonConfig',
    'dash.apps.DashConfig',
    'emotion.apps.EmotionConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bigproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bigproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        # username (id나 email)과 비밀번호가 유사한지 체크
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # default 8자와 다른 최소 비밀번호 숫자를 지정할 수 있다
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        # common한 비밀번호와 체크. 기본으로 1000개의 common 비밀번호 리스트와 비교한다.
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # 전부 숫자인 비밀번호를 사용하지 못하게 한다.
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# User Login

LOGIN_URL = '/common/login/'          # 로그인 URL
LOGIN_REDIRECT_URL = '/common/main/'  # 로그인 후 URL
LOGOUT_REDIRECT_URL = '/'            # 로그아웃 후 URL
AUTH_USER_MODEL = "common.User"       # 커스텀 인증 모델
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# 네이버 SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.naver.com'
EMAIL_HOST_USER = 'rhwy12'
EMAIL_HOST_PASSWORD = get_secret("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
EMAIL_PORT = 587
DEFAULT_FROM_MAIL = 'rhwy12'

ALLOWED_HOSTS=['172.30.1.97']

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")