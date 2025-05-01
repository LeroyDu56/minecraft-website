from django.db import models
from django.contrib.auth.models import User
import logging

class TownyServer(models.Model):
    name = models.CharField(max_length=100, default="Novania - Earth Towny")
    ip_address = models.CharField(max_length=100, default="play.Novania.fr")
    description = models.TextField(default="Towny server on a 1:1000 scale Earth map")
    version = models.CharField(max_length=20, default="1.20.4")
    player_count = models.IntegerField(default=0)
    max_players = models.IntegerField(default=100)
    status = models.BooleanField(default=True)  # True = online, False = offline
    discord_link = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Towny Server"

class Nation(models.Model):
    name = models.CharField(max_length=100)
    leader = models.CharField(max_length=100)
    founded_date = models.DateField()
    description = models.TextField(blank=True)
    capital = models.CharField(max_length=100)
    flag_image = models.CharField(max_length=255, blank=True, null=True, help_text="URL of the flag image")
    real_world_country = models.CharField(max_length=100, blank=True, help_text="Real world country represented")
    
    def __str__(self):
        return self.name

class Town(models.Model):
    name = models.CharField(max_length=100)
    mayor = models.CharField(max_length=100)
    nation = models.ForeignKey(Nation, on_delete=models.SET_NULL, null=True, blank=True, related_name='towns')
    founded_date = models.DateField()
    description = models.TextField(blank=True)
    residents_count = models.IntegerField(default=1)
    location_x = models.IntegerField(help_text="X coordinate on the map")
    location_z = models.IntegerField(help_text="Z coordinate on the map")
    real_world_location = models.CharField(max_length=100, blank=True, help_text="Real world location represented")
    
    def __str__(self):
        return self.name

class StaffMember(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('mod', 'Moderator'),
        ('helper', 'Helper'),
        ('builder', 'Builder'),
    ]
    
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    minecraft_uuid = models.CharField(max_length=36, blank=True, null=True)
    description = models.TextField(blank=True)
    discord_username = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

class Rank(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    color_code = models.CharField(max_length=7, help_text="HEX color code (e.g.: #FF0000)")
    is_donation = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class ServerRule(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']

class DynamicMapPoint(models.Model):
    POINT_TYPE_CHOICES = [
        ('town', 'Town'),
        ('capital', 'Capital'),
        ('warp', 'Teleport Point'),
        ('shop', 'Shop'),
        ('pve', 'PvE Zone'),
        ('pvp', 'PvP Zone'),
    ]
    
    name = models.CharField(max_length=100)
    point_type = models.CharField(max_length=20, choices=POINT_TYPE_CHOICES)
    location_x = models.IntegerField(help_text="X coordinate on the map")
    location_z = models.IntegerField(help_text="Z coordinate on the map")
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_point_type_display()})"
    
    # Ajoutez ceci à la fin de minecraft_app/models.py

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    minecraft_username = models.CharField(max_length=100, blank=True)
    minecraft_uuid = models.CharField(max_length=36, blank=True)
    bio = models.TextField(blank=True)
    discord_username = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Profil de {self.user.username}"
    
    def get_avatar_url(self):
        if self.minecraft_uuid:
            return f"https://mc-heads.net/avatar/{self.minecraft_uuid}/100"
        elif self.minecraft_username:
            return f"https://mc-heads.net/avatar/{self.minecraft_username}/100"
        else:
            return "https://mc-heads.net/avatar/MHF_Steve/100"  # Avatar par défaut
        
class UserPurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    rank = models.ForeignKey(Rank, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_id = models.CharField(max_length=100, unique=True)
    payment_status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    is_gift = models.BooleanField(default=False)
    gifted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='gifts_given')
    
    def __str__(self):
        if self.is_gift and self.gifted_by:
            return f"{self.user.username} - {self.rank.name if self.rank else 'Rank supprimé'} (Gift from {self.gifted_by.username})"
        return f"{self.user.username} - {self.rank.name if self.rank else 'Rank supprimé'}"
    
class StoreItem(models.Model):
    CATEGORY_CHOICES = [
        ('collectible', 'Collectible'),
        ('cosmetic', 'Cosmetic'),
        ('utility', 'Utility'),
        ('special', 'Special'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.CharField(max_length=255, help_text="URL of the item image", blank=True, null=True)
    color_code = models.CharField(max_length=7, help_text="HEX color code (e.g.: #FF0000)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='collectible')
    quantity = models.IntegerField(default=1, help_text="Available quantity (-1 for unlimited)")
    
    def __str__(self):
        return self.name

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    rank = models.ForeignKey(Rank, on_delete=models.SET_NULL, null=True, blank=True)
    store_item = models.ForeignKey(StoreItem, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [
            ('user', 'rank'),
            ('user', 'store_item'),
        ]
    
    def __str__(self):
        if self.rank:
            return f"{self.user.username} - {self.rank.name}"
        elif self.store_item:
            return f"{self.user.username} - {self.store_item.name} (x{self.quantity})"
        return f"{self.user.username} - Unknown item"
    
    def get_subtotal(self):
        if self.rank:
            return self.rank.price
        elif self.store_item:
            return self.store_item.price * self.quantity
        return 0
    
    def save(self, *args, **kwargs):
        logger = logging.getLogger(__name__)
        logger.debug("DEBUG: Saving CartItem %s: quantity=%s", self.id, self.quantity)
        super().save(*args, **kwargs)
        logger.debug("DEBUG: Saved CartItem %s: quantity=%s", self.id, self.quantity)
    

class StoreItemPurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='store_item_purchases')
    store_item = models.ForeignKey(StoreItem, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=20, default='completed')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.store_item.name if self.store_item else 'Deleted item'} x{self.quantity}"

class WebhookError(models.Model):
    event_type = models.CharField(max_length=100)
    session_id = models.CharField(max_length=100)
    error_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.session_id} - {self.error_message[:50]}"