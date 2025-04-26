from django.shortcuts import render, get_object_or_404
from .models import TownyServer, Nation, Town, StaffMember, Rank, ServerRule, DynamicMapPoint, UserProfile, UserPurchase, StoreItemPurchase, StoreItem, CartItem
from django.db.models import Count, Sum, F
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from django.conf import settings
from django.shortcuts import redirect, render
from .services import fetch_minecraft_uuid, format_uuid_with_dashes
from django.views.decorators.csrf import csrf_exempt
from .minecraft_service import apply_rank_to_player
import requests
import json
import logging
import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

def home(request):
    server = TownyServer.objects.first()
    nations_count = Nation.objects.count()
    towns_count = Town.objects.count()
    
    # Get the top 3 nations for the home page display
    top_nations = Nation.objects.annotate(towns_count=Count('towns')).order_by('-towns_count')[:3]
    
    context = {
        'server': server,
        'nations_count': nations_count,
        'towns_count': towns_count,
        'nations': top_nations,  # Add nations for the home page
    }
    
    return render(request, 'minecraft_app/home.html', context)

def nations(request):
    # Get only the top 3 nations by number of towns
    nations_list = Nation.objects.annotate(towns_count=Count('towns')).order_by('-towns_count')[:3]
    
    # Calculate additional statistics for the nations page
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

def store(request):  # Replace ranks
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
            description="Founder and lead developer of Novania server. Responsible for technical operations and overall gameplay experience.",
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

# Custom registration form
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    minecraft_username = forms.CharField(
        max_length=100, 
        required=False, 
        help_text="Your Minecraft username",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter your Minecraft username (optional)',
            'autocomplete': 'off'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'minecraft_username']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm your password'})
    
    def clean_minecraft_username(self):
        minecraft_username = self.cleaned_data.get('minecraft_username')
        if minecraft_username and not is_minecraft_username_unique(minecraft_username):
            raise forms.ValidationError("This Minecraft username is already taken by another user.")
        return minecraft_username

# Modify register_view to retrieve UUID
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            minecraft_username = form.cleaned_data.get('minecraft_username')
            
            # Create user profile
            profile = UserProfile.objects.create(
                user=user,
                minecraft_username=minecraft_username
            )
            
            # If a Minecraft username is provided, try to retrieve the UUID
            if minecraft_username:
                uuid = fetch_minecraft_uuid(minecraft_username)
                if uuid:
                    profile.minecraft_uuid = uuid
                    profile.save()
                
            # Log in the user
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to Novania!")
            return redirect('home')
    else:
        form = RegisterForm()
    
    return render(request, 'minecraft_app/register.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'minecraft_app/login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

# Profile view
@login_required
def profile_view(request):
    user = request.user
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    # Get user purchases for display
    purchases = UserPurchase.objects.filter(user=user).select_related('rank')
    
    # Get the server for global context
    server = TownyServer.objects.first()
    
    if request.method == 'POST':
        # Profile update form
        minecraft_username = request.POST.get('minecraft_username')
        discord_username = request.POST.get('discord_username')
        bio = request.POST.get('bio')
        
        # Vérifier si le pseudo Minecraft est unique avant de mettre à jour
        if minecraft_username and minecraft_username != profile.minecraft_username:
            if not is_minecraft_username_unique(minecraft_username, user):
                messages.error(request, "This Minecraft username is already taken by another user.")
                return redirect('profile')
        
        # Update profile
        old_minecraft_username = profile.minecraft_username
        
        profile.minecraft_username = minecraft_username
        profile.discord_username = discord_username
        profile.bio = bio
        
        # If Minecraft username changed, update UUID
        if minecraft_username != old_minecraft_username:
            if minecraft_username:
                uuid = fetch_minecraft_uuid(minecraft_username)
                if uuid:
                    profile.minecraft_uuid = uuid
                else:
                    # If UUID can't be retrieved, clear the old one
                    profile.minecraft_uuid = ''
            else:
                # If username is empty, clear UUID
                profile.minecraft_uuid = ''
        
        profile.save()
        
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    
    context = {
        'profile': profile,
        'server': server,
        'purchases': purchases
    }
        
    return render(request, 'minecraft_app/profile.html', context)

def check_minecraft_username(request):
    """Vue API pour vérifier la disponibilité d'un pseudo Minecraft via AJAX"""
    if request.method == 'GET':
        username = request.GET.get('username', '')
        current_user = request.user if request.user.is_authenticated else None
        
        is_available = is_minecraft_username_unique(username, current_user)
        
        return JsonResponse({
            'available': is_available,
            'message': 'Username is available' if is_available else 'This Minecraft username is already taken'
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def checkout(request, rank_id):
    rank = get_object_or_404(Rank, id=rank_id)
    user = request.user
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'unit_amount': int(rank.price * 100),  # Montant en centimes
                        'product_data': {
                            'name': rank.name,
                            'description': rank.description,
                        },
                    },
                    'quantity': 1,
                }
            ],
            metadata={
                'user_id': user.id,
                'username': user.username,
                'rank_id': rank.id,
                'rank_name': rank.name
            },
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success') + f'?session_id={{CHECKOUT_SESSION_ID}}'),
            cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        logging.error(f"Error creating Stripe checkout session: {str(e)}")
        messages.error(request, f"Error creating payment: {str(e)}")
        return redirect('store')


