# clueless/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup.as_view(), name='signup'),
    path('game/', views.gameState, name='game'),
    path('game/clear/', views.clearState, name='clear_state'),
    path('suggestion/', views.makeSuggestion, name='suggestion'),
    path('accusation/', views.makeAccusation, name='accusation'),
]
