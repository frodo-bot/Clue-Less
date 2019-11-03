# clueless/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup.as_view(), name='signup'),
    path('lobby/', views.lobby, name='lobby'),
    path('lobby/leave/', views.leaveLobby, name='lobby-leave'),
    path('lobby/players/', views.getLobbyPlayers, name='lobby-players'),
    path('game/', views.gameState, name='game'),
    path('game/clear/', views.clearState, name='clear_state'),
    path('suggestion/', views.makeSuggestion, name='suggestion'),
    path('accusation/', views.makeAccusation, name='accusation'),
    path('creategame/', views.createGame, name='creategame'),
    path('startgame/', views.startGame, name='startgame'),
    path('moveroom/', views.moveToRoom, name='moveroom'),
    path('movehall/', views.moveToHallway, name='movehall'),
    path('endturn/', views.endTurn, name='endturn'),
]
