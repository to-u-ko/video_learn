from django.db import models
from django.contrib.auth.models import AbstractUser


#ユーザーテーブルを定義
class User(AbstractUser):
    email = models.EmailField(max_length=100, unique=True)

    def __str__(self):
        return self.username

# 動画ファイルのパス生成関数
def video_directory_path(instance, filename):
    # ファイルの拡張子を取得
    ext = filename.split('.')[-1]
    # video_titleをファイル名の一部として使用
    video_title = instance.video_title
    # ファイル名をカスタマイズ
    filename = f"storage/videos/{video_title}.{ext}"
    return filename

#チャプターテーブルを定義
class Chapter(models.Model):
    user         = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1)
    video_title  = models.CharField(max_length=255, unique=True)
    chapter_data = models.TextField(default='チャプター生成中')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    status       = models.CharField(max_length=50, default='処理順番待ち')
    video_path   = models.FileField(upload_to=video_directory_path)
    transcription_path = models.CharField(max_length=256, null=True)

    def __str__(self):
        return self.video_title


    

