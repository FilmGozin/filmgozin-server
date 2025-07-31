import random
import uuid
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import Profile
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
    sms_provider = get_sms_provider()
    return sms_provider.send_otp(phone_number, code)


def send_verification_email(user):
    """Send verification email with OTP token"""
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
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


class UserSignupView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create profile for the user
            Profile.objects.get_or_create(user=user)
            
            # Send verification email
            if send_verification_email(user):
                return Response({
                    'message': 'User registered successfully. Please check your email to verify your account.',
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': 'User registered successfully but failed to send verification email.',
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'token': token.key
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
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
                    'error': 'Invalid or expired verification token'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        if user.is_email_verified:
            return Response({
                'error': 'Email is already verified'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if send_verification_email(user):
            return Response({
                'message': 'Verification email sent successfully'
            })
        else:
            return Response({
                'error': 'Failed to send verification email'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RequestPhonenumberOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            # Store OTP in cache with 2 minutes expiry
            cache_key = f"otp_{phone_number}"
            cache.set(cache_key, code, timeout=120)

            if send_otp(phone_number, code):
                return Response({'message': 'OTP sent successfully'})
            return Response(
                {'error': 'Failed to send OTP'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyPhoneNumberOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            submitted_code = serializer.validated_data['code']

            # Get OTP from cache
            cache_key = f"otp_{phone_number}"
            stored_code = cache.get(cache_key)

            if not stored_code:
                return Response(
                    {'error': 'OTP expired or invalid'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if submitted_code == stored_code:
                # Clear the OTP from cache
                cache.delete(cache_key)

                user, created = User.objects.get_or_create(
                    phone_number=phone_number,
                    defaults={'is_phone_verified': True}
                )
                if not created:
                    user.is_phone_verified = True
                    user.save()

                Profile.objects.get_or_create(user=user)

                token, _ = Token.objects.get_or_create(user=user)

                return Response({
                    'message': 'Phone number verified successfully',
                    'user': UserSerializer(user).data,
                    'token': token.key
                })

            return Response(
                {'error': 'Invalid OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print(f"Validation errors: {serializer.errors}")
            raise
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class ContactMessageView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionnaireView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        return Response({
            'questionnaire_answers': profile.questionnaire_answers
        })

    def post(self, request):
        profile = request.user.profile
        answers = request.data.get('answers', {})
        profile.questionnaire_answers = answers
        profile.save()
        return Response({
            'message': 'Questionnaire answers saved successfully',
            'questionnaire_answers': profile.questionnaire_answers
        })

    def delete(self, request):
        profile = request.user.profile
        profile.questionnaire_answers = {}
        profile.save()
        return Response({
            'message': 'Questionnaire answers deleted successfully'
        })
