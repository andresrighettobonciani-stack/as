from django.urls import path
from . import views

urlpatterns = [
    path('', views.channel_list, name='channel_list'),
    path('create/', views.channel_create, name='channel_create'),
    path('<slug:slug>/', views.channel_detail, name='channel_detail'),
    path('<slug:slug>/join/', views.channel_join, name='channel_join'),
    path('<slug:slug>/leave/', views.channel_leave, name='channel_leave'),
    path('<slug:slug>/delete/', views.channel_delete, name='channel_delete'),
]
