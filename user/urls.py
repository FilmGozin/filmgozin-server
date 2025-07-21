from django.urls import path
from .views import (
    RequestOTPView,
    VerifyOTPView,
    ProfileView,
    ContactMessageView,
    QuestionnaireView,
)

app_name = 'user'

urlpatterns = [
    path('request-otp/', RequestOTPView.as_view(), name='request-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('contact/', ContactMessageView.as_view(), name='contact'),
    path('questionnaire/', QuestionnaireView.as_view(), name='questionnaire'),
]