from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from apps.chat.models import *
import json

class ChatConsumer(WebsocketConsumer):
	def connect(self):
		self.room_name = self.scope['url_route']['kwargs']['game_id']
		self.room_group_name = 'chat_%s' % self.room_name

		# Join room group
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name,
			self.channel_name
		)

		self.accept()

		for message in Game.objects.get(id=self.room_name).messages.all():
			send_data = {
				'content': message.content,
				'user_alias': message.sender.alias,
				'user_id': message.sender.id,
				'sent_at': message.sent_at.strftime('%m/%d/%y %H:%M:%S')
			}
			self.send(text_data=json.dumps(send_data))

	def disconnect(self, close_code):
		# Leave room group
		async_to_sync(self.channel_layer.group_discard)(
			self.room_group_name,
			self.channel_name
		)

	def receive(self, text_data):
		data = json.loads(text_data)
		message = Message.objects.post(
			msg_str = data['msg_str'],
			game_id = data['game_id'],
			user_id = data['user_id']
		)
		if message:
			send_data = {
				'content': message.content,
				'user_alias': message.sender.alias,
				'user_id': message.sender.id,
				'sent_at': message.sent_at.strftime('%m/%d/%y %H:%M:%S')
			}
			# Send message to room group
			async_to_sync(self.channel_layer.group_send)(
				self.room_group_name,
				{
					'type': 'chat_message',
					'data': send_data
				}
			)

	def chat_message(self, event):
		# Send message to WebSocket
		self.send(text_data=json.dumps(event['data']))
