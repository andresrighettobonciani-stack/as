from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Channel, Post


@receiver(post_save, sender=Channel)
def channel_created(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'channels_updates',
            {
                'type': 'channel_update',
                'data': {
                    'action': 'created',
                    'channel_id': instance.id,
                    'channel_name': instance.name,
                    'channel_slug': instance.slug,
                }
            }
        )


@receiver(post_save, sender=Post)
def post_created(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'channel_{instance.channel.slug}',
            {
                'type': 'new_post',
                'post': {
                    'author': instance.author.display_name,
                    'content': instance.content,
                    'created_at': instance.created_at.strftime('%b %d, %Y %H:%M'),
                }
            }
        )


@receiver(m2m_changed, sender=Channel.members.through)
def channel_members_changed(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove']:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'channel_{instance.slug}',
            {
                'type': 'member_update',
                'data': {
                    'action': action,
                    'member_count': instance.member_count(),
                }
            }
        )
