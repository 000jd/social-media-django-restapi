from django.contrib import admin
from .models import User, Profile

class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'avatar', 'is_active', 'is_admin', 'created_at']
    search_fields = ['username', 'email']
    list_filter = ['username', 'email'] 

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['avatar', 'user']
    search_fields = ['user__username', 'user__email']
    list_filter = ['user__username', 'user__email'] 

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
