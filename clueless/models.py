from django.db import models
from django.contrib.auth.models import User
from random import randint, shuffle
import json

CHARACTERS = ["Miss Scarlet", "Mrs. Peacock", "Professor Plum", "Mr. Green", "Colonel Mustard", "Mrs. White"]
WEAPONS = ["Rope", "Lead Pipe", "Knife", "Wrench", "Candlestick", "Revolver"]
ROOMS = ["Study", "Hall", "Lounge", "Library", "Billiard Room", "Dining Room", "Conservatory", "Ballroom", "Kitchen"]
HALLWAYS = ["Study - Hall", "Hall - Lounge", "Study - Library", "Hall - Billiard Room", "Lounge - Dining Room", "Library - Billiard Room", "Billiard Room - Dining Room", "Library - Conservatory", "Billiard Room - Ballroom", "Dining Room - Kitchen", "Conservatory - Ballroom", "Ballroom - Kitchen"]
SECRET_PASSAGE_ROOMS = ["Study", "Lounge", "Conservatory", "Kitchen"]
SECRET_PASSAGES = {"Study": "Kitchen", "Kitchen": "Study", "Lounge": "Conservatory", "Conservatory": "Lounge"}
STARTING_LOCATIONS = {"Miss Scarlet": "Hall - Lounge", "Mrs. Peacock": "Library - Conservatory", "Professor Plum": "Study - Library", "Mr. Green": "Conservatory - Ballroom", "Colonel Mustard": "Lounge - Dining Room", "Mrs. White": "Ballroom - Kitchen"}

#suggestion model specifically for skeletal increment (this will be modified/removed later)
class Suggestion(models.Model):
    user = models.CharField(max_length=150)
    text = models.CharField(max_length=500)

#accusation model specifically for skeletal increment (this will be modified/removed later)
class Accusation(models.Model):
    user = models.CharField(max_length=150)
    text = models.CharField(max_length=500)

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    game = models.ForeignKey('Game', on_delete=models.DO_NOTHING, related_name="game_player_is_in", null=True)
    character = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=20)
    currentRoom = models.ForeignKey('Room', on_delete=models.DO_NOTHING, null=True)
    currentHallway = models.ForeignKey('Hallway', on_delete=models.DO_NOTHING, null=True)
    movedBySuggestion = models.BooleanField(default=False)
    hasMadeSuggestionInRoom = models.BooleanField(default=False)
    unplayed = models.BooleanField(default=False)

    #returns True if the player is currently in a room and False if they're in a hallway
    def inRoom(self):
        if self.currentRoom is None:
            return False
        else:
            return True

    #returns a list of the valid moves on the board that the player can currently make
    def getValidMoves(self):
        move_list = []
        if self.game.currentPlayer == self:
            if self.status != "lost":
                if self.inRoom():
                    queryset = Hallway.objects.filter(room1=self.currentRoom) | Hallway.objects.filter(room2=self.currentRoom)
                    for hallway in queryset:
                        if not hallway.isOccupied():
                            move_list.append(hallway.name)
                    if self.currentRoom.hasSecretPassage:
                        move_list.append(SECRET_PASSAGES[self.currentRoom.name])
                else:
                    move_list.append(self.currentHallway.room1.name)
                    move_list.append(self.currentHallway.room2.name)

        return move_list

    # returns a list of the valid actions that a user can take (i.e. make suggestion or accusation)
    def getValidActions(self): 
        action_list = []
        if self.game.currentPlayer == self:
            if self.status != "lost":
                if self.inRoom():
                    if not self.hasMadeSuggestionInRoom:
                        action_list.append("Make Suggestion")
                action_list.append("Make Accusation")  
        return action_list

    #returns a list of the cards that a player owns
    def getCards(self):
        card_list = []
        queryset = Card.objects.filter(owner=self)
        for item in queryset:
            card_list.append(item)
        return card_list


