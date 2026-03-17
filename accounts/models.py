from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import random
import string


class AnonymousUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)


class AnonymousUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    display_name = models.CharField(max_length=50, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = AnonymousUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = f"Anon_{self.generate_random_code()}"
        super().save(*args, **kwargs)

    @staticmethod
    def generate_random_code():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class GlobalChatMessage(models.Model):
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('join', 'User Joined'),
        ('leave', 'User Left'),
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
    )
    
    user = models.ForeignKey(
        'AnonymousUser',
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    message = models.TextField(max_length=500, blank=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    file = models.FileField(upload_to='chatglobal/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.display_name}: {self.message[:50]}"
