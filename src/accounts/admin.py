from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, InactiveUser, StaffUser, CustomerUser, Profile


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'phone_number', 'get_username')
    list_filter = ('is_verified', 'is_staff')
    ordering = ('email', )
    
    fieldsets = (
        (None, {'fields': ('email', 'phone_number', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified','groups', 'user_permissions')}),
        ('dates', {'fields': ('last_login', )}),
    )
    
    
    add_fieldsets = (
        (None, {'fields': ('email', 'phone_number', 'password1', 'password2')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified','groups', 'user_permissions')}),
        ('dates', {'fields': ('last_login', )}),
    )
    
    def get_username(self, instance):
        return instance.profile.username if instance.profile and instance.profile.username else '?'
    
    get_username.short_description = 'username'


@admin.register(User)
class UserAdmin(CustomUserAdmin):
    actions = ["deactivate_users"]
    
    @admin.action
    def deactivate_users(self, request, queryset):
        queryset.delete()
    

@admin.register(InactiveUser)
class InactiveUserAdmin(CustomUserAdmin):
    
    actions = ["activate_users"]
    
    @admin.action
    def activate_users(self, request, queryset):
        queryset.delete()
    

admin.site.register(StaffUser, UserAdmin)
admin.site.register(CustomerUser, UserAdmin)
admin.site.register(Profile)