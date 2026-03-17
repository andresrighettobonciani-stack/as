from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import AnonymousUserRegistrationForm, AnonymousUserLoginForm
from .models import GlobalChatMessage


def landing_view(request):
    """SEO-optimized landing page for anonymous social network"""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'landing.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AnonymousUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to the network, {user.display_name}!')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = AnonymousUserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AnonymousUserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.display_name}!')
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AnonymousUserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def home_view(request):
    recent_messages = GlobalChatMessage.objects.all()[:50]
    context = {
        'recent_messages': list(reversed(recent_messages)),
    }
    return render(request, 'accounts/home.html', context)


@login_required
def global_chat_view(request):
    recent_messages = GlobalChatMessage.objects.all()[:50]
    context = {
        'recent_messages': list(reversed(recent_messages)),
    }
    return render(request, 'accounts/global_chat.html', context)


@login_required
@csrf_exempt
def upload_chat_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        
        # Determine file type
        file_type = file.content_type.split('/')[0]
        if file_type not in ['image', 'audio', 'video']:
            return JsonResponse({'error': 'Invalid file type'}, status=400)
        
        # Create a temporary message object to save the file
        chat_message = GlobalChatMessage(
            user=request.user,
            message='',
            message_type=file_type,
            file=file
        )
        chat_message.save()
        
        return JsonResponse({
            'success': True,
            'file_url': chat_message.file.url,
            'file_type': file_type,
            'message_id': chat_message.id
        })
    
    return JsonResponse({'error': 'No file provided'}, status=400)
