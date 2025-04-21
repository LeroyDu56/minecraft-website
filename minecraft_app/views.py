from django.shortcuts import render, get_object_or_404
from .models import TownyServer, Nation, Town, StaffMember, Rank, ServerRule, DynamicMapPoint
from django.db.models import Count, Sum
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from django.shortcuts import redirect
from .models import UserProfile
from .services import fetch_minecraft_uuid, format_uuid_with_dashes
import requests
import json
import logging


def home(request):
    server = TownyServer.objects.first()
    nations_count = Nation.objects.count()
    towns_count = Town.objects.count()
    
    # Récupérer les 3 premières nations pour l'affichage en page d'accueil
    top_nations = Nation.objects.annotate(towns_count=Count('towns')).order_by('-towns_count')[:3]
    
    context = {
        'server': server,
        'nations_count': nations_count,
        'towns_count': towns_count,
        'nations': top_nations,  # Ajout des nations pour la page d'accueil
    }
    
    return render(request, 'minecraft_app/home.html', context)

def nations(request):
    # Récupérer seulement les 3 premières nations par nombre de villes (top nations)
    nations_list = Nation.objects.annotate(towns_count=Count('towns')).order_by('-towns_count')[:3]
    
    # Calculer des statistiques supplémentaires pour la page nations
    total_towns = Town.objects.count()
    total_residents = Town.objects.aggregate(total=Sum('residents_count'))['total'] or 0
    
    context = {
        'nations': nations_list,
        'total_towns': total_towns,
        'total_residents': total_residents,
    }
    
    return render(request, 'minecraft_app/nations.html', context)

def nation_detail(request, nation_id):
    nation = get_object_or_404(Nation, id=nation_id)
    towns = Town.objects.filter(nation=nation).order_by('-residents_count')
    
    context = {
        'nation': nation,
        'towns': towns,
    }
    
    return render(request, 'minecraft_app/nation_detail.html', context)

def dynmap(request):
    map_points = DynamicMapPoint.objects.all()
    towns = Town.objects.all()
    nations = Nation.objects.all()
    
    context = {
        'map_points': map_points,
        'towns': towns,
        'nations': nations,
    }
    
    return render(request, 'minecraft_app/dynmap.html', context)

def staff(request):
    admins = StaffMember.objects.filter(role='admin')
    mods = StaffMember.objects.filter(role='mod')
    helpers = StaffMember.objects.filter(role='helper')
    builders = StaffMember.objects.filter(role='builder')
    
    context = {
        'admins': admins,
        'mods': mods,
        'helpers': helpers,
        'builders': builders,
    }
    
    return render(request, 'minecraft_app/staff.html', context)

def store(request):  # Remplace ranks
    ranks_list = Rank.objects.all().order_by('price')
    
    context = {
        'ranks': ranks_list,
    }
    
    return render(request, 'minecraft_app/store.html', context)

def rules(request):
    rules_list = ServerRule.objects.all()
    
    context = {
        'rules': rules_list,
    }
    
    return render(request, 'minecraft_app/rules.html', context)

def contact(request):
    server = TownyServer.objects.first()
    
    context = {
        'server': server,
    }
    
    return render(request, 'minecraft_app/contact.html', context)

def faq(request):
    return render(request, 'minecraft_app/faq.html')

def staff(request):
    # Check if staff members exist, if not create default administrators
    if StaffMember.objects.count() == 0:
        # Create administrators
        StaffMember.objects.create(
            name="EnzoLaPicole",
            role="admin",
            description="Founder and lead developer of GeoMC server. Responsible for technical operations and overall gameplay experience.",
            discord_username="EnzoLaPicole#1234"
        )
        
        StaffMember.objects.create(
            name="karatoss",
            role="admin",
            description="Co-administrator in charge of community management and moderation. Towny plugin specialist.",
            discord_username="karatoss#5678"
        )
        
        StaffMember.objects.create(
            name="Betaking",
            role="admin",
            description="Administrator responsible for events and communications. Expert in town construction and design.",
            discord_username="Betaking#9012"
        )
    
    # Get staff members by role
    admins = StaffMember.objects.filter(role='admin')
    mods = StaffMember.objects.filter(role='mod')
    helpers = StaffMember.objects.filter(role='helper')
    builders = StaffMember.objects.filter(role='builder')
    
    context = {
        'admins': admins,
        'mods': mods,
        'helpers': helpers,
        'builders': builders,
    }
    
    return render(request, 'minecraft_app/staff.html', context)