def payment_success(request):
    session_id = request.GET.get('session_id')
    
    if session_id:
        # Try to retrieve rank purchases
        rank_purchases = UserPurchase.objects.filter(payment_id=session_id)
        
        # Try to retrieve store item purchases
        store_item_purchases = StoreItemPurchase.objects.filter(payment_id=session_id)
        
        # Calculate total amount
        total_amount = 0
        for purchase in rank_purchases:
            total_amount += purchase.amount
        
        for purchase in store_item_purchases:
            total_amount += purchase.amount
        
        if rank_purchases.exists() or store_item_purchases.exists():
            return render(request, 'minecraft_app/payment_success.html', {
                'rank_purchases': rank_purchases,
                'store_item_purchases': store_item_purchases,
                'total_amount': total_amount,
                'server': TownyServer.objects.first()
            })
    
    # Fallback if purchase not found (can happen if webhook hasn't processed yet)
    return render(request, 'minecraft_app/payment_success.html', {
        'server': TownyServer.objects.first()
    })

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Handle different event types
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        process_successful_payment(session)
    elif event['type'] == 'payment_intent.payment_failed':
        session = event['data']['object']
        process_failed_payment(session)
    elif event['type'] == 'checkout.session.expired':
        session = event['data']['object']
        process_expired_session(session)

    return HttpResponse(status=200)

def process_successful_payment(session):
    # Get information from metadata
    user_id = session.get('metadata', {}).get('user_id')
    rank_id = session.get('metadata', {}).get('rank_id')
    
    if user_id and rank_id:
        try:
            user = User.objects.get(id=user_id)
            rank = Rank.objects.get(id=rank_id)
            
            # Record the purchase
            purchase = UserPurchase.objects.create(
                user=user,
                rank=rank,
                amount=rank.price,
                payment_id=session.id,
                payment_status='completed'
            )
            
            # Appliquer le rang sur le serveur Minecraft
            minecraft_username = user.profile.minecraft_username
            if minecraft_username:
                success = apply_rank_to_player(minecraft_username, rank.name)
                if success:
                    logging.info(f"Rank {rank.name} successfully applied to Minecraft player {minecraft_username}")
                else:
                    logging.error(f"Failed to apply rank {rank.name} to player {minecraft_username}")
            else:
                logging.warning(f"User {user.username} doesn't have a Minecraft username set; rank not applied")
            
            logging.info(f"Payment successful for {rank.name} by {user.username}")
        except User.DoesNotExist:
            logging.error(f"User with ID {user_id} not found")
        except Rank.DoesNotExist:
            logging.error(f"Rank with ID {rank_id} not found")
    else:
        logging.error("User or rank metadata missing in Stripe session")

