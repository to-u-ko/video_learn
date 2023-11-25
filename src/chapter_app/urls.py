from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user/', views.user_view, name='user'),
    path('upload/', views.upload_view, name='upload'),
    path('main/', views.main_view, name='main'),
    path('edit/<int:pk>',views.edit_view, name='edit'),
    # path('celery/', views.celery, name='celery'),
]
