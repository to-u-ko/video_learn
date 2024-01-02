from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from mdeditor.fields import MDTextField


#ユーザーテーブルを定義
class User(AbstractUser):
    email = models.EmailField(max_length=100, unique=True)
    
    def __str__(self):
        return self.username

# 動画テーブル
class Video(models.Model):   
    def video_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        return f"storage/videos/{instance.id}.{ext}"
     
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1)
    video_title = models.CharField(max_length=255, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='処理順番待ち')
    video_path = models.FileField(upload_to=video_upload_path)
    thumbnail_path = models.CharField(max_length=256, null=True)
    transcription_path = models.CharField(max_length=256, null=True)

    def video_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        return f"storage/videos/{instance.id}.{ext}"

    def save(self, *args, **kwargs):
        if self.id is None:
        # アップロードされたファイルを変数に代入しておく
            uploaded_file = self.video_path

            # 一旦fileフィールドがNullの状態で保存(→インスタンスIDが割り当てられる)
            self.video_path= None
            super().save(*args, **kwargs)

            # fileフィールドに値をセット
            self.video_path = uploaded_file
            if "force_insert" in kwargs:
                kwargs.pop("force_insert")

        # この段階ではインスタンスIDが存在するので、_file_upload_path関数でinstance.idが使える
        super().save(*args, **kwargs)

# 動画ファイルのパス生成関数
def get_video_path(instance, filename):
    # ファイルの拡張子を取得
    ext = filename.split('.')[-1]
    # ファイル名を「id＋拡張子」として設定
    filename = f"storage/videos/video_{instance.id}.{ext}"
    return filename

# チャプターテーブル
class Chapter(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    chapter_text = models.TextField(default='チャプター生成中')
    updated_at = models.DateTimeField(auto_now=True)

# 要約テーブル
class Summary(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    summary_text = MDTextField(default='## 要約生成中')
    updated_at = models.DateTimeField(auto_now=True)
    
    