def process_failed_payment(session):
    # Log failed payment
    user_id = session.get('metadata', {}).get('user_id')
    rank_id = session.get('metadata', {}).get('rank_id')
    
    if user_id and rank_id:
        try:
            user = User.objects.get(id=user_id)
            rank = Rank.objects.get(id=rank_id)
            
            # Record the failed purchase for tracking
            UserPurchase.objects.create(
                user=user,
                rank=rank,
                amount=rank.price,
                payment_id=session.id,
                payment_status='failed'
            )
            
            logging.warning(f"Payment failed for {rank.name} by {user.username}")
        except (User.DoesNotExist, Rank.DoesNotExist):
            logging.error(f"User or Rank not found for failed payment. User ID: {user_id}, Rank ID: {rank_id}")
    else:
        logging.error("User or rank metadata missing in failed payment")

def process_expired_session(session):
    # Log expired session
    user_id = session.get('metadata', {}).get('user_id')
    
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            logging.info(f"Checkout session expired for user {user.username}")
        except User.DoesNotExist:
            logging.error(f"User with ID {user_id} not found for expired session")
    else:
        logging.error("User metadata missing in expired session")

def payment_cancel(request):
    messages.warning(request, "Your payment has been cancelled. No money has been charged.")
    return render(request, 'minecraft_app/payment_cancel.html')

def payment_failed(request):
    messages.error(request, "Your payment could not be processed. Please try again or use a different payment method.")
    return render(request, 'minecraft_app/payment_failed.html')


