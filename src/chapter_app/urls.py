from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user/', views.user_view, name='user'),
    path('upload/', views.upload_view, name='upload'),
    path('main/', views.main_view, name='main'),
    path('chapter_edit/<int:pk>',views.chapter_edit_view, name='chapter_edit'),
    path('download_transcription/<int:pk>', views.download_transcripion_view, name='download_transcription'),
    path('summary_edit/<int:pk>', views.summary_edit_view, name='summary_edit')
]