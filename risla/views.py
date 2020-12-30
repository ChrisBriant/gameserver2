from django.shortcuts import render

def index(request):
    return render(request, 'risla/connect.html')

def room(request, room_name):
    return render(request, 'risla/room.html', {
        'room_name': room_name
    })
