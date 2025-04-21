from django.contrib import admin
from .models import TownyServer, Nation, Town, StaffMember, Rank, ServerRule, DynamicMapPoint, UserProfile

admin.site.register(TownyServer)
admin.site.register(Nation)
admin.site.register(Town)
admin.site.register(StaffMember)
admin.site.register(Rank)
admin.site.register(ServerRule)
admin.site.register(DynamicMapPoint)
admin.site.register(UserProfile)