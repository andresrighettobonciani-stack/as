from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Channel, Post
from .forms import ChannelCreateForm, PostCreateForm
from accounts.models import GlobalChatMessage


@login_required
def channel_list(request):
    search_query = request.GET.get('search', '')
    
    public_channels = Channel.objects.filter(is_private=False)
    my_channels = request.user.joined_channels.all()
    created_channels = request.user.created_channels.all()
    
    if search_query:
        public_channels = public_channels.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        my_channels = my_channels.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        created_channels = created_channels.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Get recent chat messages for sidebar
    recent_messages = GlobalChatMessage.objects.all()[:50]
    
    context = {
        'public_channels': public_channels,
        'my_channels': my_channels,
        'created_channels': created_channels,
        'search_query': search_query,
        'recent_messages': list(reversed(recent_messages)),
    }
    return render(request, 'channels/channel_list.html', context)


@login_required
def channel_create(request):
    if request.method == 'POST':
        form = ChannelCreateForm(request.POST)
        if form.is_valid():
            channel = form.save(commit=False)
            channel.creator = request.user
            channel.save()
            channel.members.add(request.user)
            messages.success(request, f'Channel "{channel.name}" created successfully!')
            return redirect('channel_detail', slug=channel.slug)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = ChannelCreateForm()
    
    # Get recent chat messages for sidebar
    recent_messages = GlobalChatMessage.objects.all()[:50]
    
    context = {
        'form': form,
        'recent_messages': list(reversed(recent_messages)),
    }
    return render(request, 'channels/channel_create.html', context)


@login_required
def channel_detail(request, slug):
    channel = get_object_or_404(Channel, slug=slug)
    
    if channel.is_private and not channel.is_member(request.user) and channel.creator != request.user:
        messages.error(request, 'This is a private channel.')
        return redirect('channel_list')
    
    posts = channel.posts.all()
    
    if request.method == 'POST':
        if not channel.is_member(request.user):
            messages.error(request, 'You must join the channel to post.')
            return redirect('channel_detail', slug=slug)
        
        form = PostCreateForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.channel = channel
            post.author = request.user
            
            # Handle file upload
            if request.FILES.get('file'):
                file = request.FILES['file']
                post.file = file
                
                # Determine post type based on file
                if file.content_type.startswith('image/'):
                    post.post_type = 'image'
                elif file.content_type.startswith('audio/'):
                    post.post_type = 'audio'
                elif file.content_type.startswith('video/'):
                    post.post_type = 'video'
            
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('channel_detail', slug=slug)
    else:
        form = PostCreateForm()
    
    # Get recent chat messages for sidebar
    recent_messages = GlobalChatMessage.objects.all()[:50]
    
    context = {
        'channel': channel,
        'posts': posts,
        'form': form,
        'is_member': channel.is_member(request.user),
        'is_creator': channel.creator == request.user,
        'recent_messages': list(reversed(recent_messages)),
    }
    return render(request, 'channels/channel_detail.html', context)


@login_required
def channel_join(request, slug):
    channel = get_object_or_404(Channel, slug=slug)
    
    if channel.is_private:
        messages.error(request, 'Cannot join private channels.')
        return redirect('channel_detail', slug=slug)
    
    if channel.is_member(request.user):
        messages.info(request, 'You are already a member of this channel.')
    else:
        channel.members.add(request.user)
        messages.success(request, f'You joined "{channel.name}"!')
    
    return redirect('channel_detail', slug=slug)


@login_required
def channel_leave(request, slug):
    channel = get_object_or_404(Channel, slug=slug)
    
    if channel.creator == request.user:
        messages.error(request, 'Channel creators cannot leave their own channels.')
        return redirect('channel_detail', slug=slug)
    
    if channel.is_member(request.user):
        channel.members.remove(request.user)
        messages.success(request, f'You left "{channel.name}".')
        return redirect('channel_list')
    else:
        messages.info(request, 'You are not a member of this channel.')
        return redirect('channel_detail', slug=slug)


@login_required
def channel_delete(request, slug):
    channel = get_object_or_404(Channel, slug=slug)
    
    if channel.creator != request.user:
        messages.error(request, 'Only the channel creator can delete it.')
        return redirect('channel_detail', slug=slug)
    
    if request.method == 'POST':
        channel_name = channel.name
        channel.delete()
        messages.success(request, f'Channel "{channel_name}" deleted successfully.')
        return redirect('channel_list')
    
    # Get recent chat messages for sidebar
    recent_messages = GlobalChatMessage.objects.all()[:50]
    
    context = {
        'channel': channel,
        'recent_messages': list(reversed(recent_messages)),
    }
    return render(request, 'channels/channel_delete.html', context)
