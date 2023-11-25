from django import forms
# デフォルトのUserモデルを外す
# from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
# カスタムのUserモデルを適用
from .models import User, Chapter

#ファイル拡張子を指定
from django.core.validators import FileExtensionValidator 

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class LoginForm(AuthenticationForm):
    pass

class UploadForm(forms.Form):
    video_title = forms.CharField(max_length=256,label='動画タイトル')
    video_file = forms.FileField(widget=forms.FileInput(attrs={'accept':'.mp4'}),label='動画ファイル')

    def clean_video_title(self):
        video_title = self.cleaned_data.get('video_title')

        #既存の動画と重複しているかチェック
        if Chapter.objects.filter(video_title=video_title).exists():
            raise forms.ValidationError('同じタイトルが既に存在しています。')
        
        return video_title

class EditForm(forms.ModelForm):
    class Meta:
        model=Chapter
        fields=[
            'video_title',
            'chapter_data',
        ]
        labels={
           'video_title':'タイトル',
           'chapter_data':'チャプター',
           }

    