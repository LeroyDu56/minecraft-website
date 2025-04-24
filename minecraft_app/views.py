from django.shortcuts import render, get_object_or_404
from .models import TownyServer, Nation, Town, StaffMember, Rank, ServerRule, DynamicMapPoint, UserProfile, UserPurchase
from django.db.models import Count, Sum
from django.urls import reverse
from django.http import HttpResponse
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
    email = forms.EmailField()
    minecraft_username = forms.CharField(max_length=100, required=False, help_text="Your Minecraft username")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'minecraft_username']

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
        try:
            purchase = UserPurchase.objects.get(payment_id=session_id)
            return render(request, 'minecraft_app/payment_success.html', {
                'purchase': purchase,
                'server': TownyServer.objects.first()
            })
        except UserPurchase.DoesNotExist:
            pass
    
    # Fallback if purchase not found (can happen if webhook hasn't processed yet)
    return render(request, 'minecraft_app/payment_success.html', {
        'server': TownyServer.objects.first()
    })

def payment_cancel(request):
      return render(request, 'minecraft_app/payment_cancel.html')

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