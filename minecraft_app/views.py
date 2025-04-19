from django.shortcuts import render, get_object_or_404
from .models import TownyServer, Nation, Town, NewsPost, StaffMember, Rank, ServerRule, DynamicMapPoint
from django.db.models import Count

def home(request):
    server = TownyServer.objects.first()
    latest_news = NewsPost.objects.order_by('-created_at')[:3]
    nations_count = Nation.objects.count()
    towns_count = Town.objects.count()
    
    context = {
        'server': server,
        'latest_news': latest_news,
        'nations_count': nations_count,
        'towns_count': towns_count,
    }
    
    return render(request, 'minecraft_app/home.html', context)

def nations(request):
    nations_list = Nation.objects.annotate(towns_count=Count('towns')).order_by('-towns_count')
    
    context = {
        'nations': nations_list,
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

def towns(request):
    towns_list = Town.objects.all().order_by('-residents_count')
    
    context = {
        'towns': towns_list,
    }
    
    return render(request, 'minecraft_app/towns.html', context)

def town_detail(request, town_id):
    town = get_object_or_404(Town, id=town_id)
    
    context = {
        'town': town,
    }
    
    return render(request, 'minecraft_app/town_detail.html', context)

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

def news(request):
    news_posts = NewsPost.objects.order_by('-created_at')
    
    context = {
        'news_posts': news_posts,
    }
    
    return render(request, 'minecraft_app/news.html', context)

def news_detail(request, post_id):
    post = get_object_or_404(NewsPost, id=post_id)
    
    context = {
        'post': post,
    }
    
    return render(request, 'minecraft_app/news_detail.html', context)

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

def ranks(request):
    ranks_list = Rank.objects.all().order_by('price')
    
    context = {
        'ranks': ranks_list,
    }
    
    return render(request, 'minecraft_app/ranks.html', context)

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