from django.urls import path
from .views import (
    RequestPhonenumberOTPView,
    VerifyPhoneNumberOTPView,
    ProfileView,
    ContactMessageView,
    QuestionnaireView,
    UserSignupView,
    UserLoginView,
    EmailVerificationView,
    ResendVerificationEmailView,
)

app_name = 'user'

urlpatterns = [
    # Authentication
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),

    # Verification
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),
    path('request-phonenumber-otp/', RequestPhonenumberOTPView.as_view(), name='request-phonenumber-otp'),
    path('verify-phonenumber/', VerifyPhoneNumberOTPView.as_view(), name='verify-phonenumber'),

    # User Profile
    path('profile/', ProfileView.as_view(), name='profile'),
    path('questionnaire/', QuestionnaireView.as_view(), name='questionnaire'),

    # Contact Us
    path('contact/', ContactMessageView.as_view(), name='contact'),
]