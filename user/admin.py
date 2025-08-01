from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profile, ContactMessage


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('phone_number', 'email', 'username', 'is_staff', 'is_active', 'is_phone_verified', 'is_email_verified', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_phone_verified', 'is_email_verified', 'date_joined')
    fieldsets = (
        (None, {'fields': ('phone_number', 'email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'is_phone_verified', 'is_email_verified', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Verification'), {'fields': ('email_verification_token', 'email_verification_expires')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'email', 'username', 'password1', 'password2'),
        }),
    )
    search_fields = ('phone_number', 'email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    list_per_page = 25


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'city', 'gender', 'birth_date', 'created_at')
    list_filter = ('gender', 'city', 'created_at')
    search_fields = ('user__phone_number', 'user__email', 'user__username', 'first_name', 'last_name', 'city')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('user',)}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'phone_number', 'bio', 'birth_date', 'gender', 'city')}),
        (_('Media'), {'fields': ('avatar',)}),
        (_('Preferences'), {'fields': ('interests', 'liked_movies', 'questionnaire_answers')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    list_per_page = 25


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'phone_number', 'message')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)
    ordering = ('-created_at',)
    list_per_page = 25


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
