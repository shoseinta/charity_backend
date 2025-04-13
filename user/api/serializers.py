# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from charity.models import Charity
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate


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
    

class CharityLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                              username=username, password=password)
            charity_user = Charity.objects.filter(charity_username=username, charity_password=password).first()
            if not user:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
            if not charity_user:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")
        
        data['user'] = user
        return data