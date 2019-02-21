from django.conf.urls import url
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
	url(r'^favicon.ico$',
		RedirectView.as_view(url=staticfiles_storage.url('d6.ico'))
	),
	url(r'^$', views.index),
	url(r'^users/register$', views.register),
	url(r'^users/login$', views.login),
	url(r'^users/logout$', views.logout),
	url(r'^home$', views.home),
	url(r'^users/(?P<user_id>\d+)$', views.users_view),
	url(r'^users/edit$', views.users_edit),
	url(r'^users/update$', views.users_update),
	url(r'^users/(?P<user_id>\d+)/request$', views.users_request),
	url(r'^users/(?P<user_id>\d+)/accept$', views.users_accept),
	url(r'^users/(?P<user_id>\d+)/refuse$', views.users_refuse),
	url(r'^users/search$', views.users_search),
	url(r'^games/new$', views.games_new),
	url(r'^games$', views.games_create),
	url(r'^games/(?P<game_id>\d+)$', views.games_view),
	url(r'^games/(?P<game_id>\d+)/update$', views.games_update),
	url(r'^games/(?P<game_id>\d+)/delete$', views.games_delete),
	url(r'^games/(?P<game_id>\d+)/invite$', views.games_invite),
	url(r'^games/(?P<game_id>\d+)/uninvite/(?P<user_id>\d+)$', views.games_uninvite),
	url(r'^games/(?P<game_id>\d+)/remove/(?P<user_id>\d+)$', views.games_remove),
	url(r'^games/(?P<game_id>\d+)/accept$', views.games_accept),
	url(r'^games/(?P<game_id>\d+)/refuse$', views.games_refuse),
	url(r'^games/(?P<game_id>\d+)/chat$', views.games_chat),
]
