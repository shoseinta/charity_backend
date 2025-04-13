# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from charity.models import Charity
from django.contrib.auth.password_validation import validate_password

class CharityRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
        )
        charity = Charity(
            charity_user_id=user,
            charity_username=validated_data['username'],
            charity_password=validated_data['password'],
        )
        charity.save()
        user.set_password(validated_data['password'])
        user.save()
        return user