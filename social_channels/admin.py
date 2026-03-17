from django.contrib import admin
from .models import Channel, Post


class PostInline(admin.TabularInline):
    model = Post
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'creator', 'is_private', 'member_count', 'created_at')
    list_filter = ('is_private', 'created_at')
    search_fields = ('name', 'description', 'creator__username')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    filter_horizontal = ('members',)
    inlines = [PostInline]

    def member_count(self, obj):
        return obj.member_count()
    member_count.short_description = 'Members'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'channel', 'content_preview', 'created_at')
    list_filter = ('channel', 'created_at')
    search_fields = ('content', 'author__username', 'channel__name')
    readonly_fields = ('created_at', 'updated_at')

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
