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
]