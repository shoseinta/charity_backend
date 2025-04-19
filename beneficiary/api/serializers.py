#a serializer for the Beneficiary model and models related to that
from rest_framework import serializers
from beneficiary.models import (
    BeneficiaryUserRegistration,
    BeneficiaryUserInformation,
    BeneficiaryUserAddress,
    Province,
    City,
)
from request.models import (
    BeneficiaryRequest,
    BeneficiaryRequestDurationOnetime,
    BeneficiaryRequestDurationRecurring,
    BeneficiaryRequestHistory,
    BeneficiaryRequestChild,
)


class BeneficiaryUserInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserInformation
        fields = '__all__'

class BeneficiaryUserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAddress
        fields = '__all__'

class BeneficiaryUserSerializer(serializers.ModelSerializer):
    beneficiary_user_information = BeneficiaryUserInformationSerializer()
    beneficiary_user_address = BeneficiaryUserAddressSerializer()

    class Meta:
        model = BeneficiaryUserRegistration
        exclude = ['password']