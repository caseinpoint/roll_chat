from django.db import models
import bcrypt
import json
import random
import re

random.seed()
EMAIL_REGEX = re.compile(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')
ALIAS_REGEX = re.compile(r'^[a-zA-Z0-9_-]+$')
DICE_REGEX = re.compile(r'/[rR](oll)?\s*(?P<num>\d*)?[dD](?P<side>\d+)((?P<pos>[+-])(?P<mod>\d+))?')

class UserManager(models.Manager):
	def register(self, post_data):
		result = {'registered': False, 'data': []}

		if len(post_data['alias']) < 2:
			result['data'].append('Alias must be at least 2 characters.')
		elif len(post_data['alias']) > 31:
			result['data'].append('Alias must be at most 31 characters.')
		elif not ALIAS_REGEX.match(post_data['alias']):
			result['data'].append('Alias can only contain letters, numbers, hyphens and underscores.')
		elif len(self.filter(alias__iexact=post_data['alias'])) > 0:
			result['data'].append('That alias is already taken.')
		if len(post_data['email']) < 1:
			result['data'].append('Email is required.')
		elif len(post_data['email']) > 127:
			result['data'].append('Your email is way too long.')
		elif not EMAIL_REGEX.match(post_data['email']):
			result['data'].append('Invalid email address.')
		elif len(self.filter(email__iexact=post_data['email'])) > 0:
			result['data'].append('That email is already registered, please log in.')
		if len(post_data['password']) < 8:
			result['data'].append('Password must be at least 8 characters.')
		if post_data['confirm_password'] != post_data['password']:
			result['data'].append('Passwords must match.')

		if len(result['data']) > 0:
			return result

		result['data'] = self.create(
			alias = post_data['alias'],
			email = post_data['email'],
			password = bcrypt.hashpw(post_data['password'].encode(), bcrypt.gensalt()),
			pic_url = post_data['pic_url']
		)
		welcome_game = Game.objects.get(id=1)
		result['data'].pc_games.add(welcome_game)
		result['registered'] = True
		return result

	def update_user(self, post_data):
		user = self.get(id=post_data['u_id'])
		result = {'updated': False, 'data': []}

		if len(post_data['alias']) < 2:
			result['data'].append('Alias must be at least 2 characters.')
		elif len(post_data['alias']) > 31:
			result['data'].append('Alias must be at most 31 characters.')
		elif not ALIAS_REGEX.match(post_data['alias']):
			result['data'].append('Alias can only contain letters, numbers, hyphens and underscores.')
		elif (user.alias != post_data['alias'] and
			len(self.filter(alias__iexact=post_data['alias'])) > 0):
			result['data'].append('That alias is already taken.')
		if len(post_data['email']) < 1:
			result['data'].append('Email is required.')
		elif len(post_data['email']) > 127:
			result['data'].append('Your email is way too long.')
		elif not EMAIL_REGEX.match(post_data['email']):
			result['data'].append('Invalid email address.')
		elif (user.email != post_data['email'] and
			len(self.filter(email__iexact=post_data['email'])) > 0):
			result['data'].append('That email is already registered to another account.')
		if len(post_data['password']) > 0 and len(post_data['password']) < 8:
			result['data'].append('Password must be at least 8 characters.')
		if post_data['confirm_password'] != post_data['password']:
			result['data'].append('Passwords must match.')

		if len(result['data']) > 0:
			return result

		user.alias = post_data['alias']
		user.email = post_data['email']
		if len(post_data['password']) > 7:
			user.password = bcrypt.hashpw(post_data['password'].encode(), bcrypt.gensalt())
		user.pic_url = post_data['pic_url']
		user.save()
		result['updated'] = True
		return result

	def login(self, post_data):
		result = {'logged': False}
		users = self.filter(email__iexact=post_data['email'])

		if len(users) == 0:
			print('Email not found in DB.')
			result['message'] = 'Invalid login.'
			return result
		if not bcrypt.checkpw(post_data['password'].encode(), users[0].password.encode()):
			print('Passwords don\'t match.')
			result['message'] = 'Invalid login.'
			return result

		result['logged'] = True
		result['u_id'] = users[0].id
		return result

class User(models.Model):
	# SlugField only allows letters, numbers, hyphens, underscores
	alias = models.SlugField(max_length=31, unique=True)
	email = models.EmailField(max_length=127, unique=True)
	pic_url = models.TextField(blank=True)
	password = models.CharField(max_length=63)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	# requests = models.ManyToManyField('self')
	friends = models.ManyToManyField('self')

	objects = UserManager()

	def __str__(self):
		return f'id = {self.id}, alias = "{self.alias}"'

class FriendRequestManager(models.Manager):
	def request(self, sender, sendee):
		if sender.id == sendee.id:
			return False
		elif sendee in sender.friends.all():
			return False
		elif (
			len(sender.requests_out.filter(requestee=sendee)) > 0 or len(sender.requests_in.filter(requester=sendee)) > 0):
			return False
		else:
			self.create(requester=sender, requestee=sendee)
			return True
	def accept(self, sender, sendee):
		reqs = self.filter(requester=sender).filter(requestee=sendee)
		if len(reqs) == 0:
			return False
		else:
			sender.friends.add(sendee)
			reqs[0].delete()
			return True
	def refuse(self, sender, sendee):
		reqs = self.filter(requester=sender).filter(requestee=sendee)
		if len(reqs) == 0:
			return False
		else:
			reqs[0].delete()
			return True

class FriendRequest(models.Model):
	requester = models.ForeignKey(User, related_name='requests_out')
	requestee = models.ForeignKey(User, related_name='requests_in')

	objects = FriendRequestManager()

	def __str__(self):
		return f'id = {self.id}, requester.id = {self.requester.id}, requestee.id = {self.requestee.id}'

class GameManager(models.Manager):
	def create_game(self, post_data):
		result = {
			'created': False
		}

		if len(post_data['title']) < 2:
			result['data'] = 'The game title must be at least 2 characters.'
			return result;

		user = User.objects.get(id=post_data['u_id'])
		result['data'] = self.create(
			title = post_data['title'],
			gm = user
		)
		inv_lst = post_data.getlist('invitations')
		if len(inv_lst) > 0:
			for friend in User.objects.filter(id__in=inv_lst):
				result['data'].invitations.add(friend)
		result['created'] = True
		return result
	def invite(self, post_data):
		inv_lst = post_data.getlist('invitations')
		if len(inv_lst) == 0:
			return False
		else:
			game = self.get(id=post_data['game_id'])
			for friend in User.objects.filter(id__in=inv_lst):
				game.invitations.add(friend)
			return True

class Game(models.Model):
	title = models.CharField(max_length=127, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	gm = models.ForeignKey(User, related_name='gm_games')
	invitations = models.ManyToManyField(User, related_name='invitations')
	players = models.ManyToManyField(User, related_name='pc_games')

	objects = GameManager()

	def __str__(self):
		return f'id = {self.id}, title = "{self.title}"'

class MessageManager(models.Manager):
	def post(self, game_id, user_id, msg_str):
		user = User.objects.get(id=user_id)
		game = Game.objects.get(id=game_id)
		if game.gm.id != user.id and user not in game.players.all():
			return None

		msg_str = msg_str.lstrip().rstrip()
		if len(msg_str) == 0:
			return None

		match = DICE_REGEX.search(msg_str)

		if not match:
			return self.create(
				content = msg_str,
				game = game,
				sender = user
			)
		else:
			parsed = match.groupdict()
			if parsed['num']:
				parsed['num'] = int(parsed['num'])
			else:
				parsed['num'] = 1
			parsed['side'] = int(parsed['side'])
			if parsed['mod']:
				parsed['mod'] = int(parsed['mod'])

			if parsed['num'] > 25:
				msg_str += '\nROLL_ERROR: maximum number of dice is 25.'
			elif parsed['num'] == 0:
				msg_str += '\nROLL_ERROR: number of dice must blank or greater than 0.'
			elif parsed['side'] < 1:
				msg_str += '\nROLL_ERROR: die size must be greater than 0.'
			elif parsed['side'] > 120:
				msg_str += '\nROLL_ERROR: maximum die size is d120.'
			else:
				total = 0
				rolls = []
				for i in range(parsed['num']):
					result = random.randint(1, parsed['side'])
					rolls.append(result)
					total += result
				if parsed['pos'] == '+':
					total += parsed['mod']
				elif parsed['pos'] == '-':
					total -= parsed['mod']

				msg_str += '\nROLL_RESULT: ' + str(total) + ' = ' + json.dumps(rolls)
				if parsed['pos']:
					msg_str += ' ' + parsed['pos'] + ' ' + str(parsed['mod'])

			return self.create(
				content = msg_str,
				game = game,
				sender = user
			)

class Message(models.Model):
	content = models.TextField(blank=False)
	sent_at = models.DateTimeField(auto_now_add=True)

	game = models.ForeignKey(Game, related_name='messages')
	sender = models.ForeignKey(User, related_name='messages')

	objects = MessageManager()

	def __str__(self):
		return f'id = {self.id}, game_id = {self.game.id}, sender_id = {self.sender.id}'

# class Roll(models.Model):
# 	# string seems the best way to store the roll, for now
# 	# rather than separate fields for number, sides, modifier, etc.
# 	# single type of die with single modifier, for now
# 	roll_str = models.CharField(max_length=15) # max_length=15 for now
# 	# generate list of results, then encode as string using json.dumps()
# 	results = models.TextField()
# 	total = models.SmallIntegerField() # values from -32768 to 32767
#
# 	message = models.OneToOneField(Message, related_name='roll', primary_key=True)
#
# 	# objects = RollManager()
#
# 	def __str__(self):
# 		return f'msg_id = {self.message.id}, total = {self.total}'
