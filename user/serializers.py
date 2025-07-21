from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, ContactMessage
from phonenumber_field.serializerfields import PhoneNumberField

User = get_user_model()


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    code = serializers.CharField(max_length=6)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'email', 'is_phone_verified')
        read_only_fields = ('is_phone_verified',)


class ProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    liked_movies = serializers.JSONField(required=False)
    questionnaire_answers = serializers.JSONField(required=False)

    class Meta:
        model = Profile
        fields = ('id', 'phone_number', 'email', 'avatar', 'first_name', 'last_name',
                 'bio', 'birth_date', 'gender', 'city', 'interests', 'liked_movies',
                 'questionnaire_answers', 'created_at', 'updated_at')
        read_only_fields = ('id', 'phone_number', 'created_at', 'updated_at')

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
        fields = ('id', 'name', 'email', 'phone_number', 'message', 'created_at', 'is_read')
        read_only_fields = ('id', 'created_at', 'is_read')