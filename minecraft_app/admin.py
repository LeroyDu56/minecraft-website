from django.contrib import admin
from .models import TownyServer, Nation, Town, StaffMember, Rank, ServerRule, DynamicMapPoint, UserProfile, UserPurchase, StoreItem, CartItem

# Basic admin registration for existing models
admin.site.register(TownyServer)
admin.site.register(Nation)
admin.site.register(Town)
admin.site.register(ServerRule)
admin.site.register(DynamicMapPoint)
admin.site.register(UserProfile)

# Enhanced admin configuration for StaffMember
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'discord_username')
    list_filter = ('role',)
    search_fields = ('name', 'discord_username')

admin.site.register(StaffMember, StaffMemberAdmin)

# Enhanced admin configuration for Rank
class RankAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'color_code', 'is_donation')
    list_filter = ('is_donation',)
    search_fields = ('name',)

admin.site.register(Rank, RankAdmin)

# Enhanced admin configuration for UserPurchase
class UserPurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'rank', 'amount', 'payment_status', 'created_at')
    list_filter = ('payment_status', 'created_at')
    search_fields = ('user__username', 'rank__name', 'payment_id')
    date_hierarchy = 'created_at'

admin.site.register(UserPurchase, UserPurchaseAdmin)

# New admin configuration for StoreItem
class StoreItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'quantity', 'color_code')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'price')
        }),
        ('Appearance', {
            'fields': ('image', 'color_code')
        }),
        ('Classification', {
            'fields': ('category', 'quantity')
        }),
    )

admin.site.register(StoreItem, StoreItemAdmin)

# New admin configuration for CartItem
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_item_name', 'quantity', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username',)
    date_hierarchy = 'added_at'
    
    def get_item_name(self, obj):
        if obj.rank:
            return f"Rank: {obj.rank.name}"
        elif obj.store_item:
            return f"Item: {obj.store_item.name}"
        return "Unknown item"
    
    get_item_name.short_description = 'Item'

admin.site.register(CartItem, CartItemAdmin)