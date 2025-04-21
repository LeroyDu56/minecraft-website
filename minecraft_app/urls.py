from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('nations/', views.nations, name='nations'),
    path('nations/<int:nation_id>/', views.nation_detail, name='nation_detail'),
    # Suppression des URLs 'towns' et 'town_detail'
    path('carte/', views.dynmap, name='dynmap'),
    path('actualites/', views.news, name='news'),
    path('actualites/<int:post_id>/', views.news_detail, name='news_detail'),
    path('equipe/', views.staff, name='staff'),
    path('boutique/', views.store, name='store'),  # Remplacer 'ranks' par 'store'
    path('regles/', views.rules, name='rules'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
]