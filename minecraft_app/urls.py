# Dans urls.py, ajouter la nouvelle URL pour store_nok

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('map/', views.map_view, name='dynmap'),
    path('staff/', views.staff, name='staff'),
    path('store/', views.store, name='store'),
    path('store/require_access/', views.store_nok, name='store_nok'),  # AJOUTER CETTE LIGNE
    path('rules/', views.rules, name='rules'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('checkout/<int:rank_id>/', views.checkout, name='checkout'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),
    path('cart/', views.view_cart, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/checkout/', views.checkout_cart, name='checkout_cart'),
    path('check-minecraft-username/', views.check_minecraft_username, name='check_minecraft_username'),
    path('store/gift/<int:rank_id>/', views.gift_rank, name='gift_rank'),
    path('verify-minecraft-username/', views.verify_minecraft_username, name='verify_minecraft_username'),
]