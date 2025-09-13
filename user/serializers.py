from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from .models import Profile, ContactMessage
from movie.models import Questionnaire
from phonenumber_field.serializerfields import PhoneNumberField

User = get_user_model()


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(error_messages={
        'invalid': 'Please enter a valid phone number.',
        'required': 'Phone number is required.'
    })


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(error_messages={
        'invalid': 'Please enter a valid phone number.',
        'required': 'Phone number is required.'
    })
    code = serializers.CharField(
        max_length=6,
        error_messages={
            'required': 'OTP code is required.',
            'max_length': 'OTP code must be exactly 6 characters.'
        }
    )


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        validators=[validate_password],
        error_messages={
            'required': 'Password is required.',
            'blank': 'Password cannot be blank.'
        }
    )
    password_repeat = serializers.CharField(
        write_only=True,
        error_messages={
            'required': 'Password confirmation is required.',
            'blank': 'Password confirmation cannot be blank.'
        }
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_repeat')
        extra_kwargs = {
            'username': {
                'required': True,
                'error_messages': {
                    'required': 'Username is required.',
                    'blank': 'Username cannot be blank.',
                    'max_length': 'Username cannot exceed 150 characters.'
                }
            },
            'email': {
                'required': True,
                'error_messages': {
                    'required': 'Email address is required.',
                    'blank': 'Email address cannot be blank.',
                    'invalid': 'Please enter a valid email address.'
                }
            },
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_repeat']:
            raise serializers.ValidationError({
                'password_repeat': "Passwords don't match. Please make sure both passwords are identical."
            })
        return attrs
    
    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email address already exists. Please use a different email or try logging in."
            )
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "This username is already taken. Please choose a different username."
            )
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_repeat')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'].strip().lower(),
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            'required': 'Email address is required.',
            'blank': 'Email address cannot be blank.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    password = serializers.CharField(
        error_messages={
            'required': 'Password is required.',
            'blank': 'Password cannot be blank.'
        }
    )
    
    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        password = attrs.get('password')
        
        if email and password:
            # First check if user exists with this email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'email': 'No account found with this email address. Please check your email or sign up for a new account.'
                })
            
            # Then check if password is correct
            if not user.check_password(password):
                raise serializers.ValidationError({
                    'password': 'Incorrect password. Please check your password and try again.'
                })
            
            # Check if user is active
            if not user.is_active:
                raise serializers.ValidationError({
                    'non_field_errors': 'Your account has been disabled. Please contact support for assistance.'
                })
            
            attrs['user'] = user
        else:
            raise serializers.ValidationError({
                'non_field_errors': 'Both email address and password are required.'
            })
        
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(
        error_messages={
            'required': 'Verification token is required.',
            'blank': 'Verification token cannot be blank.'
        }
    )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'phone_number', 'email', 'is_phone_verified', 'is_email_verified')
        read_only_fields = ('is_phone_verified', 'is_email_verified',)

class ProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()
    email = serializers.EmailField(
        source='user.email', 
        required=False, 
        allow_blank=True,
        error_messages={
            'invalid': 'Please enter a valid email address.'
        }
    )
    first_name = serializers.CharField(
        required=False, 
        allow_blank=True,
        error_messages={
            'max_length': 'First name cannot exceed 100 characters.'
        }
    )
    last_name = serializers.CharField(
        required=False, 
        allow_blank=True,
        error_messages={
            'max_length': 'Last name cannot exceed 100 characters.'
        }
    )
    liked_movies = serializers.JSONField(required=False)

    class Meta:
        model = Profile
        fields = (
            'id', 'phone_number', 'email', 'avatar', 'first_name', 'last_name',
            'bio', 'birth_date', 'gender', 'city', 'interests', 'liked_movies',
            'suggested_movies', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'phone_number', 'created_at', 'updated_at', 'suggested_movies')

    def get_phone_number(self, obj):
        return str(obj.user.phone_number)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if 'email' in user_data:
            instance.user.email = user_data['email']
            instance.user.save()
        return super().update(instance, validated_data)


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ('id', 'name', 'email', 'message', 'created_at', 'is_read')
        read_only_fields = ('id', 'created_at', 'is_read')
        extra_kwargs = {
            'name': {
                'required': True,
                'error_messages': {
                    'required': 'Name is required.',
                    'blank': 'Name cannot be blank.',
                    'max_length': 'Name cannot exceed 100 characters.'
                }
            },
            'email': {
                'required': True,
                'error_messages': {
                    'required': 'Email address is required.',
                    'blank': 'Email address cannot be blank.',
                    'invalid': 'Please enter a valid email address.'
                }
            },
            'message': {
                'required': True,
                'error_messages': {
                    'required': 'Message is required.',
                    'blank': 'Message cannot be blank.'
                }
            }
        }