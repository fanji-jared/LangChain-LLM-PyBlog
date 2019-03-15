# -*- coding: UTF-8 -*-

"""
Django settings for my_site project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

import os
from django.utils.termcolors import colorize
from my_site import config
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'p-2_9jdgcawck*piav1d(kq-!((g#8#riop01(^5ilnl6f(ram'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = ['*']
LOGIN_URL = '/manager/login/'

# Application definition

INSTALLED_APPS = (
    'simpleui',
    'bootstrap3',
    # 'django_admin_bootstrapped',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap_pagination',
    'article',
)

# 首页图标
SIMPLEUI_HOME_ICON = 'layui-icon-rate'

BOOTSTRAP_ADMIN_SIDEBAR_MENU = True

MIDDLEWARE_CLASSES = (
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'utils.dlibs.middleware.request_init.RequestInitMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'my_site.urls'

WSGI_APPLICATION = 'my_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

MYSQLDB_CONNECT_TIMEOUT = 1
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 3600,
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'my-site',
        'USER': '',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'TEST': {
            'CHARSET': 'utf8',
            'COLLATION': 'utf8_general_ci'
        },
        'OPTIONS': {
            'connect_timeout': MYSQLDB_CONNECT_TIMEOUT,
        }
    }
}

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     }
# }
# SESSION_CACHE_ALIAS = 'default'
# CACHE_MIDDLEWARE_SECONDS = 1 * 60  # 单位秒
# CACHE_MIDDLEWARE_KEY_PREFIX = 'my_site'

EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config.EMAIL['host']
EMAIL_PORT = 25
EMAIL_HOST_USER = config.EMAIL['user']
EMAIL_HOST_PASSWORD = config.EMAIL['password']

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

LANGUAGES = (
    ('en', ('English')),
    ('zh-hans', ('中文简体')),
    # ('zh-hant', ('中文繁體')),
)

# 翻译文件所在目录，需要手工创建
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = "var/static/"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

ADMINS = {('Daniel', '1401358759@qq.com')}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
        'OPTIONS': {
            'context_processors': [
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.csrf",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# logger of libs
from utils.libs.config.logger_settings import *
# 重新更新所有handlers的filename，因为LOGGING是个DICT，在logger_conf内已经创建成功，需要再次更新
LOG_ROOT = BASE_DIR
for key, handler in LOGGING['handlers'].items():
    if handler.get('filename', None):
        # 将logs文件夹定义为项目根目录的上一层，这由docker部署目录结构决定
        handler['filename'] = os.path.join(LOG_ROOT, "../logs", os.path.basename(handler['filename']))


# import local settings
try:
    from .local_settings import *
    print colorize(text='local_settings imported.', fg='yellow')
except ImportError:
    pass
