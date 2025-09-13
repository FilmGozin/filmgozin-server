import random
import uuid
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import IntegrityError, DatabaseError
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from .models import Profile
from .models import ContactMessage
from .sms import get_sms_provider
from .serializers import (
    PhoneNumberSerializer,
    VerifyOTPSerializer,
    UserSerializer,
    ProfileSerializer,
    ContactMessageSerializer,
    UserSignupSerializer,
    UserLoginSerializer,
    EmailVerificationSerializer,
)

User = get_user_model()


def send_otp(phone_number, code):
    """Send OTP via SMS with error handling"""
    try:
        sms_provider = get_sms_provider()
        return sms_provider.send_otp(phone_number, code)
    except Exception as e:
        print(f"SMS sending error: {e}")
        return False


def send_verification_email(user):
    """Send verification email with OTP token"""
    try:
        token = str(uuid.uuid4())
        user.email_verification_token = token
        user.email_verification_expires = timezone.now() + timedelta(hours=24)
        user.save()
        
        subject = 'Verify your email address - FilmGozin'
        message = f"""
        Hello {user.username},
        
        Please verify your email address by clicking the link below:
        
        {settings.FRONTEND_URL}/verify-email?token={token}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        FilmGozin Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending error: {e}")
        return False


class UserSignupView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            serializer = UserSignupSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    user = serializer.save()
                    
                    # Create profile for the user
                    Profile.objects.get_or_create(user=user)
                    # try:
                    #     Profile.objects.get_or_create(user=user)
                    # except Exception as e:
                    #     return Response({
                    #         'error': 'Failed to create user profile',
                    #         'details': str(e)
                    #     }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                    return Response({
                        'message': 'User registered successfully',
                        'user': UserSerializer(user).data
                    }, status=status.HTTP_201_CREATED)
                    # Send verification email
                    # if send_verification_email(user):
                    #     return Response({
                    #         'message': 'User registered successfully. Please check your email to verify your account.',
                    #         'user': UserSerializer(user).data
                    #     }, status=status.HTTP_201_CREATED)
                    # else:
                    #     return Response({
                    #         'message': 'User registered successfully but failed to send verification email. Please contact support.',
                    #         'user': UserSerializer(user).data,
                    #         'warning': 'Email verification not sent'
                    #     }, status=status.HTTP_201_CREATED)
                        
                except IntegrityError as e:
                    # Handle specific integrity constraint violations
                    error_message = str(e)
                    if 'username' in error_message.lower():
                        return Response({
                            'error': 'Username already exists',
                            'details': 'This username is already taken. Please choose a different username.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    elif 'email' in error_message.lower():
                        return Response({
                            'error': 'Email already exists',
                            'details': 'A user with this email address already exists. Please use a different email or try logging in.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    elif 'phone_number' in error_message.lower():
                        return Response({
                            'error': 'Phone number already exists',
                            'details': 'This phone number is already registered with another account.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({
                            'error': 'Database integrity error',
                            'details': 'User creation failed due to database constraints. Please check your input data.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                except DatabaseError as e:
                    return Response({
                        'error': 'Database error',
                        'details': 'Failed to create user due to database issues. Please try again later.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                except Exception as e:
                    return Response({
                        'error': 'User creation failed',
                        'details': f'An unexpected error occurred: {str(e)}'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Unexpected error occurred',
                'details': f'Server error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    user = serializer.validated_data['user']
                    token, _ = Token.objects.get_or_create(user=user)
                    
                    return Response({
                        'message': 'Login successful',
                        'user': UserSerializer(user).data,
                        'token': token.key
                    })
                except Exception as e:
                    return Response({
                        'error': 'Authentication failed',
                        'details': 'Failed to create authentication token'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                'error': 'Login failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserSerializer

    def get(self, request):
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response({'users': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve users',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class EmailVerificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            serializer = EmailVerificationSerializer(data=request.data)
            if serializer.is_valid():
                token = serializer.validated_data['token']
                
                try:
                    user = User.objects.get(
                        email_verification_token=token,
                        email_verification_expires__gt=timezone.now()
                    )
                    
                    user.is_email_verified = True
                    user.email_verification_token = None
                    user.email_verification_expires = None
                    user.save()
                    
                    return Response({
                        'message': 'Email verified successfully',
                        'user': UserSerializer(user).data
                    })
                    
                except User.DoesNotExist:
                    return Response({
                        'error': 'Invalid or expired verification token',
                        'details': 'The verification token is not valid or has expired'
                    }, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({
                        'error': 'Email verification failed',
                        'details': str(e)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                'error': 'Invalid token format',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RequestVerificationEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            
            if user.is_email_verified:
                return Response({
                    'error': 'Email is already verified',
                    'details': 'No verification email needed'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if send_verification_email(user):
                return Response({
                    'message': 'Verification email sent successfully'
                })
            else:
                return Response({
                    'error': 'Failed to send verification email',
                    'details': 'Email service is currently unavailable. Please try again later.'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except Exception as e:
            return Response({
                'error': 'Unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RequestPhonenumberOTPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = PhoneNumberSerializer(data=request.data)
            if serializer.is_valid():
                phone_number = serializer.validated_data['phone_number']
                code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

                # Store OTP in cache with 2 minutes expiry
                try:
                    cache_key = f"otp_{phone_number}"
                    cache.set(cache_key, code, timeout=120)
                except Exception as e:
                    return Response({
                        'error': 'Cache service unavailable',
                        'details': 'Failed to store OTP code'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

                if send_otp(phone_number, code):
                    return Response({'message': 'OTP sent successfully'})
                else:
                    return Response({
                        'error': 'Failed to send OTP',
                        'details': 'SMS service is currently unavailable. Please try again later.'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                    
            return Response({
                'error': 'Invalid phone number',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyPhoneNumberOTPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = VerifyOTPSerializer(data=request.data)
            if serializer.is_valid():
                phone_number = serializer.validated_data['phone_number']
                submitted_code = serializer.validated_data['code']

                # Get OTP from cache
                try:
                    cache_key = f"otp_{phone_number}"
                    stored_code = cache.get(cache_key)
                except Exception as e:
                    return Response({
                        'error': 'Cache service unavailable',
                        'details': 'Failed to retrieve OTP code'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

                if not stored_code:
                    return Response({
                        'error': 'OTP expired or invalid',
                        'details': 'The OTP code has expired or was never sent'
                    }, status=status.HTTP_400_BAD_REQUEST)

                if submitted_code == stored_code:
                    try:
                        # Clear the OTP from cache
                        cache.delete(cache_key)

                        # Check if user already exists with this phone number
                        try:
                            user = User.objects.get(phone_number=phone_number)
                            # User exists, just verify the phone number
                            user.is_phone_verified = True
                            user.save()
                        except User.DoesNotExist:
                            # Create new user with phone number
                            # Check if we need to generate a unique username
                            base_username = f"user_{phone_number.national_number}"
                            username = base_username
                            counter = 1
                            
                            # Ensure unique username
                            while User.objects.filter(username=username).exists():
                                username = f"{base_username}_{counter}"
                                counter += 1
                            
                            # Create placeholder email for phone-only users
                            placeholder_email = f"phone_{phone_number.national_number}@filmgozin.local"
                            
                            # Ensure email is unique
                            email_counter = 1
                            while User.objects.filter(email=placeholder_email).exists():
                                placeholder_email = f"phone_{phone_number.national_number}_{email_counter}@filmgozin.local"
                                email_counter += 1
                            
                            user = User.objects.create_user(
                                phone_number=phone_number,
                                username=username,
                                email=placeholder_email,
                                is_phone_verified=True
                            )

                        # Ensure profile exists
                        Profile.objects.get_or_create(user=user)
                        
                        # Create or get authentication token
                        token, _ = Token.objects.get_or_create(user=user)

                        return Response({
                            'message': 'Phone number verified successfully',
                            'user': UserSerializer(user).data,
                            'token': token.key
                        })
                        
                    except IntegrityError as e:
                        # Handle specific integrity errors
                        if 'phone_number' in str(e):
                            return Response({
                                'error': 'Phone number already exists',
                                'details': 'This phone number is already registered with another account'
                            }, status=status.HTTP_400_BAD_REQUEST)
                        elif 'username' in str(e):
                            return Response({
                                'error': 'Username conflict',
                                'details': 'Unable to create unique username for this phone number'
                            }, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({
                                'error': 'Database integrity error',
                                'details': 'Failed to update user verification status due to data constraints'
                            }, status=status.HTTP_400_BAD_REQUEST)
                    except DatabaseError as e:
                        return Response({
                            'error': 'Database error',
                            'details': 'Failed to process verification due to database issues'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    except Exception as e:
                        return Response({
                            'error': 'Verification processing failed',
                            'details': str(e)
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                return Response({
                    'error': 'Invalid OTP',
                    'details': 'The provided OTP code is incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            return Response({
                'error': 'Invalid input data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.profile
        except Profile.DoesNotExist:
            raise ValidationError("User profile not found")

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if serializer.is_valid():
                try:
                    self.perform_update(serializer)
                    return Response(serializer.data)
                except Exception as e:
                    return Response({
                        'error': 'Profile update failed',
                        'details': str(e)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({
                    'error': 'Validation failed',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except ValidationError as e:
            return Response({
                'error': 'Profile not found',
                'details': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': 'Unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_update(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            raise Exception(f"Failed to save profile: {str(e)}")


class ContactMessageView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            serializer = ContactMessageSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response({
                        'message': 'Contact message sent successfully',
                        'data': serializer.data
                    }, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({
                        'error': 'Failed to save contact message',
                        'details': str(e)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({
                    'error': 'Invalid contact message data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': 'Unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContactMessagesListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ContactMessageSerializer

    def get(self, request):
        try:
            messages = ContactMessage.objects.all()
            serializer = ContactMessageSerializer(messages, many=True)
            return Response({'contact_messages': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve contact messages',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

