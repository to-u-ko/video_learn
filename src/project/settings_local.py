# Django SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-3avz^1(ara704kwrc4r%72-w^c+u5cd16*jgl2^tt3=fi7le7d'


# AWSのS3バケット名と、アクセスキーを設定必要
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = 'AKIAY5FXWUZITVMCS7GH'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 's3-chapter'


# メール通知設定
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'apuritesuto7@gmail.com'
EMAIL_HOST_PASSWORD = 'hytftlicleqpbfmp'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = 'apuritesuto7@gmail.com'