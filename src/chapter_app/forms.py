from django import forms
# デフォルトのUserモデルを外す
# from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
# カスタムのUserモデルを適用
from .models import User, Video, Chapter, Summary

#ファイル拡張子を指定
from django.core.validators import FileExtensionValidator 

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class LoginForm(AuthenticationForm):
    pass

class UploadForm(forms.ModelForm):
    video_path = forms.FileField(widget=forms.FileInput(attrs={'accept':'.mp4'}), label='動画ファイル')
    class Meta:
        model=Video
        fields=['video_title', 'video_path']
        labels={
           'video_title':'タイトル',
           }

    def clean_video_title(self):
        video_title = self.cleaned_data.get('video_title')

        #既存の動画と重複しているかチェック
        if Video.objects.filter(video_title=video_title).exists():
            raise forms.ValidationError('同じタイトルが既に存在しています。')
                
        return video_title

class VideoForm(forms.ModelForm):
    class Meta:
        model=Video
        fields=[
            'video_title',
        ]
        labels = {
            'video_title' : '動画タイトル'
        }

class ChapterForm(forms.ModelForm):         
    class Meta:
        model=Chapter
        fields=[
            'chapter_text',
        ]
        labels = {
            'chapter_text': 'チャプター'
        }
       
    
class SummaryForm(forms.ModelForm):
    class Meta:
        model=Summary
        fields=[           
            'summary_text'
        ]