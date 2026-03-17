from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import AnonymousUser, GlobalChatMessage


class AnonymousUserAdmin(BaseUserAdmin):
    list_display = ('username', 'display_name', 'created_at', 'is_active', 'is_staff')
    list_filter = ('is_staff', 'is_active', 'created_at')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('display_name', 'bio')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    readonly_fields = ('created_at',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'display_name')
    ordering = ('-created_at',)


admin.site.register(AnonymousUser, AnonymousUserAdmin)


@admin.register(GlobalChatMessage)
class GlobalChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__display_name', 'message')
    readonly_fields = ('created_at',)

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
