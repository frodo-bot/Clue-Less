# Create your views here.
from django.shortcuts import render
from django.shortcuts import redirect
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

def lobby(request):
    player = Player.objects.filter(user__username=request.user.username)[0]
    if player:
        player.status = "in lobby"
        player.save()
    return render(request, 'lobby.html', {})

def leaveLobby(request):
    player = Player.objects.filter(user__username=request.user.username)[0]
    if player:
        player.status = "not in game"
        player.save()
    return redirect('/')

def getLobbyPlayers(request):
    players = Player.objects.filter(status="in lobby")
    player_names = {"players": []}
    for player in players:
        player_names["players"].append(player.user.username)
    return JsonResponse(json.dumps(player_names))

#shows the sign-up form
class signup(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


#this will create a new game using a list of usernames. NOTE: This assumes that a list of usernames
#   is provided in the request in the field "players" and a name for the game is provided in the field "name"
def createGame(request):
    player_list = []
    for name in request.POST.get('players', ''):
        player = Player.objects.filter(user__username=name)[0]
        player_list.append(player)

    game_name = request.POST.get('name', '')
    game = Game(name=game_name, status="not started")
    game.initialize(player_list)
    return JsonResponse(game.getGameState())

#will use the requesting user to start the game
def startGame(request):
    player = Player.objects.filter(user__username=request.user.username)[0]
    player.game.startGame()
    return JsonResponse(player.game.getGameState())

#will check room against valid moves, and then move the player there. Will return success or failure
#   message with game state
def moveToRoom(request):
    if request.method == 'POST':
        name = request.user.username
        room = request.POST.get('room', '')
        player = Player.objects.filter(user__username=name)[0]
        message = ""
        if room in player.getValidMoves():
            player.game.board.movePlayerToRoom(player, room)
            message = name + " (" + player.character + ") " + "moved to the " + room
        else:
            message = name + " (" + player.character + ") " + "tried to move to the " + room + ", which is an invalid move"

        gameState = json.loads(player.game.getGameState())
        gameState["message"] = message
        gameState["messageFor"] = "all"
        gameState = json.dumps(gameState)

    return JsonResponse(gameState, safe=False)

#will check hallway against valid moves, and then move the player there. Will return success or failure
#   message with game state
def moveToHallway(request):
    if request.method == 'POST':
        name = request.user.username
        hallway = request.POST.get('hallway', '')
        player = Player.objects.filter(user__username=name)[0]
        message = ""
        if hallway in player.getValidMoves():
            player.game.board.movePlayerToHallway(player, hallway)
            message = name + " (" + player.character + ") " + "moved to the " + hallway + " hallway"
        else:
            message = name + " (" + player.character + ") " + "tried to move to the " + hallway + " hallway, which is an invalid move"

        gameState = json.loads(player.game.getGameState())
        gameState["message"] = message
        gameState["messageFor"] = "all"
        gameState = json.dumps(gameState)

    return JsonResponse(gameState, safe=False)

#return the valid moves in a JSON in the format {"rooms": <list of valid rooms>, "hallways":<list of valid hallways>}
def validMoves(request):
    player = Player.objects.filter(user__username=request.user.username)[0]
    move_list = player.getValidMoves()
    moves = {
        "rooms": [],
        "hallways": [],
    }
    for move in move_list:
        if "-" in move:
            moves["hallways"].append(move)
        else:
            moves["rooms"].append(move)

    return JsonResponse(json.dumps(moves), safe=False)


#responds to HTTP request for making a suggestion
def makeSuggestion(request):
    return


#checks other player's cards for the ability to disprove a suggestion
def disproveSuggestion(request):
    return



#reponds to HTTP requests for making an accusation
def makeAccusation(request):
    return

#ends the current players turn and updates game's current player to be the next player
def endTurn(request):
    player = Player.objects.filter(user__username=request.user.username)[0]
    game = Game.objects.filter(currentPlayer=player)[0]
    next_p = game.getNextPlayer()
    game.currentPlayer = next_p
    game.save()
    response = {"message": player.user.username + "ended turn. It is now " + next_p.user.username + "'s turn.",
                "messageFor": "all"
                }
    return JsonResponse(json.dumps(response), safe=False)


#returns the game state to the polling client
def gameState(request):
    player = Player.objects.filter(user__username=request.user.username)[0]
    return JsonResponse(player.game.getGameState(), safe=False)


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
