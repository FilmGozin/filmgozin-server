import random
from django.contrib.auth import get_user_model
from django.core.cache import cache
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
)

User = get_user_model()


def send_otp(phone_number, code):
    sms_provider = get_sms_provider()
    return sms_provider.send_otp(phone_number, code)


class RequestOTPView(APIView):
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


class VerifyOTPView(APIView):
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
