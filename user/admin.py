from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profile, ContactMessage


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('phone_number', 'email', 'is_staff', 'is_active', 'is_phone_verified')
    list_filter = ('is_staff', 'is_active', 'is_phone_verified')
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'is_phone_verified', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2'),
        }),
    )
    search_fields = ('phone_number', 'email')
    ordering = ('phone_number',)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'gender', 'created_at')
    list_filter = ('gender', 'city')
    search_fields = ('user__phone_number', 'city')
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(ContactMessage)
