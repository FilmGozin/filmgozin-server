from django.urls import path
from .views import (
    RequestPhonenumberOTPView,
    VerifyPhoneNumberOTPView,
    UserListView,
    ProfileView,
    ContactMessageView,
    ContactMessagesListView,
    QuestionnaireView,
    UserSignupView,
    UserLoginView,
    EmailVerificationView,
    RequestVerificationEmailView,
)

app_name = 'user'

urlpatterns = [
    # Authentication
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),

    # Verification
    path('request-verification/', RequestVerificationEmailView.as_view(), name='request-verification'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('request-phonenumber-otp/', RequestPhonenumberOTPView.as_view(), name='request-phonenumber-otp'),
    path('verify-phonenumber/', VerifyPhoneNumberOTPView.as_view(), name='verify-phonenumber'),

    # User Profile
    path('users/', UserListView.as_view(), name='user-list'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('questionnaire/', QuestionnaireView.as_view(), name='questionnaire'),

    # Contact Us
    path('contact/', ContactMessageView.as_view(), name='contact'),
    path('contact-messages/', ContactMessagesListView.as_view(), name='contact-messages-list'),
]