def contact(request):
    server = TownyServer.objects.first()
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        name = request.POST.get('name', '')
        discord_username = request.POST.get('discord_username', '')
        minecraft_username = request.POST.get('minecraft_username', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # Valider les données (vérification simple)
        if name and subject and message:
            # Ici, tu peux implémenter ta logique pour enregistrer le message dans une base de données
            # ou l'envoyer via un webhook Discord
            
            # Exemple de code pour enregistrer dans une base de données (tu pourrais créer un modèle ContactMessage)
            # ContactMessage.objects.create(
            #     name=name,
            #     discord_username=discord_username,
            #     minecraft_username=minecraft_username,
            #     subject=subject,
            #     message=message,
            #     status='pending'
            # )
            
            # Envoyer une notification à l'équipe (à implémenter selon tes besoins)
            # Par exemple, via un webhook Discord
            # send_discord_webhook(name, discord_username, minecraft_username, subject, message)
            
            # Afficher un message de succès
            messages.success(request, "Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.")
            
            # Rediriger pour éviter la resoumission du formulaire
            return redirect('contact')
        else:
            # Si des champs obligatoires sont manquants
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
    
    context = {
        'server': server,
    }
    
    return render(request, 'minecraft_app/contact.html', context)

# Fonction à implémenter pour envoyer les messages via Discord webhook
# def send_discord_webhook(name, discord_username, minecraft_username, subject, message):
#     webhook_url = settings.DISCORD_WEBHOOK_URL
#     
#     data = {
#         "embeds": [{
#             "title": f"Nouveau message: {subject}",
#             "description": message,
#             "color": 3447003,  # Bleu Discord
#             "fields": [
#                 {"name": "De", "value": name, "inline": True},
#                 {"name": "Discord", "value": discord_username or "Non fourni", "inline": True},
#                 {"name": "Minecraft", "value": minecraft_username or "Non fourni", "inline": True}
#             ],
#             "footer": {"text": "Message envoyé depuis le site web"}
#         }]
#     }
#     
#     try:
#         response = requests.post(webhook_url, json=data)
#         return response.status_code == 204
#     except Exception as e:
#         logging.error(f"Erreur d'envoi au webhook Discord: {str(e)}")
#         return False


# Update your store view
def store(request):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect('store_nok')
    
    # Get all ranks ordered by price
    all_ranks = Rank.objects.all().order_by('price')
    store_items = StoreItem.objects.all().order_by('category', 'price')
    
    # Get user's purchased ranks
    user_purchased_ranks = UserPurchase.objects.filter(
        user=request.user,
        payment_status='completed'
    ).select_related('rank')
    
    # Get the highest rank the user owns (based on price)
    highest_owned_rank = None
    if user_purchased_ranks.exists():
        highest_owned_rank = max(
            [purchase.rank for purchase in user_purchased_ranks],
            key=lambda rank: rank.price
        )
    
    # Filter ranks to show
    if highest_owned_rank:
        # Show only ranks that are more expensive than the highest owned rank
        available_ranks = all_ranks.filter(price__gt=highest_owned_rank.price)
        show_new_ranks_notice = not available_ranks.exists()
    else:
        # User hasn't purchased any ranks, show all
        available_ranks = all_ranks
        show_new_ranks_notice = False
    
    # Get cart data if user is authenticated
    cart_count = 0
    cart_total = 0
    
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        cart_count = cart_items.count()
        
        # Calculate cart total
        cart_total = 0
        for item in cart_items:
            cart_total += item.get_subtotal()
    
    context = {
        'ranks': available_ranks,
        'store_items': store_items,
        'cart_count': cart_count,
        'cart_total': cart_total,
        'show_new_ranks_notice': show_new_ranks_notice,
        'user_has_any_rank': user_purchased_ranks.exists(),
        'highest_owned_rank': highest_owned_rank,
    }
    
    return render(request, 'minecraft_app/store.html', context)

def store_nok(request):
    # If user is already authenticated, redirect to the actual store
    if request.user.is_authenticated:
        return redirect('store')
    
    server = TownyServer.objects.first()
    
    context = {
        'server': server,
    }
    
    return render(request, 'minecraft_app/store_nok.html', context)
# Modifié le fichier views.py pour supporter AJAX dans la fonction add_to_cart

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        item_type = request.POST.get('item_type')
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        try:
            # Ensure quantity is within bounds
            max_available = 99
            if quantity < 1:
                quantity = 1
                error_msg = "Quantity must be at least 1."
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg})
                else:
                    messages.warning(request, error_msg)

            if item_type == 'store_item':
                store_item = StoreItem.objects.get(id=item_id)
                cart_item, created = CartItem.objects.get_or_create(
                    user=request.user,
                    store_item=store_item,
                    defaults={'quantity': quantity}
                )
                if not created:
                    # Incrémenter la quantité au lieu de la remplacer
                    cart_item.quantity += quantity
                    if cart_item.quantity > max_available:
                        cart_item.quantity = max_available
                        error_msg = f"Quantity adjusted to maximum available ({max_available})."
                        if is_ajax:
                            return JsonResponse({
                                'success': False,
                                'error': error_msg,
                                'cart_count': CartItem.objects.filter(user=request.user).count(),
                                'cart_total': f"{sum(item.get_subtotal() for item in CartItem.objects.filter(user=request.user)):.2f}",
                                'current_quantity': cart_item.quantity
                            })
                        else:
                            messages.warning(request, error_msg)
                    cart_item.save()
                    logger.debug("DEBUG: Saving CartItem %s: quantity=%s", cart_item.id, cart_item.quantity)
                logger.debug("Added store_item %s to cart with quantity %s", item_id, quantity)
            elif item_type == 'rank':
                rank = Rank.objects.get(id=item_id)
                cart_item, created = CartItem.objects.get_or_create(
                    user=request.user,
                    rank=rank,
                    defaults={'quantity': 1}
                )
                if not created:
                    error_msg = "Rank already in cart."
                    if is_ajax:
                        return JsonResponse({'success': False, 'error': error_msg})
                    else:
                        messages.warning(request, error_msg)
                        return redirect('cart')
                logger.debug("Added rank %s to cart", item_id)
            else:
                error_msg = "Invalid item type."
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg})
                else:
                    messages.error(request, error_msg)
                    return redirect('store')

            # Calculate cart totals
            cart_items = CartItem.objects.filter(user=request.user)
            cart_count = cart_items.count()
            cart_total = sum(item.get_subtotal() for item in cart_items)

            success_msg = "Item added to cart successfully."
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': success_msg,
                    'status': 'success',
                    'cart_count': cart_count,
                    'cart_total': f"{cart_total:.2f}",
                    'current_quantity': cart_item.quantity
                })
            else:
                messages.success(request, success_msg)
                return redirect('cart')

        except (StoreItem.DoesNotExist, Rank.DoesNotExist):
            error_msg = "Item not found."
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg})
            else:
                messages.error(request, error_msg)
        except Exception as e:
            error_msg = f"Error adding item to cart: {str(e)}"
            logger.error(error_msg)
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg})
            else:
                messages.error(request, error_msg)

    return redirect('store')