# Formulaire d'inscription personnalisé
class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    minecraft_username = forms.CharField(max_length=100, required=False, help_text="Votre pseudo Minecraft")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'minecraft_username']

# Modifiez la vue register_view pour récupérer l'UUID
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            minecraft_username = form.cleaned_data.get('minecraft_username')
            
            # Créer le profil utilisateur
            profile = UserProfile.objects.create(
                user=user,
                minecraft_username=minecraft_username
            )
            
            # Si un nom d'utilisateur Minecraft est fourni, essayer de récupérer l'UUID
            if minecraft_username:
                uuid = fetch_minecraft_uuid(minecraft_username)
                if uuid:
                    profile.minecraft_uuid = uuid
                    profile.save()
                
            # Connecter l'utilisateur
            login(request, user)
            messages.success(request, "Compte créé avec succès! Bienvenue sur GeoMC!")
            return redirect('home')
    else:
        form = RegisterForm()
    
    return render(request, 'minecraft_app/register.html', {'form': form})

# Vue de connexion
@login_required
def profile_view(request):
    user = request.user
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
        
    if request.method == 'POST':
        # Formulaire de mise à jour du profil
        minecraft_username = request.POST.get('minecraft_username')
        discord_username = request.POST.get('discord_username')
        bio = request.POST.get('bio')
        
        # Mettre à jour le profil
        old_minecraft_username = profile.minecraft_username
        
        profile.minecraft_username = minecraft_username
        profile.discord_username = discord_username
        profile.bio = bio
        
        # Si le nom d'utilisateur Minecraft a changé, mettre à jour l'UUID
        if minecraft_username != old_minecraft_username:
            if minecraft_username:
                uuid = fetch_minecraft_uuid(minecraft_username)
                if uuid:
                    profile.minecraft_uuid = uuid
                else:
                    # Si l'UUID ne peut pas être récupéré, effacer l'ancien
                    profile.minecraft_uuid = ''
            else:
                # Si le nom d'utilisateur est vide, effacer l'UUID
                profile.minecraft_uuid = ''
        
        profile.save()
        
        messages.success(request, "Profil mis à jour avec succès!")
        return redirect('profile')
        
    return render(request, 'minecraft_app/profile.html', {'profile': profile})

# Vue de déconnexion
def logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('home')

# Vue de profil
@login_required
def profile_view(request):
    user = request.user
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
        
    if request.method == 'POST':
        # Formulaire de mise à jour du profil (à compléter)
        minecraft_username = request.POST.get('minecraft_username')
        discord_username = request.POST.get('discord_username')
        bio = request.POST.get('bio')
        
        # Mettre à jour le profil
        profile.minecraft_username = minecraft_username
        profile.discord_username = discord_username
        profile.bio = bio
        profile.save()
        
        messages.success(request, "Profil mis à jour avec succès!")
        return redirect('profile')
        
    return render(request, 'minecraft_app/profile.html', {'profile': profile})

def fetch_minecraft_uuid(username):
    """
    Récupère l'UUID Minecraft d'un utilisateur à partir de son nom d'utilisateur.
    Utilise l'API Mojang.
    
    Args:
        username (str): Nom d'utilisateur Minecraft
        
    Returns:
        str: UUID de l'utilisateur (sans tirets) ou None si non trouvé
    """
    if not username:
        return None
        
    try:
        url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('id')  # UUID sans tirets
        elif response.status_code == 204 or response.status_code == 404:
            logger.warning(f"Utilisateur Minecraft non trouvé: {username}")
            return None
        else:
            logger.error(f"Erreur lors de la récupération de l'UUID: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Exception lors de la récupération de l'UUID: {str(e)}")
        return None

def format_uuid_with_dashes(uuid):
    """
    Ajoute des tirets à l'UUID au format standard.
    
    Args:
        uuid (str): UUID sans tirets
        
    Returns:
        str: UUID avec tirets au format standard
    """
    if not uuid or len(uuid) != 32:
        return uuid
        
    return f"{uuid[0:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:32]}"