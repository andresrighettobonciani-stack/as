from django.db import models
from django.conf import settings
from django.utils.text import slugify
import random
import string


class Channel(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(max_length=500, blank=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_channels'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='joined_channels',
        blank=True
    )
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            if not base_slug:
                base_slug = 'channel'
            slug = base_slug
            counter = 1
            while Channel.objects.filter(slug=slug).exists():
                random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
                slug = f"{base_slug}-{random_suffix}"
                counter += 1
                if counter > 10:
                    break
            self.slug = slug
        super().save(*args, **kwargs)

    def member_count(self):
        return self.members.count()

    def is_member(self, user):
        return self.members.filter(id=user.id).exists()


class Post(models.Model):
    POST_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
    ]
    
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    content = models.TextField(max_length=2000, blank=True)
    file = models.FileField(upload_to='channel_posts/', blank=True, null=True)
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES, default='text')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.display_name} in {self.channel.name}"
