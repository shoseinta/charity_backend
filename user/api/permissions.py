from rest_framework.permissions import BasePermission
from charity.models import Charity
from beneficiary.models import BeneficiaryUserRegistration
class IsAdminOrCharity(BasePermission):
    def has_permission(self, request, view):
        return Charity.objects.filter(charity_username=request.user).exists() or request.user.is_staff
    
class IsCertainBeneficiary(BasePermission):
    def has_permission(self, request, view):
        # Allow staff and charity users
        if request.user.is_staff or Charity.objects.filter(charity_username=request.user).exists():
            return True
            
        try:
            # Try to get the ID from URL kwargs
            beneficiary_id = view.kwargs.get('beneficiary_user_registration_id') or view.kwargs.get('pk')
            
            if not beneficiary_id:
                return False
                
            # Get the BeneficiaryUserRegistration object
            beneficiary = BeneficiaryUserRegistration.objects.get(pk=beneficiary_id)
            
            # Compare the related user with request.user
            return request.user == beneficiary.benficiary_user_id
            
        except (KeyError, AttributeError, BeneficiaryUserRegistration.DoesNotExist):
            return False
        

    

