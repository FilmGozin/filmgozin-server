from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number=None, email=None, password=None, **extra_fields):
        if not phone_number and not email:
            raise ValueError(_('Either Phone Number or Email must be set'))
        
        if email:
            email = self.normalize_email(email)
        
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(phone_number, email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    phone_number = PhoneNumberField(unique=True, null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, null=True, blank=True)
    email_verification_expires = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email or str(self.phone_number) or self.username or 'Anonymous User'

    def clean(self):
        if not self.email and not self.phone_number:
            raise ValueError(_('Either email or phone number must be provided'))

    def save(self, *args, **kwargs):
        # Ensure we have at least one identifier
        if not self.email and not self.phone_number:
            raise ValueError(_('Either email or phone number must be provided'))
        
        # If using email as USERNAME_FIELD, ensure it's not empty when saving
        if not self.email and self.phone_number:
            # For phone-only users, we'll use a placeholder email
            # This is a workaround for Django's authentication system
            if not self.pk:  # Only for new users
                self.email = f"phone_{self.phone_number.national_number}@filmgozin.local"
        
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        """Return the best available display name"""
        if self.username:
            return self.username
        elif self.email and '@' in self.email and not self.email.startswith('phone_'):
            return self.email.split('@')[0]
        elif self.phone_number:
            return str(self.phone_number)
        else:
            return 'Anonymous User'

    
class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone_number = PhoneNumberField(blank=True)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    city = models.CharField(max_length=100, blank=True)
    interests = models.JSONField(default=list, blank=True)
    liked_movies = models.JSONField(default=list, blank=True)  # Store movie IDs
    suggested_movies = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.phone_number}'s profile"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name}"