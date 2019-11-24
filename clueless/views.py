# Create your views here.
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
import json
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse
from .models import Player, Game, Card, Notification
from django.contrib.auth.models import User
from time import sleep

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

#returns the players currently in the game
def getGamePlayers(request):
    player = Player.objects.filter(user__username=request.user.username)[0]
    players = Player.objects.filter(game=player.game, unplayed=False)
    game_players = {"players" : []}
    for player in players:
        if player.user:
            game_players["players"].append(player.character + " - " + player.user.username)
    return JsonResponse(game_players)

#shows the sign-up form
class signup(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


#this will create a new game using a list of usernames. NOTE: This assumes that a list of usernames
#   is provided in the request in the field "players" and a name for the game is provided in the field "name"
def createGame(request):
    request_player = Player.objects.filter(user__username=request.user.username)[0]
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
    return JsonResponse(game.getGameState(request_player), safe=False)

#will use the requesting user to start the game
def startGame(request):
    player = Player.objects.filter(user__username=request.user.username)[0]
    player.game.startGame()
    return JsonResponse(player.game.getGameState(player), safe=False)

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

    gameState = player.game.getGameState(player)
        
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

    gameState = player.game.getGameState(player)
        
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


#return the valid moves in a JSON in the format {"rooms": <list of valid rooms>, "hallways":<list of valid hallways>}
def playerCards(request):
    player = Player.objects.filter(user__username=request.user.username)[0]
    cards = Card.objects.filter(owner=player)
    card_list = []
    for card in cards:
        card_list.append(card.name)

    return JsonResponse({"cardList": card_list}, safe=False)

#responds to HTTP request for making a suggestion
def makeSuggestion(request):
    if request.method == 'POST':
        name = request.user.username
        player = Player.objects.filter(user__username=name)[0]
        character = request.POST.get('character', '')
        weapon = request.POST.get('weapon', '')
        room = player.currentRoom
        suggestion = [room.name, weapon, character]
        game = player.game

        message = ""
        if "Make Suggestion" in player.getValidActions():
            if room != None:
                suggPlayer = Player.objects.filter(game=player.game, character=character)[0]
                if not suggPlayer.inRoom() or suggPlayer.currentRoom.name != room.name:
                    suggPlayer.game.board.movePlayerToRoom(suggPlayer, room.name)
                    message = name + " suggested that the crime was committed in the " + room.name + " by " + character + " with the " + weapon + ". " + character + " has been moved to the " + room.name + " for this suggestion."
                    suggPlayer.movedBySuggestion = True
                    suggPlayer.save()
                else:
                    message = name + " suggested that the crime was committed in the " + room.name + " by " + character + " with the " + weapon + ". "
                notif = Notification(content=message, game=player.game)
                notif.save()
                player.hasMadeSuggestionThisTurn = True
                player.hasMadeSuggestionInRoom = True
                player.save()
                game.disprovePlayer = game.getNextPlayer(player).user.username
                game.currentSuggestion = character + "," + room.name + "," + weapon
                game.save()
            else:
                return JsonResponse({"error": "You must be in the room that you want to make a suggestion for."}, safe=False)
        else:
            return JsonResponse({"error": "You cannot make a suggestion at this time."}, safe=False)

    #gameStateJson = disproveSuggestion(request)
    gameStateJson = game.getGameState(player)
    return JsonResponse(gameStateJson, safe=False)


def disproveSuggestion(request):
    if request.method == 'POST':
        name = request.user.username
        disprovePlayer = Player.objects.filter(user__username=name)[0]
        game = disprovePlayer.game
        suggPlayer = game.currentPlayer
        card = request.POST.get('card', '')
        forfeit = request.POST.get('forfeit', '')

        if forfeit == True:
            if game.getNextPlayer(disprovePlayer).user.username == suggPlayer.user.username:
                message = "No one could disprove " + suggPlayer.user.username + "'s suggestion."
                notif = Notification(content=message, game=suggPlayer.game)
                notif.save()
                game.disprovePlayer = None
                game.currentSuggestion = None
                game.save()
            else:
                message = name + " could not disprove " + suggPlayer.user.username + "'s suggestion."
                notif = Notification(content=message, game=suggPlayer.game)
                notif.save()
                game.disprovePlayer = game.getNextPlayer(disprovePlayer).user.username
                game.save()

            gameState = game.getGameState(suggPlayer)
            return JsonResponse(gameState, safe=False)

        queryset = Card.objects.filter(owner=disprovePlayer, game=game)
        player_cards = []
        for item in queryset:
            player_cards.append(item)

        matches = game.checkSuggestion(player_cards, game.currentSuggestion.split(","))
        if card in matches:
            message = name + " disproved " + suggPlayer.user.username + "'s suggestion."
            notif = Notification(content=message, game=suggPlayer.game)
            notif.save()
            game.specialMessage = disprovePlayer.user.username + " disproved your suggestion with the "  + card + " card."
            game.disprovePlayer = None
            game.currentSuggestion = None
            game.save()
        else:
            if game.getNextPlayer(disprovePlayer).user.username == suggPlayer.user.username:
                message = "No one could disprove " + suggPlayer.user.username + "'s suggestion."
                notif = Notification(content=message, game=suggPlayer.game)
                notif.save()
                game.disprovePlayer = None
                game.currentSuggestion = None
                game.save()
            else:
                message = name + " could not disprove " + suggPlayer.user.username + "'s suggestion."
                notif = Notification(content=message, game=suggPlayer.game)
                notif.save()
                game.disprovePlayer = game.getNextPlayer(disprovePlayer).user.username
                game.save()

        gameState = game.getGameState(suggPlayer)
        return JsonResponse(gameState, safe=False)




#checks other player's cards for the ability to disprove a suggestion
#call this from the client that made the suggestion
""" def disproveSuggestion(request):
    if request.method == 'POST':
        print("HELLO WORLD ", request.user.username)
        name = request.user.username
        suggPlayer = Player.objects.filter(user__username=name)[0]
        game = suggPlayer.game
        disprovePlayer = game.getNextPlayer(suggPlayer)
        character = request.POST.get('character', '')
        weapon = request.POST.get('weapon', '')
        room = suggPlayer.currentRoom.name

        sleep(5)

        disproved = False
        while disprovePlayer.user.username != suggPlayer.user.username:
            queryset = Card.objects.filter(owner=disprovePlayer, game=game)
            player_cards = []
            for item in queryset:
                player_cards.append(item)
            
            matches = game.checkSuggestion(player_cards, [character, weapon, room])
            message = ""
            if len(matches) > 0:
                message = disprovePlayer.user.username + " disproved " + name + "'s suggestion."
                notif = Notification(content=message, game=suggPlayer.game)
                notif.save()
                game.specialMessage = disprovePlayer.user.username + " disproved your suggestion with the "  + matches[0] + " card."
                game.save()
                disprovePlayer = suggPlayer
                disproved = True
            else:
                disprovePlayer = game.getNextPlayer(disprovePlayer)

    if disproved == False:
        message = "No one could disprove " + name + "'s suggestion."
        notif = Notification(content=message, game=suggPlayer.game)
        notif.save()

    gameState = suggPlayer.game.getGameState(suggPlayer)
        
    return JsonResponse(gameState, safe=False)
             """

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
                player.game.status = "won"
                player.game.save()
            else:
                player.status = "lost"
                player.save()
                players_left = Player.objects.filter(game=player.game, unplayed=False, status="in game")
                if players_left.count() == 1:
                    win_name = players_left[0].user.username
                    message += name + "'s accusation was incorrect. Since " + win_name + " is the only player left, they win the game!"
                    player.game.status = "won"
                    player.game.save()
                else:
                    message += " This accusation is incorrect, " + name + " can no longer win the game."
            notif = Notification(content=message, game=player.game)
            notif.save()
            game.specialMessage = ""
            game.save()
        else:
            return JsonResponse({"error": "You cannot make an accusation at this time."}, safe=False)

    gameState = player.game.getGameState(player)
        
    return JsonResponse(gameState, safe=False)

#ends the current players turn and updates game's current player to be the next player
def endTurn(request):
    player = Player.objects.filter(user__username=request.user.username)[0]
    game = Game.objects.filter(currentPlayer=player)[0]
    next_p = game.getNextPlayer(player)
    game.currentPlayer = next_p
    game.specialMessage = ""
    game.save()

    next_p.hasMadeSuggestionThisTurn = False
    next_p.hasMovedThisTurn = False
    next_p.save()

    message = player.user.username + " ended their turn. It is now " + next_p.user.username + "'s turn."
    notif = Notification(content=message, game=game)
    notif.save()

    gameState = player.game.getGameState(player)
        
    return JsonResponse(gameState, safe=False)


def endGame(request):
    player = Player.objects.filter(user__username=request.user.username)[0]
    game = player.game
    players_left = Player.objects.filter(game=game, unplayed=False)
    if players_left.count() == 1:
        game.endGame()
        game.delete()

    player.status = "not in game"
    player.game = None
    player.character = None
    player.movedBySuggestion = False
    player.hasMadeSuggestionInRoom = False
    player.hasMadeSuggestionThisTurn = False
    player.hasMovedThisTurn = False
    player.save()

    return redirect('/')


#returns the game state to the polling client
def gameState(request):
    player = Player.objects.filter(user__username=request.user.username)[0]
    if player.game == None:
        return JsonResponse({'status':'won'}, safe=False)
    return JsonResponse(player.game.getGameState(player), safe=False)


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
