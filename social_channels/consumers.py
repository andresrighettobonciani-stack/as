import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Channel, Post
from accounts.models import GlobalChatMessage


class ChannelConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'channels_updates'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def channel_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'channel_update',
            'data': event['data']
        }))


class ChannelDetailConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.channel_slug = self.scope['url_route']['kwargs']['channel_slug']
        self.room_group_name = f'channel_{self.channel_slug}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def new_post(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_post',
            'post': event['post']
        }))

    async def member_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'member_update',
            'data': event['data']
        }))


class GlobalChatConsumer(AsyncWebsocketConsumer):
    connected_users = {}  # Changed to dict to store {user_id: display_name}
    
    async def connect(self):
        self.room_group_name = 'global_chat'
        self.user = self.scope['user']
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Add user to connected users
        GlobalChatConsumer.connected_users[self.user.id] = self.user.display_name
        
        # Get list of connected users
        users_list = list(GlobalChatConsumer.connected_users.values())
        
        # Send join notification
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user': self.user.display_name,
                'user_count': len(GlobalChatConsumer.connected_users),
                'connected_users': users_list
            }
        )
        
        # Send current user count and list to the new user
        await self.send(text_data=json.dumps({
            'type': 'user_count',
            'count': len(GlobalChatConsumer.connected_users),
            'connected_users': users_list
        }))

    async def disconnect(self, close_code):
        # Remove user from connected users and send leave notification
        if hasattr(self, 'user') and self.user.id in GlobalChatConsumer.connected_users:
            del GlobalChatConsumer.connected_users[self.user.id]
            
            users_list = list(GlobalChatConsumer.connected_users.values())
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'user': self.user.display_name,
                    'user_count': len(GlobalChatConsumer.connected_users),
                    'connected_users': users_list
                }
            )
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        message_type = data.get('message_type', 'text')
        file_url = data.get('file_url', None)
        
        print(f"[CONSUMER RECEIVE] message='{message}', type={message_type}, file_url={file_url}")
        
        # Accept message if there's text OR a file
        if (message and len(message.strip()) > 0) or file_url:
            user = self.scope['user']
            
            chat_message = await self.save_message(user, message, message_type, file_url)
            
            print(f"[CONSUMER] Saved message ID={chat_message.id}, has file={bool(chat_message.file)}")
            if chat_message.file:
                print(f"[CONSUMER] File URL: {chat_message.file.url}")
            
            message_data = {
                'id': chat_message.id,
                'user': chat_message.user.display_name,
                'message': chat_message.message,
                'message_type': chat_message.message_type,
                'created_at': chat_message.created_at.strftime('%H:%M'),
            }
            
            if chat_message.file:
                message_data['file_url'] = chat_message.file.url
                print(f"[CONSUMER] Added file_url to message_data: {message_data['file_url']}")
            else:
                print(f"[CONSUMER] No file attached to message")
            
            print(f"[CONSUMER] Broadcasting message_data: {message_data}")
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user': event['user'],
            'user_count': event['user_count'],
            'connected_users': event.get('connected_users', [])
        }))
    
    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user': event['user'],
            'user_count': event['user_count'],
            'connected_users': event.get('connected_users', [])
        }))
    
    @database_sync_to_async
    def save_message(self, user, message, message_type='text', file_url=None):
        print(f"[SAVE_MESSAGE] user={user.display_name}, message='{message}', type={message_type}, file_url={file_url}")
        
        # If file_url is provided, find the most recent message with that file
        if file_url:
            # Extract filename from URL
            filename = file_url.split('/')[-1]
            print(f"[SAVE_MESSAGE] Looking for file with filename: {filename}")
            
            # Get the most recent message from this user with this filename
            # Use select_related to preload user data
            messages = list(GlobalChatMessage.objects.select_related('user').filter(
                file__endswith=filename,
                user=user
            ).order_by('-created_at')[:1])
            
            print(f"[SAVE_MESSAGE] Found {len(messages)} messages with that file")
            
            if messages:
                chat_message = messages[0]
                print(f"[SAVE_MESSAGE] Found existing message ID={chat_message.id}, file={chat_message.file.name if chat_message.file else 'None'}")
                # Update message text if provided
                chat_message.message = message if message else chat_message.message
                chat_message.save()
                # Refresh to get updated data with user preloaded
                chat_message = GlobalChatMessage.objects.select_related('user').get(id=chat_message.id)
                return chat_message
            else:
                print(f"[SAVE_MESSAGE] No existing message found with that file")
        
        # Create new message without file
        print(f"[SAVE_MESSAGE] Creating new message without file")
        chat_message = GlobalChatMessage.objects.create(
            user=user,
            message=message,
            message_type=message_type
        )
        # Preload user relation
        chat_message = GlobalChatMessage.objects.select_related('user').get(id=chat_message.id)
        return chat_message
