from django.shortcuts import render
from .models import MinecraftServer

def home(request):
    servers = MinecraftServer.objects.all()
    return render(request, 'minecraft_app/home.html', {'servers': servers})