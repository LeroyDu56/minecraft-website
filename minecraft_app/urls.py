from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('nations/', views.nations, name='nations'),
    path('nations/<int:nation_id>/', views.nation_detail, name='nation_detail'),
    path('villes/', views.towns, name='towns'),
    path('villes/<int:town_id>/', views.town_detail, name='town_detail'),
    path('carte/', views.dynmap, name='dynmap'),
    path('actualites/', views.news, name='news'),
    path('actualites/<int:post_id>/', views.news_detail, name='news_detail'),
    path('equipe/', views.staff, name='staff'),
    path('grades/', views.ranks, name='ranks'),
    path('regles/', views.rules, name='rules'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
]