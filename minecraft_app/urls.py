from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('nations/', views.nations, name='nations'),
    path('nations/<int:nation_id>/', views.nation_detail, name='nation_detail'),
    path('carte/', views.dynmap, name='dynmap'),
    path('equipe/', views.staff, name='staff'),
    path('boutique/', views.store, name='store'),
    path('regles/', views.rules, name='rules'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    
    # Routes d'authentification
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
]