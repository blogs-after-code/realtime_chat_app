from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Message, UserStatus
from django.views.decorators.csrf import csrf_exempt
import json

def login_view(request):
    if request.user.is_authenticated:
        return redirect('chat_room')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            return redirect('chat_room')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST.get('email', '')
        
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        
        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user)
        return redirect('chat_room')
    
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def chat_room(request):
    users = User.objects.exclude(id=request.user.id)
    online_users = UserStatus.objects.filter(is_online=True).values_list('user_id', flat=True)
    
    # Get recent messages
    recent_messages = Message.objects.filter(
        sender=request.user
    ) | Message.objects.filter(
        receiver=request.user
    ).order_by('-timestamp')[:50]
    
    context = {
        'users': users,
        'online_users': list(online_users),
        'recent_messages': recent_messages,
        'current_user': request.user
    }
    return render(request, 'chat_room.html', context)

@login_required
def get_messages(request, user_id):
    other_user = User.objects.get(id=user_id)
    messages = Message.objects.filter(
        sender=request.user, receiver=other_user
    ) | Message.objects.filter(
        sender=other_user, receiver=request.user
    ).order_by('timestamp')
    
    messages_data = [{
        'sender': msg.sender.username,
        'content': msg.content,
        'timestamp': msg.timestamp.isoformat(),
        'is_mine': msg.sender == request.user
    } for msg in messages]
    
    return JsonResponse({'messages': messages_data})

@login_required
def get_online_users(request):
    online_users = UserStatus.objects.filter(is_online=True).values_list('user_id', flat=True)
    return JsonResponse({'online_users': list(online_users)})