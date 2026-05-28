from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Message, UserStatus
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import models  # Add this line with the other imports
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
    
    context = {
        'users': users,
        'online_users': list(online_users),
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
        'id': msg.id,
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

@login_required
@csrf_exempt
def send_message_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            receiver_id = data.get('receiver_id')
            content = data.get('content')
            
            receiver = User.objects.get(id=receiver_id)
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content
            )
            return JsonResponse({
                'status': 'success', 
                'message_id': message.id,
                'message': {
                    'id': message.id,
                    'sender': message.sender.username,
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat(),
                    'is_mine': True
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)})
    
    return JsonResponse({'status': 'error', 'error': 'Invalid request'})

@login_required
def get_new_messages(request):
    last_message_id = request.GET.get('last_id', 0)
    other_user_id = request.GET.get('user_id')
    
    if not other_user_id:
        return JsonResponse({'messages': []})
    
    try:
        last_id = int(last_message_id)
        other_user = User.objects.get(id=other_user_id)
        
        # Get messages AFTER the last_id (new messages only)
        messages = Message.objects.filter(
            (models.Q(sender=request.user, receiver=other_user) |
             models.Q(sender=other_user, receiver=request.user))
        ).filter(id__gt=last_id).order_by('id')
        
        messages_data = [{
            'id': msg.id,
            'sender': msg.sender.username,
            'sender_id': msg.sender.id,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'is_mine': msg.sender == request.user
        } for msg in messages]
        
        return JsonResponse({'messages': messages_data})
    except User.DoesNotExist:
        return JsonResponse({'messages': []})
    except Exception as e:
        return JsonResponse({'messages': [], 'error': str(e)})

@login_required
def check_user_status(request):
    online_users = UserStatus.objects.filter(is_online=True).values_list('user_id', flat=True)
    return JsonResponse({'online_users': list(online_users)})

@login_required
def update_online_status(request):
    status, created = UserStatus.objects.get_or_create(user=request.user)
    status.last_seen = timezone.now()
    status.is_online = True
    status.save()
    return JsonResponse({'status': 'ok'})