class Game(models.Model):
    solution = models.ForeignKey('CaseFile', on_delete=models.DO_NOTHING, null=True)
    status = models.CharField(max_length=20, null=True)
    name = models.CharField(max_length=50)
    currentPlayer = models.ForeignKey(Player, on_delete=models.DO_NOTHING, related_name="current_player_turn", null=True)
    board = models.OneToOneField('Board', on_delete=models.DO_NOTHING, null=True)

    #initializes the game state by assigning the players to the game creating the board, rooms,
    #   and hallways, assigns a character to each player, and sets game status to "not started"
    def initialize(self, players):
        #set status to not started
        self.status = "not started"

        #create the board, initialize it, and save it
        new_board = Board()
        new_board.save()
        self.board = new_board
        self.board.initialize()
        self.board.save()

        self.save()

        #assign all of the players to this game and assign their character
        for i in range(6):
            if i < len(players):
                players[i].game = self
                players[i].character = CHARACTERS[i]
                players[i].status = "in game"
                players[i].save()
            else:
                player = Player(game=self, character=CHARACTERS[i], unplayed=True, status="in game")
                player.save()

        #put the players in their starting locations
        for char in CHARACTERS:
            player = Player.objects.filter(game=self, character=char)[0]
            player.currentHallway = Hallway.objects.filter(board=self.board, name=STARTING_LOCATIONS[char])[0]
            player.save()

        self.save()

    #starts the game by randomizing the case file, handing out the rest of the cards to the 
    #   players, setting currentPlayer to whoever has the Miss Scarlet character, and changing
    #   game status to "in progress"
    def startGame(self):
         #create all of the character cards
        character_cards = []
        for character in CHARACTERS:
            card = Card(name=character, cardType="character", game=self)
            card.save()
            character_cards.append(card)

        #create all of the weapon cards
        weapon_cards = []
        for weapon in WEAPONS:
            card = Card(name=weapon, cardType="weapon", game=self)
            card.save()
            weapon_cards.append(card)

        #create all of the room cards
        room_cards = []
        for room in ROOMS:
            card = Card(name=room, cardType="room", game=self)
            card.save()
            room_cards.append(card)

        #create the case file, randomize the cards in it, and save it
        case_file = CaseFile()
        case_file.randomize(game_id=self.pk)
        case_file.save()
        self.solution = case_file
 
        cards = []
        queryset = Card.objects.filter(game=self)
        for item in queryset:
            cards.append(item)

        #remove case file cards from assignable cards
        cards.remove(self.solution.characterCard)
        cards.remove(self.solution.weaponCard)
        cards.remove(self.solution.roomCard)

        #shuffle cards and hand them out to players
        shuffle(cards)
        players = Player.objects.filter(game=self, unplayed=False)
        while len(cards) > 0:
            for player in players:
                if len(cards) == 0:
                    break
                else:
                    cards[0].owner = player
                    cards[0].save()
                    del cards[0]

        self.currentPlayer = Player.objects.filter(game=self, character="Miss Scarlet")[0]
        self.status = "in progress"
        self.save()

    #returns the current game state as a JSON object
    def getGameState(self):
        state = {
            'status': self.status,
            'currentCharacter': self.currentPlayer.character,
            'currentPlayer': self.currentPlayer.user.username,
            'name': self.name,
            'board': json.loads(self.board.getBoardState()),
        }
        return json.dumps(state)

    #checks whether an accusation is correct against the case file stored in the game object. If
    #   it's correct, return True. Otherwise return False
    def checkAccusation(self, character, weapon, room):
        if self.solution.characterCard.name == character:
            if self.solution.weaponCard.name == weapon:
                if self.solution.roomCard.name == room:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    #compares the cards that a player has to the cards in a suggestion, returns a list of the 
    #   ones that match. If none match, returns an empty list
    def checkSuggestion(self, playerCards, suggestionCards):
        card_matches = []
        for p_card in playerCards:
            for s_card in suggestionCards:
                if p_card.name == s_card:
                    card_matches.append(p_card.name)
        return card_matches

    #ends the game by setting the winning player's status to "won" as well as setting the game's
    #   status to "won". Also deletes the unplayed character objects, board, casefile, and cards
    def endGame(self, player):
        currentPlayer.status = "won"
        currentPlayer.save()

        self.status = "won"
        self.save()

        self.board.delete()
        self.solution.delete()
        Player.objects.filter(game=self, unplayed=True).delete()
        Card.objects.filter(game=self).delete()

        self.save()

    #returns a list of the Clue-Less characters that are not being played by Players (i.e. there
    #   are less than 6 players)
    def getUnplayedCharacters(self):
        unplayed_list = []
        queryset = Player.objects.filter(game=self, unplayed=True)
        for item in queryset:
            unplayed_list.append(item.character)
        return unplayed_list

    #uses the character order to determine who next player is and returns it
    def getNextPlayer(self):
        next_player = ""
        currentCharacterPos = CHARACTERS.index(self.currentPlayer.character)
        if currentCharacterPos + 1 < len(CHARACTERS):
            next_player = Player.objects.filter(game=self, character=CHARACTERS[currentCharacterPos+1], unplayed=False)
            if not next_player:
                next_player = Player.objects.filter(game=self, character=CHARACTERS[0], unplayed=False)[0]
            else:
                next_player = next_player[0]
        else:
            next_player = Player.objects.filter(game=self, character=CHARACTERS[0], unplayed=False)[0]
        return next_player


