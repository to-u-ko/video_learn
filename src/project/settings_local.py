# Django SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'


# AWSのS3バケット名と、アクセスキーを設定必要
AWS_ACCESS_KEY_ID = 'AKIAXXXXXXXXXXXXXXXXX'
AWS_SECRET_ACCESS_KEY = 'ECn6iXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AWS_STORAGE_BUCKET_NAME = 'chaptan-XXXXX'

# AWSのS3へ、staticとmediaのアップロード設定関連
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'
AWS_DEFAULT_ACL = None
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

MEDIA_URL = 'https://%s/storage/' % (AWS_S3_CUSTOM_DOMAIN)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


# メール通知設定
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'XXXXXXXXXXX@gmail.com'
EMAIL_HOST_PASSWORD = 'aXXXXXXXXXXXXXX'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = 'XXXXXXXXXXX@gmail.com'
