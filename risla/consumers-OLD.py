# chat/consumers.py
import json
from .player import *
from .models import *
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import secrets

players = PlayerList()
rooms = RoomList()

#Send the room list will need to be called continually
# async def send_room_data(channel_layer):
#     await channel_layer.group_send(
#         'all_users',
#         {
#             'type': 'room_data',
#             'data': {
#                 'action' : 'room_list',
#                 'payload' : {
#                         'success': True,
#                         'rooms': [r.name for r in rooms.rooms]
#                 }
#             }
#         }
#     )

@sync_to_async
def get_random_celeb():
    return Person.random_objects.random()


class PlayerConsumer(AsyncWebsocketConsumer):


    async def connect(self):
        print("Hello")
        #print(self.scope["session"].)
        id = secrets.token_hex(15)
        room_id = secrets.token_hex(15)
        self.scope["session"]["id"] = id
        newplayer = Player(id)
        players.add_player(newplayer)

        newplayer.set_name('bob')
        #self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'all_users'
        #
        # # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        data = {
            'action' : 'room_list',
            'payload' : {
                    'success': True,
                    'rooms': [r.name for r in rooms.rooms]
            }
        }
        # await self.send(text_data=json.dumps({
        #     'player_id':id
        # }))
        await self.send(text_data=json.dumps(data))
        #Send ID
        data = {
            'action' : 'send_id',
            'payload' : {
                    'player_id':id
            }
        }
        await self.send(text_data=json.dumps(data))



    async def disconnect(self, close_code):
        # Leave room group
        print("Disconnecting", self.scope['session']['id'])
        #Remove the disconnected player
        player = players.get_player(self.scope['session']['id'])
        players.remove_player(player.id)
        room = rooms.get_room(player.room)
        if room:
            #Sending messages on disconnect doesn't seem to work
            print('Players', players.players)
            print('Player Count', len(players.players))
            players_left = room.leave_room(player)
            if players_left < 1:
                rooms.remove_room(room.name)
                await self.channel_layer.group_send(
                    'all_users',
                    {
                        'type': 'room_list',
                    }
                )
                await self.channel_layer.group_discard(
                    room.name,
                    self.channel_name
                )
            else:
                print("NOT REMOVING")
                await self.send_room(room,'list_players')


    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        #print(text_data_json.keys())
        #print(self.channel_name)
        if 'newroom' in text_data_json.keys():
            #Create a new room
            owner = players.get_player(self.scope['session']['id'])
            try:
                room = Room(text_data_json['newroom'],owner,rooms)
                rooms.add_room(room)
                #self.room_group_name = text_data_json['newroom']
                await self.channel_layer.group_add(
                    text_data_json['newroom'],
                    self.channel_name
                )
                await self.channel_layer.group_send(
                    'all_users',
                    {
                        'type': 'room_list',
                    }
                )
                await self.room_join(room)
                data = {
                    'room' : room,
                    'player' : owner
                }
                await self.send_room(data,'list_players')

                #Doesn't work
                #send_room_data(self.channel_layer)
            except Exception as e:
                print(e)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'room_data',
                        'data': {
                            'action' : 'room_list',
                            'payload' : {
                                'success': False,
                                'message': str(e)
                            }
                        }
                    }
                )
        if 'setname' in text_data_json.keys():
            player = players.get_player(self.scope['session']['id'])
            player.name = text_data_json['setname']
            #Set celebrity name
            celeb = await get_random_celeb();
            player.celeb = celeb.name

            data = {
                'action' : 'name_set',
                'payload' : {
                    'success': True,
                    'name' : text_data_json['setname'],
                }

            }
            await self.send(text_data=json.dumps(data))
            await self.room_list(None)
        if 'joinroom' in text_data_json.keys():
            player = players.get_player(self.scope['session']['id'])
            room = rooms.get_room(text_data_json['joinroom'])
            try:
                room.add_player(player)
                # data = {
                #     'action' : 'room_join',
                #     'payload' : {
                #         'success': True,
                #         'room' : text_data_json['joinroom'],
                #         'players' : room.get_players()
                #     }
                # }
                await self.room_join(room)
                await self.channel_layer.group_add(
                    room.name,
                    self.channel_name
                )
                data = {
                    'room' : room,
                    'player' : player
                }
                await self.send_room(data,'list_players')
                print('list players')
            except Exception as e:
                print(e)
                data = {
                    'action' : 'room_join',
                    'payload' : {
                        'success': False,
                        'message':str(e)
                    }
                }
                await self.send(text_data=json.dumps(data))
        if 'leaveroom' in text_data_json.keys():
            player = players.get_player(self.scope['session']['id'])
            room = rooms.get_room(text_data_json['leaveroom'])
            players_left = room.leave_room(player)
            #Destroy if empty, if not send the list of players
            if players_left < 1:
                rooms.remove_room(room.name)
                await self.channel_layer.group_discard(
                    room.name,
                    self.channel_name
                )
            else:
                data = {
                    'room' : room,
                    'player' : player
                }
                await self.send_room(data,'list_players')
            await self.channel_layer.group_send(
                'all_users',
                {
                    'type': 'room_list',
                }
            )
            data = {
                'action' : 'room_leave',
                'payload' : {
                    'success': True,
                    'room' : room.name,
                }
            }
            await self.send(text_data=json.dumps(data))
            # await self.send(
            #     {
            #         'type': 'room_data',
            #         'message': json.dumps({'success':True})
            #     }
            # )
        #BELOW SENDS TO CONNECTED INDIVIDUAL
        #await self.send(text_data=json.dumps("Hello world!"))
        #message = text_data_json['message']

        # Send message to room group

    #Send to a room
    async def send_room(self,data,type):

        room = data['room']
        print('send_room',data)
        await self.channel_layer.group_send(
            room.name,
            {
                'type': type,
                'data': data
            }
        )


    # Receive message from room group
    async def room_data(self, event):
        data = event['data']
        print('DATA HERE',data)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'action': data['action'],
            'payload': data['payload']
        }))

    async def room_list(self,event):
        # Send message to WebSocket
        print("here");
        await self.send(text_data=json.dumps({
            'action': 'room_list',
            'payload': {
                'success': True,
                'rooms':[r.name for r in rooms.rooms]
            }
        }))

    async def room_join(self,event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'action': 'room_join',
            'payload' : {
                'success': True,
                'room' : event.name
                #'players' : event.get_players()
            }
        }))


    async def list_players(self,event):
        # Send message to WebSocket
        # room = rooms.get_room(event['data']['room'])
        # player = event['data']['player']
        # players = room.get_players()
        await self.send(text_data=json.dumps({
            'action': 'room_list_players',
            # 'payload' : {
            #     'players' : players,
            #     'owner' : room.owner.id
            # }
            'payload' : event['data']
        }))



# class RoomConsumer(AsyncWebsocketConsumer):
#
#     async def connect(self):
#         print("IN ROOM")
#         print('SESSION ID',self.scope["session"].__dict__)
#         print('players',[p.id for p in players.players])
#         self.room_group_name = self.scope['url_route']['kwargs']['room_name']
#
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()
#         data = {
#             'action' : 'player_list',
#             'payload' : {
#                     'success': True,
#                     'players': [p.name for p in players.players]
#             }
#         }
#         await self.send(text_data=json.dumps(data))
#
#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#
#     async def disconnect(self, close_code):
#         # Leave room group
#         print("Disconnecting", self.scope['session']['id'])