class Board(models.Model):

    #initialize the game board by creating all of the rooms and hallways
    def initialize(self):
        for hallway in HALLWAYS:
            room_name1 = hallway[:hallway.find("-")-1]
            room_name2 = hallway[hallway.find("-")+2:]
            room1, created = Room.objects.get_or_create(name=room_name1, board=self)
            if room_name1 in SECRET_PASSAGE_ROOMS:
                room1.hasSecretPassage = True
            room1.save()
            room2, created = Room.objects.get_or_create(name=room_name2, board=self)
            if room_name2 in SECRET_PASSAGE_ROOMS:
                room2.hasSecretPassage = True
            room2.save()
            hallway_obj, created = Hallway.objects.get_or_create(name=hallway, room1=room1, room2=room2, board=self)
            hallway_obj.save()
        return

    #returns the state of the board (i.e. all the rooms and hallways and their occupants) as a JSON object
    def getBoardState(self):
        rooms = Room.objects.filter(board=self)
        hallways = Hallway.objects.filter(board=self)
        state = {'rooms': [], 
                'hallways': [],
                }

        for room in rooms:
            state['rooms'].append({room.name: room.getOccupants()})

        for hallway in hallways:
            hall_occupants = []
            if hallway.isOccupied():
                hall_occupants.append(Player.objects.filter(currentHallway=hallway)[0].character)
            state['hallways'].append({hallway.name: hall_occupants})

        return json.dumps(state)

    #moves a player to a particular room on the board. No return value
    def movePlayerToRoom(self, player, roomName):
        room = Room.objects.filter(name=roomName, board=self)[0]
        player.currentRoom = room
        player.currentHallway = None
        player.hasMadeSuggestionInRoom = False
        player.save()
        return 

     #moves a player to a particular hallway on the board. No return value
    def movePlayerToHallway(self, player, hallwayName):
        hallway = Hallway.objects.filter(name=hallwayName, board=self)[0]
        player.currentHallway = hallway
        player.currentRoom = None
        player.hasMadeSuggestionInRoom = False
        player.save()
        return


class Room(models.Model):
    name = models.CharField(max_length=50)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    hasSecretPassage = models.BooleanField(default=False)

    #returns list of players that are in the room. Returns empty list if room is empty
    def getOccupants(self):
        queryset = Player.objects.filter(currentRoom=self)
        occupants = []
        for item in queryset:
            occupants.append(item)
        return occupants


class Hallway(models.Model):
    name = models.CharField(max_length=50)
    room1 = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="adjacent_room_one")
    room2 = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="adjacent_room_two")
    board = models.ForeignKey(Board, on_delete=models.CASCADE)

    #returns True if there is a Player in the hallway, and False otherwise
    def isOccupied(self):
        queryset = Player.objects.filter(currentHallway=self)
        if queryset.count() > 0:
            return True
        else:
            return False


class Card(models.Model):
    name = models.CharField(max_length=50)
    cardType = models.CharField(max_length=20)
    owner = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)

    #returns True if otherCard is equal to self, returns False otherwise
    def isEqual(self, otherCard):
        if self.cardType == otherCard.cardType and self.name == otherCard.name:
            return True
        else:
            return False


class CaseFile(models.Model):
    characterCard = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="casefile_character_card", limit_choices_to={'cardType': 'character'}, null=True)
    weaponCard = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="casefile_weapon_card", limit_choices_to={'cardType': 'weapon'}, null=True)
    roomCard = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="casefile_room_card", limit_choices_to={'cardType': 'room'}, null=True)

    #randomly choose a character, weapon, and room card for the case file
    def randomize(self, game_id):
        character = CHARACTERS[randint(0, 5)]
        weapon = WEAPONS[randint(0, 5)]
        room = ROOMS[randint(0, 8)]
        self.characterCard = Card.objects.filter(name=character, cardType="character", game__pk=game_id)[0]
        self.weaponCard = Card.objects.filter(name=weapon, cardType="weapon", game__pk=game_id)[0]
        self.roomCard = Card.objects.filter(name=room, cardType="room", game__pk=game_id)[0]