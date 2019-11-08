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
        elif player[0].status == "in lobby":
            return redirect('/lobby')
        elif player[0].status == "in game":
            return redirect('/play')

    #render the main page
    return render(request, 'index.html', {})

#displays lobby page
def lobby(request):
    players = Player.objects.filter(status="in lobby")
    #if six players already in lobby, then let the user know the lobby is full
    if len(players) >= 6:
        return render(request, 'full-lobby.html', {})
    player = Player.objects.filter(user__username=request.user.username)[0]
    if player:
        player.status = "in lobby"
        player.save()
    return render(request, 'lobby.html', {})

#leave the lobby and go back to the main page
def leaveLobby(request):
    if request.user.is_authenticated:
        player = Player.objects.filter(user__username=request.user.username)[0]
        if player:
            player.status = "not in game"
            player.save()
    return redirect('/')

#returns the players currently in the lobby and a status for the player making the request
#   the status will be used to move the player from the lobby to the play game page
def getLobbyPlayers(request):
    players = Player.objects.filter(status="in lobby")
    lobby_state = {"players": [], "status": ""}
    for player in players:
        lobby_state["players"].append(player.user.username)
    player = Player.objects.filter(user__username=request.user.username)[0]
    lobby_state["status"] = player.status
    return JsonResponse(lobby_state)

#displays play game page
def playGame(request):
    if request.user.is_authenticated:
        player = Player.objects.filter(user__username=request.user.username)[0]
        if player.status == "in lobby":
            return redirect('/lobby')
        elif player.status == "not in game":
            return redirect('/')
    return render(request, 'play.html',{})

#shows the sign-up form
class signup(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


#this will create a new game using a list of usernames. NOTE: This assumes that a list of usernames
#   is provided in the request in the field "players" and a name for the game is provided in the field "name"
def createGame(request):
    player_list = []
    for name in request.POST.getlist('players[]'):
        player = Player.objects.filter(user__username=name)[0]
        player.save()
        player_list.append(player)

    game_name = request.POST.get('name', '')
    game = Game(name=game_name, status="not started")
    game.initialize(player_list)
    #create and start game together (TEMPORARY for minimal increment only)
    startGame(request)
    return JsonResponse(game.getGameState(), safe=False)

#will use the requesting user to start the game
def startGame(request):
    player = Player.objects.filter(user__username=request.user.username)[0]
    player.game.startGame()
    return JsonResponse(player.game.getGameState(), safe=False)

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
            notif = Notification(content=message, game=player.game)
            notif.save()

        gameState = player.game.getGameState()
        
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
            notif = Notification(content=message, game=player.game)
            notif.save()

        gameState = player.game.getGameState()
        
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
    if request.method == 'POST':
        name = request.user.username
        player = Player.objects.filter(user__username=name)[0]
        character = request.POST.get('character', '')
        weapon = request.POST.get('weapon', '')
        room = request.POST.get('room', '')

        message = ""
        if "Make Suggestion" in player.getValidActions():
            if room == player.currentRoom.name:
                suggPlayer = Player.objects.filter(game=player.game, character=character)
                if suggPlayer.currentRoom.name != room:
                    suggPlayer.game.board.movePlayerToRoom(suggPlayer, room)
                    message = name + " suggested that the crime was committed in the " + room + " by " + character + " with the " + weapon + ". " + character + " has been moved to the " + room + " for this suggestion."
                else:
                    message = name + " suggested that the crime was committed in the " + room + " by " + character + " with the " + weapon + ". "
                notif = Notification(content=message, game=player.game)
                notif.save()
            else:
                return JsonResponse({"error": "You must be in the room that you want to make a suggestion for."}, safe=False)
        else:
            return JsonResponse({"error": "You cannot make a suggestion at this time."}, safe=False)

    gameState = player.game.getGameState()
        
    return JsonResponse(gameState, safe=False)


#checks other player's cards for the ability to disprove a suggestion
def disproveSuggestion(request):
    return



#reponds to HTTP requests for making an accusation
def makeAccusation(request):
    if request.method == 'POST':
        name = request.user.username
        player = Player.objects.filter(user__username=name)[0]
        character = request.POST.get('character', '')
        weapon = request.POST.get('weapon', '')
        room = request.POST.get('room', '')
        
        message = ""
        if "Make Accusation" in player.getValidActions():
            message = name + " accused " + character + " of committing the crime in the " + room + " with the " + weapon + ". "
            result = player.game.checkAccusation(character, weapon, room)
            if result == True:
                message += " This accusation is correct, " + name + " has won the game!"
            else:
                message += " This accusation is incorrect, " + name + " can no longer win the game."
            notif = Notification(content=message, game=player.game)
            notif.save()
        else:
            return JsonResponse({"error": "You cannot make an accusation at this time."}, safe=False)

    gameState = player.game.getGameState()
        
    return JsonResponse(gameState, safe=False)

#ends the current players turn and updates game's current player to be the next player
def endTurn(request):
    player = Player.objects.filter(user__username=request.user.username)[0]
    game = Game.objects.filter(currentPlayer=player)[0]
    next_p = game.getNextPlayer()
    game.currentPlayer = next_p
    game.save()

    message = player.user.username + "ended their turn. It is now " + next_p.user.username + "'s turn."
    notif = Notification(content=message, game=game)
    notif.save()

    gameState = player.game.getGameState()
        
    return JsonResponse(gameState, safe=False)


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
