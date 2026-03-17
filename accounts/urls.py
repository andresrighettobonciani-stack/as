from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('home/', views.home_view, name='home'),
    path('global-chat/', views.global_chat_view, name='global_chat'),
    path('signup/', views.register_view, name='signup'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upload-chat-file/', views.upload_chat_file, name='upload_chat_file'),
]
