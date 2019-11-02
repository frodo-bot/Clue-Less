# Create your views here.
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse
from .models import Accusation, Suggestion, Player, Game
from django.contrib.auth.models import User

#displays main page
def index(request):
    #if a Player object doesn't exist for the current User, create it and save to DB
    if request.user.is_authenticated:
        player = Player.objects.filter(user__username=request.user.username)
        if not player:
            current_user = User.objects.filter(username=request.user.username)
            player = Player(user=current_user[0], status="not in game")
            player.save()
    
    #render the main page
    return render(request, 'index.html', {})

#shows the sign-up form
class signup(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

def createGame(request):
    # I was just testing stuff in here, this will change when I actually write the views
    #game = Game(name="test game 2", status="not started")
    #player1 = Player.objects.filter(user__username=request.user.username)[0]
    #player2 = Player.objects.filter(user__username="frodo")[0]
    #game.initialize([player1, player2])
    return


def startGame(request):
    # I was just testing stuff in here, this will change when I actually write the views
    #game = Game.objects.filter(pk=5)[0]
    #print(game.getUnplayedCharacters())
    #player = game.currentPlayer
    #game.board.movePlayerToHallway(player, "Hall - Lounge")
    #next_p = game.getNextPlayer()
    #game.currentPlayer = next_p
    #game.save()
    #next_p = game.getNextPlayer()
    #print(next_p.user.username)
    #print(next_p.character)
    #game.startGame()
    return

#returns the game state to the polling client
def gameState(request):
    name = request.GET.get('name', '')

    #query for all accusations made by current user and return
    queryset_acc = Accusation.objects.filter(user=name)
    acc_list = []
    for item in queryset_acc:
        acc_list.append(item.text)

    #query for all suggestions and return list
    queryset_sug = Suggestion.objects.all()
    sug_list = []
    for item in queryset_sug:
        sug_list.append(item.text)

    data = {
        "suggestions" : sug_list,
        "accusations" : acc_list
    }
    return JsonResponse(data)

#reponds to HTTP requests for making an accusation
def makeAccusation(request):
    global accusations
    if request.method == 'POST':
        name = request.POST.get('name', '')
        if name:
            character = request.POST.get('character', '')
            weapon = request.POST.get('weapon', '')
            room = request.POST.get('room', '')
            accusationStr = name + " made an accusation: " + character + ", " + weapon + ", " + room
            
            #create accusation object and save it to database
            acc = Accusation(user=name, text=accusationStr)
            acc.save()

    #query for all accusations made by current user and return
    queryset = Accusation.objects.filter(user=name)
    acc_list = []
    for item in queryset:
        acc_list.append(item.text)

    return JsonResponse({"accusations" : acc_list})

#responds to HTTP request for making a suggestion
def makeSuggestion(request):
    global suggestions
    if request.method == 'POST':
        name = request.POST.get('name', '')
        character = request.POST.get('character', '')
        weapon = request.POST.get('weapon', '')
        room = request.POST.get('room', '')
        suggestionStr = name + " made an suggestion: " + character + ", " + weapon + ", " + room

        #create suggestion object and save it to database
        sug = Suggestion(user=name, text=suggestionStr)
        sug.save()

    #query for all suggestions and return list
    queryset = Suggestion.objects.all()
    sug_list = []
    for item in queryset:
        sug_list.append(item.text)

    return JsonResponse({"suggestions" : sug_list})

#clears the database (TEMPORARY for skeletal increment only)
def clearState(request):
    global suggestions
    global accusations
    if request.method == 'POST':
        #delete all suggestions from database
        queryset = Suggestion.objects.all()
        queryset.delete()

        #delete user's accusations from database
        name = request.POST.get('name', '')
        print(name)
        queryset = Accusation.objects.filter(user=name)
        queryset.delete()

    data = {
        "suggestions" : [],
        "accusations" : []
    }
    return JsonResponse(data)
