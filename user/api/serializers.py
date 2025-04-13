# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from charity.models import Charity
from beneficiary.models import BeneficiaryUserRegistration
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
            charity_user = Charity.objects.filter(charity_username=username, charity_password=password)
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
    

class BeneficiaryRegistrationSerializer(serializers.ModelSerializer):
    charity_id = serializers.PrimaryKeyRelatedField(
        queryset=Charity.objects.all(),
        source='charity',
        write_only=True,
        required=True
    )
    
    class Meta:
        model = User
        fields = ('username', 'charity_id')  # Add charity_id to fields

    def validate_username(self, value):
        """
        Validate that username:
        1. Must be all numeric
        2. Must have length of exactly 10 digits
        """
        if not value.isdigit():
            raise serializers.ValidationError("Identification number must be all digits")
        
        if len(value) != 10:
            raise serializers.ValidationError("Length of identification number must be 10 digits")
            
        return value

    def validate(self, attrs):
        if BeneficiaryUserRegistration.objects.filter(identification_number=attrs['username']).exists():
            raise serializers.ValidationError({"username": "This beneficiary already exists"})
        return attrs

    def create(self, validated_data):
        # Extract charity from validated_data
        charity = validated_data.pop('charity')
        
        user = User.objects.create(
            username=validated_data['username'],
        )

        beneficiary = BeneficiaryUserRegistration.objects.create(
            benficiary_user_id=user,
            identification_number=validated_data['username'],
            beneficiary_id=validated_data['username'],
            password=validated_data['username'],
            charity=charity,  # Assign the selected charity
            # Add other required fields with default values if needed
        )
        beneficiary.save()
        user.set_password(validated_data['username'])
        user.save()
        
        return user
    
class BeneficiaryLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                              username=username, password=password)
            beneficiary_user = BeneficiaryUserRegistration.objects.filter(identification_number=username, password=password)
            if not user:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
            if not beneficiary_user:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")
        
        data['user'] = user
        return data