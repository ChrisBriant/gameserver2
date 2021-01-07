# chat/consumers.py
import json
from .player import *
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from difflib import SequenceMatcher
import secrets,pprint

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
        #print(self.scope["session"])
        id = secrets.token_hex(15)
        room_id = secrets.token_hex(15)
        self.scope["session"]["id"] = id
        newplayer = Player(id)
        players.add_player(newplayer)
        print('players',players.players)
        #Create a channel group for that individual player
        await self.channel_layer.group_add(
            id,
            self.channel_name
        )
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
        print('KEYS',text_data_json.keys())
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
                await self.send_room(room,'list_players')

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
                    'name' : text_data_json['setname']
                }

            }
            await self.send(text_data=json.dumps(data))
            await self.room_list(None)
            print('This is annoying')
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
                await self.send_room(room,'list_players')
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
                await self.send_room(room,'list_players')
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
        if 'start_game' in text_data_json.keys():
            player = players.get_player(self.scope['session']['id'])
            room = rooms.get_room(player.room)
            game = {
                'current_round' : 1,
                'current_player' : player.id,
                'players_left' : [p for p in room.get_players(player)],
                'turns' : [p for p in room.get_players(player)],
                'await_response' : False
            }
            game['players_left'].append({'name':player.name, 'id':player.id, 'celeb':player.celeb})
            #Load the game dictionary with the players for tracking
            for p in game['players_left']:
                game[p['id']] = dict()
                print('settingup', p['id'] )
            room.game = game

            await self.channel_layer.group_send(
                room.name,
                {
                    'type': 'init_game',
                    'owner': room.owner.id
                }
            )
        if 'send_question' in text_data_json.keys():
            player = players.get_player(self.scope['session']['id'])
            room = rooms.get_room(player.room)
            game = room.game
            question = text_data_json['send_question']
            print('send question',question)
            matchscore = SequenceMatcher(None, question, player.celeb).ratio()
            if matchscore > 0.7:
                #Trigger player wins
                print('Trigger Win')
                self.handle_player_win(player,room,game)
            else:
                #Get the remaining players and then set the current player
                remaining_players = [ p for p in game['players_left'] if p != player]
                if len(remaining_players) > 0:
                    if player.id == game['current_player']:
                        #nextplayer
                        game['current_player'] = remaining_players[0]['id']
                        game['receiving_player'] = player.id
                        game['await_response'] = True
                        game['response_list'] = [p for p in room.get_players(player) if p != player]
                        #Question history
                        game[player.id][game['current_round']] = dict()
                        game[player.id][game['current_round']]['question'] = question
                        game[player.id][game['current_round']]['responses'] = []
                        #Send response
                        await self.channel_layer.group_send(
                            room.name,
                            {
                                'type': 'send_question',
                                'sender': {
                                    'id' : player.id,
                                    'celeb' : player.celeb
                                },
                                'question' : question
                            }
                        )
                        print(game)
        if 'reply_yesno' in text_data_json.keys():
            player = players.get_player(self.scope['session']['id'])
            room = rooms.get_room(player.room)
            game = room.game
            response = text_data_json['reply_yesno']
            #Check user hasn't responded and then remove from list
            if player.id in [p['id'] for p in game['response_list']]:
                game['response_list'] = [p for p in game['response_list'] if p['id'] != player.id]
                #Record response
                game[game['receiving_player']][game['current_round']]['responses'] = {
                    'player' : player,
                    'response' : response
                }

                if len(game['response_list']) == 0:
                    last_response = True
                else:
                    last_response = False

                #send response to receiving player
                await self.channel_layer.group_send(
                    game['receiving_player'],
                    {
                        'type': 'receive_yesno',
                        'sender': player.celeb,
                        'response' : response,
                        'last_response' : last_response
                    }
                )
        if 'end_turn' in text_data_json.keys():
            #Others have all responded ready to move on
            player = players.get_player(self.scope['session']['id'])
            room = rooms.get_room(player.room)
            game = room.game
            game['await_response'] = False
            game['turns'] = [p for p in game['turns'] if p['id'] != player.id ]
            if len(game['turns']) == 0:
                game['current_round'] += 1
                print('end of round', game['current_player'], room.owner)
            else:
                game['current_player'] = game['turns'][0]['id']
            #game['current_player'] = player.id
            game['players_left'] = [p for p in room.get_players(player)]

            print('switch over', game)
            #Signal to the current player that it is now their turn
            await self.channel_layer.group_send(
                room.name,
                {
                    'type': 'init_game',
                    'owner': game['current_player']
                }
            )

                #game['current_round'] += 1
                #Need to change turns
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

    async def handle_player_win(self,player,room,game):
        #Add to ranking table
        #Take out of room, but not channel
        print('heelo')
        pp = pprint.PrettyPrinter(indent=4)
        pp.print(game)
        #Signal to other players that this player has guessed correctly
        #If not more players then end the game

    #Send to a room
    async def send_room(self,room,type):
        await self.channel_layer.group_send(
            room.name,
            {
                'type': type,
                'data': room.name,
                'sender_chanel_name' : self.channel_name
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
        print("here", rooms, [r for r in rooms.rooms]);
        await self.send(text_data=json.dumps({
            'action': 'room_list',
            'payload': {
                'success': True,
                'rooms':[r.name for r in rooms.rooms]
            }
        }))

    async def init_game(self,event):
        # Send message to WebSocket
        player = players.get_player(self.scope['session']['id'])
        owner = event['owner']
        await self.send(text_data=json.dumps({
            'action': 'init_game',
            'payload': {
                'owner_id': owner,
                'player_id': player.id
            }
        }))

    async def room_join(self,event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'action': 'room_join',
            'payload' : {
                'success': True,
                'room' : event.name,
                #'players' : event.get_players()
            }
        }))


    async def list_players(self,event):
        # Send message to WebSocket
        player = players.get_player(self.scope['session']['id'])
        room = rooms.get_room(event['data'])
        room_members = room.get_players(player)

        print('list_players')
        # print(self.channel_name)
        # print(event['sender_chanel_name'])
        # if self.channel_name != event['sender_chanel_name']:

        await self.send(text_data=json.dumps({
            'action': 'room_list_players',
            'payload' : {
                'players' : room_members,
                'owner' : room.owner.id
            }
        }))


    async def send_question(self,event):
        print('Here is the event', event)
        await self.send(text_data=json.dumps({
            'action': 'receive_question',
            'payload' : {
                'sender' :event['sender'],
                'question' : event['question']
            }
        }))


    async def receive_yesno(self,event):
        await self.send(text_data=json.dumps({
            'action': 'receive_yesno',
            'payload' : {
                'sender' :event['sender'],
                'response' : event['response'],
                'last_response' : event['last_response']
            }
        }))


class RoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("IN ROOM")
        print('SESSION ID',self.scope["session"].__dict__)
        print('players',[p.id for p in players.players])
        self.room_group_name = self.scope['url_route']['kwargs']['room_name']

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        data = {
            'action' : 'player_list',
            'payload' : {
                    'success': True,
                    'players': [p.name for p in players.players]
            }
        }
        await self.send(text_data=json.dumps(data))

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

    async def disconnect(self, close_code):
        # Leave room group
        print("Disconnecting", self.scope['session']['id'])
