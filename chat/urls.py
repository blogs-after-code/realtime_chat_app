from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.chat_room, name='chat_room'),
    path('get_messages/<int:user_id>/', views.get_messages, name='get_messages'),
    path('get_online_users/', views.get_online_users, name='get_online_users'),
]