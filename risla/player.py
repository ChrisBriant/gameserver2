class Player:

    def __init__(self, id):
        self.id = id
        self.asks = []
        self.room = None

    def set_name(name):
        self.name = name

    def set_alias(alias):
        self.alias = alias

    def set_room(room_id):
        self.room_id = room_id

class Room:

    def __init__(self, name, owner, roomlist):
        #Validate room name doesn't already exist
        if name in [r.name for r in roomlist.rooms]:
            raise ValueError("Room already exists")
        if owner.room:
            raise ValueError("User already joined to room")
        #Set player room reference and room attributes
        owner.room = name
        self.name = name
        self.owner = owner
        self.players = [owner]

    def add_player(self,player):
        if player.room:
            raise ValueError("User already joined to room")
        player.room = self.name
        self.players.append(player)

    def get_players(self):
        return [{'name':p.name, 'id':p.id} for p in self.players]

    def leave_room(self,player):
        if player in self.players:
            self.players = [p for p in self.players if p != player]
        #Change owner if it is the owner who is leaving
        if self.owner == player and len(self.players) > 0:
            self.owner = self.players[0]
        player.room = None
        return len(self.players)



class PlayerList:

    def __init__(self):
        self.players = []

    def add_player(self,player):
        self.players.append(player)

    def remove_player(self,id):
        self.players = [p for p in self.players if p.id != id]

    def get_player(self,id):
        return [p for p in self.players if p.id == id][0]

class RoomList:

    def __init__(self):
        self.rooms = []

    def add_room(self,room):
        self.rooms.append(room)

    def remove_room(self,roomname):
        self.rooms = [r for r in self.rooms if r.name != roomname]

    def get_room(self,roomname):
        room = [r for r in self.rooms if r.name == roomname]
        if len(room) > 0:
            return room[0]
        else:
            return None





    # def remove_player(self,id):
    #     self.rooms = [p for p in self.rooms if p.id != id]