# View cart page
@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    total = 0
    for item in cart_items:
        total += item.get_subtotal()
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'server': TownyServer.objects.first(),
    }
    
    return render(request, 'minecraft_app/cart.html', context)

# Remove from cart
@login_required
def remove_from_cart(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id, user=request.user)
        item_name = cart_item.rank.name if cart_item.rank else cart_item.store_item.name
        cart_item.delete()
        messages.success(request, f"'{item_name}' has been removed from your cart.")
    except CartItem.DoesNotExist:
        messages.error(request, "Item not found in your cart.")
    
    return redirect('cart')

# Update cart item quantity
@login_required
def update_cart_quantity(request):
    logger.debug("DEBUG: update_cart_quantity called (2025-04-29) with POST data: %s", request.POST)
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            cart_item = CartItem.objects.get(id=item_id, user=request.user)
            logger.debug("DEBUG: Before update: Item %s, quantity=%s, store_item=%s, rank=%s", item_id, cart_item.quantity, cart_item.store_item, cart_item.rank)
            
            # Only store items can have quantities (not ranks)
            if cart_item.store_item:
                # Set max quantity to 99
                max_available = 99
                logger.debug("DEBUG: Store item quantity available: %s, max_available: %s", cart_item.store_item.quantity, max_available)
                
                # Ensure quantity is within bounds
                if quantity > max_available:
                    quantity = max_available
                    if is_ajax:
                        return JsonResponse({
                            'success': False,
                            'error': f'Maximum quantity is {max_available}.',
                            'current_quantity': cart_item.quantity
                        })
                    else:
                        messages.warning(request, f"Quantity adjusted to maximum available ({max_available}).")
                
                # Update the quantity
                logger.debug("DEBUG: Setting quantity to: %s", quantity)
                cart_item.quantity = quantity
                logger.debug("DEBUG: Quantity after set: %s", cart_item.quantity)
                cart_item.save()
                
                logger.debug("DEBUG: After save: Item %s, quantity=%s", item_id, cart_item.quantity)
                
                # Refresh from database to confirm
                cart_item.refresh_from_db()
                logger.debug("DEBUG: After refresh: Item %s, DB quantity=%s", item_id, cart_item.quantity)
                
                if is_ajax:
                    item_subtotal = cart_item.get_subtotal()
                    cart_total = sum(item.get_subtotal() for item in CartItem.objects.filter(user=request.user))
                    logger.debug("DEBUG: Subtotal=%s, Total=%s", item_subtotal, cart_total)
                    return JsonResponse({
                        'success': True,
                        'item_subtotal': f"{item_subtotal:.2f}",
                        'cart_total': f"{cart_total:.2f}",
                        'current_quantity': cart_item.quantity
                    })
            else:
                logger.debug("DEBUG: Item %s is a rank, quantity not updated", item_id)
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'error': 'Ranks cannot have quantity updated'
                    })
                
        except CartItem.DoesNotExist:
            logger.debug("DEBUG: CartItem %s not found for user %s", item_id, request.user)
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Item not found'})
            else:
                messages.error(request, "Item not found in your cart.")
        except Exception as e:
            logger.debug("DEBUG: Error updating cart: %s", str(e))
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)})
            else:
                messages.error(request, f"Error updating cart: {str(e)}")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        logger.debug("DEBUG: Invalid AJAX request")
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    logger.debug("DEBUG: Redirecting to cart")
    return redirect('cart')

