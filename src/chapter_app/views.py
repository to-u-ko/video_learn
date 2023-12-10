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
    users = User.objects.exclude(username=request.user.username)

    #chapterモデルからvideo_titleのリストを取得
    chapter_list = Chapter.objects.all()[::-1]

    params = {
        'users' : users,
        'chapter_list': chapter_list,
    }

    return render(request, 'main.html', params)


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

    params = {'form': form, 'chapter': chapter, 'chapter_lines': chapter_lines}

    return render(request, 'edit.html', params)