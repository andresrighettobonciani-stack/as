from django.apps import AppConfig


class ChannelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social_channels'

    def ready(self):
        import social_channels.signals
