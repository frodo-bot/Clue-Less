# clueless/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup.as_view(), name='signup'),
    path('game/', views.getGameState, name='game'),
]
