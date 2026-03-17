from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Post


@login_required
@csrf_exempt
def upload_post_file(request):
    """Handle file uploads for channel posts"""
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        
        # Determine file type
        file_type = 'text'
        if file.content_type.startswith('image/'):
            file_type = 'image'
        elif file.content_type.startswith('audio/'):
            file_type = 'audio'
        elif file.content_type.startswith('video/'):
            file_type = 'video'
        
        # Create temporary post to get file URL
        # This will be updated when the actual post is created
        temp_post = Post(
            file=file,
            post_type=file_type,
            author=request.user,
            channel_id=1  # Temporary, will be set properly later
        )
        temp_post.save()
        
        return JsonResponse({
            'success': True,
            'file_url': temp_post.file.url,
            'file_type': file_type,
            'post_id': temp_post.id
        })
    
    return JsonResponse({'success': False, 'error': 'No file provided'})
