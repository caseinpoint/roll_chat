from django.shortcuts import render, redirect
from django.contrib import messages
from apps.chat.models import *

def index(request):
	return render(request, 'chat/index.html')

def register(request):
	result = User.objects.register(request.POST)
	if not result['registered']:
		for msg in result['data']:
			messages.error(request, msg)
		return redirect('/')
	request.session['u_id'] = result['data'].id
	return redirect('/home')

def login(request):
	result = User.objects.login(request.POST)
	if not result['logged']:
		messages.error(request, result['message'])
		return redirect('/')
	request.session['u_id'] = result['u_id']
	return redirect('/home')

def logout(request):
	request.session.pop('u_id')
	messages.info(request, 'You have been logged out.')
	return redirect('/')

def home(request):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	user = User.objects.get(id=request.session['u_id'])
	context = {
		'user': user,
	}
	if user.requests_in.count() > 0:
		context['requests'] = user.requests_in.all()
	if user.invitations.count() > 0:
		context['invitations'] = user.invitations.all()
	return render(request, 'chat/home.html', context)

def users_view(request, user_id):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	user = User.objects.get(id=request.session['u_id'])
	other_user = User.objects.get(id=user_id)
	context = {
		'user': user,
		'other_user': other_user
	}
	if user.id != other_user.id and len(user.friends.filter(id=other_user.id)) == 0:
		if len(user.requests_in.filter(requester=other_user)) > 0:
			context['has_request'] = True
		elif len(user.requests_out.filter(requestee=other_user)) == 0:
			context['send_request'] = True
	elif user.id == other_user.id and user.requests_in.count() > 0:
		context['requests'] = user.requests_in.all()
	return render(request, 'chat/users_profile.html', context)

def users_edit(request):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	context = {
		'user': User.objects.get(id=request.session['u_id'])
	}
	return render(request, 'chat/users_edit.html', context)

def users_update(request):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	result = User.objects.update_user(request.POST)
	if not result['updated']:
		for msg in result['data']:
			messages.error(request, msg)
		return redirect('/users/edit')
	u_id = request.session['u_id']
	return redirect(f'/users/{u_id}')

def users_request(request, user_id):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	user = User.objects.get(id=request.session['u_id'])
	other_user = User.objects.get(id=user_id)
	print(f'Friend request from {user.id} to {other_user.id} result: ', end='')
	print(FriendRequest.objects.request(sender=user, sendee=other_user))
	return redirect('/home')

def users_accept(request, user_id):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	user = User.objects.get(id=request.session['u_id'])
	other_user = User.objects.get(id=user_id)
	print(f'Accept friend request from {other_user.id} to {user.id} result: ', end='')
	print(FriendRequest.objects.accept(sender=other_user, sendee=user))
	return redirect('/home')

def users_refuse(request, user_id):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	user = User.objects.get(id=request.session['u_id'])
	other_user = User.objects.get(id=user_id)
	print(f'Accept friend request from {other_user.id} to {user.id} result: ', end='')
	print(FriendRequest.objects.refuse(sender=other_user, sendee=user))
	return redirect('/home')

def users_search(request):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	context = {}
	if '@' in request.POST['query']:
		context['results'] = User.objects.filter(email__iexact=request.POST['query'])
	else:
		context['results'] = User.objects.filter(alias__icontains=request.POST['query'])
	if len(context['results']) == 0:
		context['none_found'] = True
	return render(request, 'chat/users_search.html', context)

def games_new(request):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	context = {
		'user': User.objects.get(id=request.session['u_id'])
	}
	return render(request, 'chat/games_new.html', context)

def games_create(request):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	result = Game.objects.create_game(request.POST)
	if not result['created']:
		messages.error(request, result['data'])
		return redirect('/games/new')
	return redirect('/home')

def games_view(request, game_id):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	user = User.objects.get(id=request.session['u_id'])
	game = Game.objects.get(id=game_id)
	context = {
		'user': user,
		'game': game
	}
	if game.gm.id == user.id:
		context['is_gm'] = True
		other_friends = user.friends.exclude(pc_games=game).exclude(invitations=game)
		# for friend in user.friends.all():
		# 	if friend not in game.players.all() and friend not in game.invitations.all():
		# 		other_friends.append(friend)
		if len(other_friends) > 0:
			context['other_friends'] = other_friends
	elif user in game.players.all():
		context['is_player'] = True
	elif user in game.invitations.all():
		context['has_invite'] = True
	return render(request, 'chat/games_view.html', context)

def games_update(request, game_id):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	user = User.objects.get(id=request.session['u_id'])
	game = Game.objects.get(id=game_id)
	if game.gm.id == user.id and len(request.POST['title']) > 1:
		game.title = request.POST['title']
		game.save()
	return redirect(f'/games/{game_id}')

def games_delete(request, game_id):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	user = User.objects.get(id=request.session['u_id'])
	game = Game.objects.get(id=game_id)
	if game.gm.id == user.id:
		game.delete()
	return redirect('/home')

def games_invite(request, game_id):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	user = User.objects.get(id=request.session['u_id'])
	game = Game.objects.get(id=game_id)
	if game.gm.id != user.id:
		return redirect(f'/games/{game_id}')
	Game.objects.invite(request.POST)
	return redirect(f'/games/{game_id}')

def games_uninvite(request, game_id, user_id):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	user = User.objects.get(id=request.session['u_id'])
	other_user = User.objects.get(id=user_id)
	game = Game.objects.get(id=game_id)
	if game.gm.id != user.id:
		return redirect(f'/games/{game_id}')
	game.invitations.remove(other_user)
	return redirect(f'/games/{game_id}')

def games_remove(request, game_id, user_id):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	user = User.objects.get(id=request.session['u_id'])
	other_user = User.objects.get(id=user_id)
	game = Game.objects.get(id=game_id)
	if game.gm.id != user.id and user.id != other_user.id:
		return redirect(f'/games/{game_id}')
	game.players.remove(other_user)
	return redirect(f'/games/{game_id}')

def games_accept(request, game_id):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	user = User.objects.get(id=request.session['u_id'])
	game = Game.objects.get(id=game_id)
	if user not in game.invitations.all():
		return redirect('/home')
	game.invitations.remove(user)
	game.players.add(user)
	return redirect(f'/games/{game_id}')

def games_refuse(request, game_id):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	user = User.objects.get(id=request.session['u_id'])
	game = Game.objects.get(id=game_id)
	game.invitations.remove(user)
	return redirect('/home')

def games_chat(request, game_id):
	if 'u_id' not in request.session:
		messages.error(request, 'You must log in first.')
		return redirect('/')
	user = User.objects.get(id=request.session['u_id'])
	game = Game.objects.get(id=game_id)
	if game.gm.id != user.id and user not in game.players.all():
		return redirect('/home')
	context = {
		'user': user,
		'game': game
	}
	if game.gm.id == user.id:
		context['is_gm'] = True
	return render(request, 'chat/chatroom.html', context)
