from django.shortcuts import render,redirect,get_object_or_404
from .forms import SignupForm, LoginForm, UploadForm, VideoForm, ChapterForm, SummaryForm
from django.contrib.auth import login, logout
from .processing import celery_process, create_thumbnail
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .models import User, Video, Chapter, Summary

import boto3
from botocore.client import Config


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
    user = request.user
    if user.is_staff:
        if request.method == 'POST':
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():        
                video = form.save()
                video.user = request.user
                video.thumbnail_path = create_thumbnail(video.id, video.video_path.url)
                video.save()
                Chapter.objects.create(video=video)
                Summary.objects.create(video=video)
                print('動画アップロード完了')               
                celery_process.delay(user.id, video.id)
                return redirect('main')

        else:
            form = UploadForm()

        params = {'form': form}
        return render(request, 'upload.html', params)
    
    else:
        messages.error(request, '講師のみ動画のアップロードが可能です')
        return redirect('main')
        


@login_required
def main_view(request):
    user = request.user
    # ユーザーがteacherの場合は全動画
    if user.is_staff:
        videos = Video.objects.all()[::-1]

    # ユーザーがstudentの場合はステータスが完了の動画のみ
    else:
        videos = Video.objects.all().filter(status='完了')[::-1] #[::-1]はpythonのスライス構文。リストを逆順にする。つまり最新のアップロードが最初に来るようになる
    
    params = {
        'user' : user,
        'videos': videos,
    }

    return render(request, 'main.html', params)


@login_required
def video_view(request, pk):
    user = request.user
    video = get_object_or_404(Video, pk=pk)
    chapter = get_object_or_404(Chapter, video=video)
    chapter_lines = chapter.chapter_text.splitlines()
    params = {'user': user, 
              'video': video, 
              'chapter': chapter, 
              'chapter_lines': chapter_lines
    }

    return render(request, 'video.html', params) 


@login_required
def chapter_edit_view(request, pk):
    video = get_object_or_404(Video, pk=pk)
    chapter = get_object_or_404(Chapter, video=video)
    if request.user == video.user:
        if request.method == 'POST':
            video_form = VideoForm(request.POST, instance=video)
            chapter_form = ChapterForm(request.POST, instance=chapter)
            if video_form.is_valid():
                video_form.save()
                if chapter_form.is_valid():
                    chapter_form.save()
                    return redirect('chapter_edit', pk)
        else:
            video_form = VideoForm(instance=video)
            chapter_form = ChapterForm(instance=chapter)
            chapter_lines = chapter.chapter_text.splitlines()

        params = {'video_form': video_form, 
                  'chapter_form': chapter_form, 
                  'video': video, 
                  'chapter': chapter, 
                  'chapter_lines': chapter_lines
        }
        return render(request, 'chapter_edit.html', params)
    
    else:
        messages.error(request, '自分でアップロードした動画のみ編集可能です')
        return redirect('video', pk)
        

@login_required
def download_transcripion_view(request, pk):
    video = get_object_or_404(Video, pk=pk)
    file_name = video.transcription_path

    boto_session = boto3.session.Session(region_name='ap-northeast-1')
    s3 = boto3.client(
        's3', 
        config=Config(signature_version='s3v4'),
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name='ap-northeast-1'
        )
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
    video = get_object_or_404(Video, pk=pk)
    summary = get_object_or_404(Summary, video=video)

    params = {'user': user, 
              'video': video, 
              'summary': summary
    }

    return render(request, 'summary.html', params)


@login_required
def summary_edit_view(request, pk):
    video = get_object_or_404(Video, pk=pk)
    summary = get_object_or_404(Summary, video=video)
    if request.user == video.user:
        if request.method == 'POST':
            form = SummaryForm(request.POST, instance=summary)
            if form.is_valid():
                form.save()
                return redirect('summary_edit', pk)
        else:
            form = SummaryForm(instance=summary)

        params = {'form': form, 
                  'video': video, 
                  'summary': summary
        }
        
        return render(request, 'summary_edit.html', params)

    else:
        messages.error(request, '自分でアップロードした動画のみ編集可能です')
        return redirect('summary', pk)