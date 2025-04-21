from django.db import models
from django.contrib.auth.models import User

class TownyServer(models.Model):
    name = models.CharField(max_length=100, default="GeoMC - Earth Towny")
    ip_address = models.CharField(max_length=100, default="play.geomc.fr")
    description = models.TextField(default="Serveur Towny sur une carte de la Terre à l'échelle 1:1000")
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
    flag_image = models.CharField(max_length=255, blank=True, null=True, help_text="URL de l'image du drapeau")
    real_world_country = models.CharField(max_length=100, blank=True, help_text="Pays réel représenté")
    
    def __str__(self):
        return self.name

class Town(models.Model):
    name = models.CharField(max_length=100)
    mayor = models.CharField(max_length=100)
    nation = models.ForeignKey(Nation, on_delete=models.SET_NULL, null=True, blank=True, related_name='towns')
    founded_date = models.DateField()
    description = models.TextField(blank=True)
    residents_count = models.IntegerField(default=1)
    location_x = models.IntegerField(help_text="Coordonnée X sur la carte")
    location_z = models.IntegerField(help_text="Coordonnée Z sur la carte")
    real_world_location = models.CharField(max_length=100, blank=True, help_text="Lieu réel représenté")
    
    def __str__(self):
        return self.name

class StaffMember(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('mod', 'Modérateur'),
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
    color_code = models.CharField(max_length=7, help_text="Code couleur HEX (ex: #FF0000)")
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
        ('town', 'Ville'),
        ('capital', 'Capitale'),
        ('warp', 'Point de téléportation'),
        ('shop', 'Magasin'),
        ('pve', 'Zone PvE'),
        ('pvp', 'Zone PvP'),
    ]
    
    name = models.CharField(max_length=100)
    point_type = models.CharField(max_length=20, choices=POINT_TYPE_CHOICES)
    location_x = models.IntegerField(help_text="Coordonnée X sur la carte")
    location_z = models.IntegerField(help_text="Coordonnée Z sur la carte")
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_point_type_display()})"