from rest_framework import serializers
from beneficiary.models import BeneficiaryUserRegistration,BeneficiaryUserInformation,BeneficiaryUserAddress,BeneficiaryUserAdditionalInfo


class BeneficiaryInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserInformation
        fields = ["beneficiary_user_information_id",
                   "under_charity_support",
                   "first_name",
                   "last_name",
                   "gender"]
        
class BeneficiaryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAddress
        fields = ["beneficiary_user_address_id",
                   "province",
                   "city"]

class BeneficiaryAdditionalInfo(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAdditionalInfo
        fields = "__all__"

class BeneficiaryListSerializer(serializers.ModelSerializer):
    beneficiary_user_information = BeneficiaryInformationSerializer()
    beneficiary_user_address = BeneficiaryAddressSerializer()
    beneficiary_user_additional_info = BeneficiaryAdditionalInfo(many=True)
    class Meta:
        model = BeneficiaryUserRegistration
        fields = ["beneficiary_user_registration_id",
                  "identification_number",
                  "beneficiary_id",
                  "phone_number",
                  "email",
                  "beneficiary_user_information",
                  "beneficiary_user_address",
                  "beneficiary_user_additional_info"
                  ]

