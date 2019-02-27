from django.core.management.base import BaseCommand, CommandError
from apps.chat.models import Message, User
from datetime import datetime, timedelta
import pytz

class Command(BaseCommand):
	args = ''
	help = 'Clears messages older than 2 months from the database.'

	def handle(self, *args, **options):
		two_months = datetime.now(tz=pytz.utc) - timedelta(days=60)
		Message.objects.filter(sent_at__lte=two_months).exclude(sender__id=4).delete()
