from django.shortcuts import render,redirect,get_object_or_404
from .forms import SignupForm, LoginForm, UploadForm, EditForm, SummaryForm
from django.contrib.auth import login, logout
from .create_chapter import celery_process
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages


# デフォルトのUserモデルを外す
# from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
#カスタムのUserモデルを適用
from .models import User, Chapter, Summary

import boto3
from botocore.client import Config

def signup_view(request):
    if request.method == 'POST':

        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect(to='/user/')
    else:
        form = SignupForm()
    
    params = {
        'form': form
    }

    return render(request, 'signup.html', params)

def login_view(request):
    if request.method == 'POST':
        next = request.POST.get('next')
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user:
                login(request, user)
                if next == 'None':
                    return redirect(to='/main/')
                else:
                    return redirect(to=next)
    else:
        form = LoginForm()
        next = request.GET.get('next')

    params = {
        'form': form,
        'next': next
    }

    return render(request, 'login.html', params)

def logout_view(request):
    logout(request)

    return render(request, 'logout.html')

@login_required
def user_view(request):
    user = request.user

    params = {
        'user': user
    }

    return render(request, 'user.html', params)


@login_required
def upload_view(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():        
            chapter = form.save()
            chapter.user = request.user
            chapter.save()
            print('動画アップロード完了')
            user_id = request.user.id
            celery_process.delay(user_id, chapter.id)

            return redirect('main')

    else:
        form = UploadForm()

    params = {'form': form}
    return render(request, 'upload.html', params)


@login_required
def main_view(request):
    user = request.user

    #chapterモデルからvideo_titleのリストを取得
    chapter_list = Chapter.objects.all()[::-1]

    params = {
        'user' : user,
        'chapter_list': chapter_list,
    }

    return render(request, 'main.html', params)


@login_required
def video_view(request, pk):
    chapter = get_object_or_404(Chapter, pk=pk)
    chapter_lines = chapter.chapter_data.splitlines()
    params = {'chapter': chapter, 'chapter_lines': chapter_lines}

    return render(request, 'video.html', params) 

@login_required
def chapter_edit_view(request, pk):
    chapter = get_object_or_404(Chapter, pk=pk)
    summary = get_object_or_404(Summary, chapter=chapter)
    if request.user == chapter.user:
        if request.method == 'POST':
            form = EditForm(request.POST, instance=chapter)
            if form.is_valid():
                form.save()
                return redirect('chapter_edit', pk)
        else:
            form = EditForm(instance=chapter)
            chapter_lines = chapter.chapter_data.splitlines()

        params = {'form': form, 'chapter': chapter, 'chapter_lines': chapter_lines}

        return render(request, 'chapter_edit.html', params)
    else:
        messages.error(request, '自分でアップロードした動画のみ編集可能です')
        return redirect('videl', pk)
        

@login_required
def download_transcripion_view(request, pk):
    chapter = get_object_or_404(Chapter, pk=pk)
    file_name = chapter.transcription_path

    s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME 
    
    # プリサインされたURLの生成
    presigned_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': file_name},
        ExpiresIn=3600
    )

    # ユーザーをプリサインされたURLにリダイレクト
    return HttpResponseRedirect(presigned_url)

@login_required
def summary_view(request, pk):
    user = request.user
    chapter = get_object_or_404(Chapter, pk=pk)
    summary = get_object_or_404(Summary, chapter=chapter)

    params = {'user': user, 'chapter': chapter, 'summary': summary}

    return render(request, 'summary.html', params)

@login_required
def summary_edit_view(request, pk):
    chapter = get_object_or_404(Chapter, pk=pk)
    summary = get_object_or_404(Summary, chapter=chapter)
    if request.user == chapter.user:
        if request.method == 'POST':
            form = SummaryForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('summary_edit', pk)
        else:
            form = SummaryForm(instance=summary)

        params = {'form': form, 'chapter': chapter, 'summary': summary}

        return render(request, 'summary_edit.html', params)

    else:
        messages.error(request, '自分でアップロードした動画のみ編集可能です')
        return redirect('summary', pk)