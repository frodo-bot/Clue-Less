from django.db import models
from django.contrib.auth.models import User
from random import randint

CHARACTERS = ["Miss Scarlet", "Professor Plum", "Mrs. Peacock", "Mr. Green", "Colonel Mustard", "Mrs. White"]
WEAPONS = ["Rope", "Lead Pipe", "Knife", "Wrench", "Candlestick", "Revolver"]
ROOMS = ["Study", "Hall", "Lounge", "Library", "Billiard Room", "Dining Room", "Conservatory", "Ballroom", "Kitchen"]
HALLWAYS = ["Study - Hall", "Hall - Lounge", "Study - Library", "Hall - Billiard Room", "Lounge - Dining Room", "Library - Billiard Room", "Billiard Room - Dining Room", "Library - Conservatory", "Billiard Room - Ballroom", "Dining Room - Kitchen", "Conservatory - Ballroom", "Ballroom - Kitchen"]
SECRET_PASSAGE_ROOMS = ["Study", "Lounge", "Conservatory", "Kitchen"]

#suggestion model specifically for skeletal increment (this will be modified/removed later)
class Suggestion(models.Model):
    user = models.CharField(max_length=150)
    text = models.CharField(max_length=500)

#accusation model specifically for skeletal increment (this will be modified/removed later)
class Accusation(models.Model):
    user = models.CharField(max_length=150)
    text = models.CharField(max_length=500)

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    game = models.ForeignKey('Game', on_delete=models.DO_NOTHING, related_name="game_player_is_in", null=True)
    character = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=20)
    currentRoom = models.ForeignKey('Room', on_delete=models.DO_NOTHING, null=True)
    currentHallway = models.ForeignKey('Hallway', on_delete=models.DO_NOTHING, null=True)
    movedBySuggestion = models.BooleanField(default=False)

    #returns True if the player is currently in a room and False if they're in a hallway
    def inRoom(self):
        if self.currentRoom is None:
            return False
        else:
            return True

    #returns a list of the valid moves on the board that the player can currently make
    def getValidMoves(self):
        return []

    # returns a list of the valid actions that a user can take (i.e. make suggestion or accusation)
    def getValidActions(self): 
        return []


class Game(models.Model):
    solution = models.ForeignKey('CaseFile', on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=20, null=True)
    name = models.CharField(max_length=50)
    currentPlayer = models.ForeignKey(Player, on_delete=models.DO_NOTHING, related_name="current_player_turn", null=True)

    #initializes the game state by assigning the players to the game creating the board, rooms,
    #   and hallways, assigns a character to each player, and sets game status to "not started"
    def initialize(self, players):
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

        #set status to not started
        self.status = "not started"

        #create the board, initialize it, and save it
        board, created = Board.objects.get_or_create(game=self)
        board.initialize()
        board.save()

        self.save()

    #starts the game by randomizing the case file, handing out the rest of the cards to the 
    #   players, setting currentPlayer to whoever has the Miss Scarlet character, and changing
    #   game status to "in progress"
    def startGame(self):
        return

    #updates game in database (NOT SURE IF THIS IS NEEDED)
    def updateGame(self):
        return

    #returns the current game state as a JSON object
    def getGameState(self):
        return {}

    #checks whether an accusation is correct against the case file stored in the game object. If
    #   it's correct, return True. Otherwise return False
    def checkAccusation(self, character, weapon, room):
        return True

    #ends the game by setting the winning player's status to "won" as well as setting the game's
    #   status to "won"
    def endGame(self, player):
        return

    #returns a list of the Clue-Less characters that are not being played by Players (i.e. there
    #   are less than 6 players)
    def getUnplayedCharacters(self):
        return []

    #uses list of players in database to get the player after the current player. Set currentPlayer
    #   to the next player and return the next player
    def getNextPlayer(self):
        return


class Board(models.Model):
    game = models.OneToOneField(Game, on_delete=models.CASCADE)

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

    #returns the state of the board (i.e. all the rooms and hallways) as a JSON object
    def getBoardState(self):
        return {}


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
    owner = models.ForeignKey(Player, on_delete=models.DO_NOTHING, null=True)
    game = models.ForeignKey(Game, on_delete=models.DO_NOTHING, null=True)

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