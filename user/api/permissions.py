from rest_framework.permissions import BasePermission
from charity.models import Charity
class IsAdminOrCharity(BasePermission):
    def has_permission(self, request, view):
        return request.user in Charity.objects.all() or request.user.is_staff
    
class IsCertainBeneficiary(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff or Charity.objects.filter(charity_username=request.user).exists():
            return True
        try:
            beneficiary_user_registration_id = view.kwargs['beneficiary_user_registration_id']
            return request.user.beneficiaryuserregistration.beneficiary_user_registration_id == beneficiary_user_registration_id
        except (KeyError, AttributeError):
            return False
        

    

