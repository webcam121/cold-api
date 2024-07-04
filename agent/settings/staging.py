from boto3.session import Session
from .base import *

DEBUG = True


ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'agent-api-staging.us-east-2.elasticbeanstalk.com',
    'agent-phone-staging.us-east-2.elasticbeanstalk.com',
    'agent-frontend-staging.us-east-2.elasticbeanstalk.com',
    'agent-frontend-prod.us-east-2.elasticbeanstalk.com',
    'cold-caller-api-staging.us-east-2.elasticbeanstalk.com',
    'app.agent.ai',
    'agent.ai',
    'agent-app2-dev.us-east-2.elasticbeanstalk.com',
    'test.agent.ai',
    'staging.agent.ai',
]

ec2_instance_ip = get_ec2_instance_ip()  # noqa
if ec2_instance_ip:
    ALLOWED_HOSTS.append(ec2_instance_ip)

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


SECURE_BROWSER_XSS_FILTER = True

# https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-USE_X_FORWARDED_HOST
USE_X_FORWARDED_HOST = True

# # https://docs.djangoproject.com/en/3.1/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = True

# # https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-SESSION_COOKIE_SECURE
SESSION_COOKIE_SECURE = True
#
# # https://docs.djangoproject.com/en/3.1/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True
#
# # https://docs.djangoproject.com/en/3.1/ref/middleware/#http-strict-transport-security
SECURE_HSTS_SECONDS = 60
#
# # https://docs.djangoproject.com/en/3.1/ref/settings/#secure-hsts-preload
SECURE_HSTS_PRELOAD = True
#
# # https://docs.djangoproject.com/en/3.1/ref/settings/#secure-hsts-include-subdomains
# enforcing https on request through subdomain
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# SESSION_COOKIE_SECURE = False
# CSRF_COOKIE_SECURE = False
# SECURE_SSL_REDIRECT = False

CORS_ORIGIN_ALLOW_ALL = False

CSRF_TRUSTED_ORIGINS = [
    'agent-api-staging.us-east-2.elasticbeanstalk.com',
    'agent-phone-staging.us-east-2.elasticbeanstalk.com',
    'agent-staging-backend.us-east-2.elasticbeanstalk.com',
    'agent-frontend-staging.us-east-2.elasticbeanstalk.com',
    'cold-caller-api-staging.us-east-2.elasticbeanstalk.com',
    'agent.ai',
    'app.agent.ai',
    'test.agent.ai',
    'staging.agent.ai'
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://agent-staging-backend.us-east-2.elasticbeanstalk.com',
    'http://agent-phone-staging.us-east-2.elasticbeanstalk.com',
    'http://agent-api-staging.us-east-2.elasticbeanstalk.com',
    'http://cold-caller-api-staging.us-east-2.elasticbeanstalk.com',
    'https://app.agent.ai',
    'https://test.agent.ai',
    'https://agent-frontend-staging.us-east-2.elasticbeanstalk.com',
    'https://agent.ai',
    'https://staging.agent.ai',
]

CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000'
    'https://staging.agent.ai',
    'https://agent.ai',
    'http://agent-phone-staging.us-east-2.elasticbeanstalk.com',
    'http://cold-caller-api-staging.us-east-2.elasticbeanstalk.com',
]


FRONTEND_BASE_URL = 'https://staging.agent.ai/'

# django-s3-storage settings
AWS_REGION = 'us-east-2'
AWS_S3_BUCKET_AUTH = False
AWS_S3_REGION_NAME = 'us-east-2'
AWS_S3_MAX_AGE_SECONDS = 60 * 60 * 24 * 365
DEFAULT_FILE_STORAGE = 'django_s3_storage.storage.S3Storage'
AWS_S3_SIGNATURE_VERSION = 's3v4'

AWS_S3_BUCKET_NAME = 'agent-api-client-assets'

AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_S3_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

STATICFILES_LOCATION = 'static'
AWS_LOCATION = 'static'
STATICFILES_STORAGE = 'agent.storage_backends.StaticStorage'
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
AWS_PUBLIC_STATIC_STORAGE_BUCKET_NAME = 'agent-public-assets-staging'

AWS_PRIVATE_MEDIA_LOCATION = 'private'
PRIVATE_FILE_STORAGE = 'agent.storage_backends.PrivateMediaStorage'
AWS_STORAGE_BUCKET_NAME = 'agent-storage'

# CELERY settings
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

SITE_URL = 'https://test.agent.ai'

STATUS_CAKE_PUSH_URL = os.environ.get('STATUS_CAKE_PUSH_URL')

ENVIRONMENT = 'staging'

boto3_session = Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION
)

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