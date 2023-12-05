from django.shortcuts import render,redirect,get_object_or_404
from .forms import SignupForm, LoginForm, UploadForm, EditForm
from django.contrib.auth import login, logout
from .create_chapter import celery_process
from django.conf import settings

# デフォルトのUserモデルを外す
# from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
#カスタムのUserモデルを適用
from .models import User, Chapter

# Djangoのメッセージ表示
from django.contrib import messages

def signup_view(request):
    if request.method == 'POST':

        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect(to='/user/')
    else:
        form = SignupForm()
    
    param = {
        'form': form
    }

    return render(request, 'signup.html', param)

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

    param = {
        'form': form,
        'next': next
    }

    return render(request, 'login.html', param)

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
            #result = celery_process.delay(user_id, video_path, video_title)

            return redirect('main')

    else:
        form = UploadForm()

    params = {'form': form}
    return render(request, 'upload.html', params)


@login_required
def main_view(request):
    users = User.objects.exclude(username=request.user.username)

    #chapterモデルからvideo_titleのリストを取得
    chapter_list = Chapter.objects.all()[::-1]

    context = {
        'users' : users,
        'chapter_list': chapter_list,
    }

    return render(request, 'main.html', context)


@login_required
def edit_view(request, pk):
    chapter = get_object_or_404(Chapter, pk=pk)
    
    if request.method == 'POST':
        form = EditForm(request.POST, instance=chapter)
        if form.is_valid():
            form.save()
            return redirect('edit', pk)
    else:
        form = EditForm(instance=chapter)
        chapter_lines = chapter.chapter_data.splitlines()
        #bucket_name = str(settings.AWS_STORAGE_BUCKET_NAME)
        #media_url = "https://" + bucket_name + ".s3.ap-northeast-1.amazonaws.com/storage"
        if chapter.status == "チャプター生成中" or chapter.status == "完了":
            transcription_url = f"/code/storage/transcriptions/trans_{chapter.video_title}.txt"            
        else:
            transcription_url = "文字起こし未完了"   

    ctx = {'form': form, 'chapter': chapter, 'chapter_lines': chapter_lines, 'transcription_url': transcription_url}

    return render(request, 'edit.html', ctx)