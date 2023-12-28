from django import forms
# デフォルトのUserモデルを外す
# from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
# カスタムのUserモデルを適用
from .models import User, Chapter, Summary

#ファイル拡張子を指定
from django.core.validators import FileExtensionValidator 

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class LoginForm(AuthenticationForm):
    pass

class UploadForm(forms.ModelForm):
    video_path = forms.FileField(widget=forms.FileInput(attrs={'accept':'.mp4'}))
    class Meta:
        model=Chapter
        fields=['video_title', 'video_path']
        labels={
           'video_title':'タイトル',
           'video_path':'動画ファイル'
           }


    def clean_video_title(self):
        video_title = self.cleaned_data.get('video_title')

        #既存の動画と重複しているかチェック
        if Chapter.objects.filter(video_title=video_title).exists():
            raise forms.ValidationError('同じタイトルが既に存在しています。')
                
        return video_title

class ChapterForm(forms.ModelForm):         
    class Meta:
        model=Chapter
        fields=[
            'video_title',
            'chapter_data',
        ]
       

    
class SummaryForm(forms.ModelForm):
    class Meta:
        model=Summary
        fields=[           
            'summary_text'
        ]