# Checkout from cart
@login_required
def checkout_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')
    
    # Calculate total
    total_amount = 0
    items_description = []
    
    for item in cart_items:
        subtotal = item.get_subtotal()
        total_amount += subtotal
        
        if item.rank:
            items_description.append(f"Rank: {item.rank.name}")
        elif item.store_item:
            items_description.append(f"{item.store_item.name} x{item.quantity}")
    
    # Create Stripe session
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'unit_amount': int(total_amount * 100),  # Montant en centimes
                        'product_data': {
                            'name': "Novania Store Purchase",
                            'description': ", ".join(items_description),
                        },
                    },
                    'quantity': 1,
                }
            ],
            metadata={
                'user_id': request.user.id,
                'username': request.user.username,
                'cart_items': ",".join([str(item.id) for item in cart_items]),
            },
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success') + f'?session_id={{CHECKOUT_SESSION_ID}}'),
            cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        logging.error(f"Error creating Stripe checkout session for cart: {str(e)}")
        messages.error(request, f"Error creating payment: {str(e)}")
        return redirect('cart')

# Update the successful payment processing
def process_successful_payment(session):
    # Get information from metadata
    user_id = session.get('metadata', {}).get('user_id')
    cart_items_ids = session.get('metadata', {}).get('cart_items', '').split(',')
    
    if not user_id or not cart_items_ids or not cart_items_ids[0]:
        logging.error("Missing metadata in Stripe session")
        return
    
    try:
        user = User.objects.get(id=user_id)
        
        # Process each cart item
        for item_id in cart_items_ids:
            if not item_id:
                continue
                
            try:
                cart_item = CartItem.objects.get(id=item_id, user=user)
                
                # Record rank purchase
                if cart_item.rank:
                    purchase = UserPurchase.objects.create(
                        user=user,
                        rank=cart_item.rank,
                        amount=cart_item.rank.price,
                        payment_id=session.id,
                        payment_status='completed'
                    )
                    
                    # Apply rank on Minecraft server
                    minecraft_username = user.profile.minecraft_username
                    if minecraft_username:
                        success = apply_rank_to_player(minecraft_username, cart_item.rank.name)
                        if success:
                            logging.info(f"Rank {cart_item.rank.name} successfully applied to Minecraft player {minecraft_username}")
                        else:
                            logging.error(f"Failed to apply rank {cart_item.rank.name} to player {minecraft_username}")
                    else:
                        logging.warning(f"User {user.username} doesn't have a Minecraft username set; rank not applied")
                
                # Record store item purchase
                elif cart_item.store_item:
                    # Create StoreItemPurchase record
                    item_purchase = StoreItemPurchase.objects.create(
                        user=user,
                        store_item=cart_item.store_item,
                        quantity=cart_item.quantity,
                        amount=cart_item.store_item.price * cart_item.quantity,
                        payment_id=session.id,
                        payment_status='completed'
                    )
                    
                    # Update store item quantity if it's limited
                    if cart_item.store_item.quantity > 0:
                        cart_item.store_item.quantity -= cart_item.quantity
                        if cart_item.store_item.quantity < 0:
                            cart_item.store_item.quantity = 0
                        cart_item.store_item.save()
                    
                    # Apply store item benefits if applicable
                    # This depends on what the items do in your system
                    # For example:
                    minecraft_username = user.profile.minecraft_username
                    if minecraft_username:
                        # Implement item-specific logic here based on item type/category
                        if cart_item.store_item.category == 'collectible':
                            # Logic for collectible items
                            pass
                        elif cart_item.store_item.category == 'cosmetic':
                            # Logic for cosmetic items
                            pass
                        elif cart_item.store_item.category == 'utility':
                            # Logic for utility items
                            pass
                        elif cart_item.store_item.category == 'special':
                            # Logic for special items
                            pass
                
                # Remove from cart after processing
                cart_item.delete()
                
            except CartItem.DoesNotExist:
                logging.error(f"Cart item with ID {item_id} not found")
        
        logging.info(f"Payment successful for user {user.username}")
        
    except User.DoesNotExist:
        logging.error(f"User with ID {user_id} not found")


def is_minecraft_username_unique(username, current_user=None):
    """
    Vérifie si un pseudo Minecraft est unique dans la base de données
    Exclut l'utilisateur actuel si fourni (pour la mise à jour du profil)
    """
    if not username:
        return True
    
    existing_profiles = UserProfile.objects.filter(minecraft_username=username)
    if current_user:
        existing_profiles = existing_profiles.exclude(user=current_user)
    
    return not existing_profiles.exists()