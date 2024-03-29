from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user/', views.user_view, name='user'),
    path('upload/', views.upload_view, name='upload'),
    path('main/', views.main_view, name='main'),
    path('video/<int:pk>', views.video_view, name='video'),
    path('chapter_edit/<int:pk>',views.chapter_edit_view, name='chapter_edit'),
    path('download_transcription/<int:pk>', views.download_transcripion_view, name='download_transcription'),
    path('summary/<int:pk>', views.summary_view, name='summary'),
    path('summary_edit/<int:pk>', views.summary_edit_view, name='summary_edit'),
    path('video_delete/<int:pk>', views.video_delete_view, name='video_delete'),
]