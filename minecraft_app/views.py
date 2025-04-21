from django.shortcuts import render, get_object_or_404
from .models import TownyServer, Nation, Town, StaffMember, Rank, ServerRule, DynamicMapPoint
from django.db.models import Count, Sum

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