import os
import sys

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'PORT': 5432,
    }
}

# # Check if the tests are being run
# if 'test' in sys.argv:
#     # Use in-memory SQLite database for tests
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': ':memory:',
#         }
#     }

CORS_ORIGIN_ALLOW_ALL = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False



# django-s3-storage settings
AWS_REGION = 'us-east-2'
AWS_S3_BUCKET_AUTH = False
AWS_S3_REGION_NAME = 'us-east-2'
AWS_S3_MAX_AGE_SECONDS = 60 * 60 * 24 * 365
DEFAULT_FILE_STORAGE = 'django_s3_storage.storage.S3Storage'
AWS_S3_SIGNATURE_VERSION = 's3v4'

AWS_S3_BUCKET_NAME = 'agent-api-client-assets'

STATICFILES_LOCATION = 'static'
AWS_PUBLIC_STATIC_STORAGE_BUCKET_NAME = 'agent-public-assets-staging'

AWS_PRIVATE_MEDIA_LOCATION = 'private'
PRIVATE_FILE_STORAGE = 'agent.storage_backends.PrivateMediaStorage'
AWS_STORAGE_BUCKET_NAME = 'agent-storage'

ENVIRONMENT = 'development'

FRONTEND_BASE_URL = 'http://localhost:3000/'
SITE_URL = 'http://localhost:8000'

STATUS_CAKE_PUSH_URL = os.environ.get('STATUS_CAKE_PUSH_URL')

# CELERY settings
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
FB_CONVERSION_API_ACCESS_TOKEN = os.environ.get('FB_CONVERSION_API_ACCESS_TOKEN')
FB_CONVERSION_API_PIXEL_ID = os.environ.get('FB_CONVERSION_API_PIXEL_ID')

GOOGLE_ADS_DEVELOPER_TOKEN = os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN')
GOOGLE_ADS_USE_PROTO_PLUS = False
GOOGLE_ADS_LOGIN_CUSTOMER_ID = os.environ.get('GOOGLE_ADS_LOGIN_CUSTOMER_ID')
GOOGLE_ADS_CLIENT_ID = os.environ.get('GOOGLE_ADS_CLIENT_ID')
GOOGLE_ADS_CLIENT_SECRET = os.environ.get('GOOGLE_ADS_CLIENT_SECRET')
GOOGLE_ADS_REFRESH_TOKEN = os.environ.get('GOOGLE_ADS_REFRESH_TOKEN')

TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

AGENT_CALL_API_URL = os.environ.get('AGENT_CALL_API_URL')