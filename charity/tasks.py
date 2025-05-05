# request/tasks.py
from celery import shared_task
from request.models import (CharityAnnouncementForRequest, 
                     BeneficiaryRequest,
                     )
from django.core.exceptions import ObjectDoesNotExist
from beneficiary.models import CharityAnnouncementToBeneficiary

@shared_task(bind=True)
def create_request_announcement(self, request_id):
    """
    Async task to create an announcement for a newly created request
    """
    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        
        # Create the announcement
        announcement = CharityAnnouncementForRequest.objects.create(
            charity_announcement_for_request_title="Created",
            charity_announcement_for_request_description=f"Request #{request_id} was created",
            beneficiary_request=request
        )
        
    except:
        pass
    

@shared_task
def update_request_announcement(request_id):
    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title=f"Update",
            charity_announcement_for_request_description=f"The request #{request_id}' has been updated."
        )
    except BeneficiaryRequest.DoesNotExist:
        pass  # Optionally log or retry

@shared_task
def delete_request_announcement(request_id):
    try:
        CharityAnnouncementToBeneficiary.objects.create(
            charity_announcement_for_request_title=f"delete",
            charity_announcement_for_request_description=f"The request #'{request_id}' has been deleted."
        )
    except:
        pass  # Optionally log or retry

# charity/tasks.py

@shared_task
def create_history_announcement(request_id):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title="History Created",
            charity_announcement_for_request_description=f"For request #{request_id}, a history record was created."
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def create_child_request_announcement(request_id):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title="Child Request Created",
            charity_announcement_for_request_description=f"A child request was added to request #{request_id}."
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def create_history_update_announcement(request_id):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title="History Updated",
            charity_announcement_for_request_description=f"A history record of request #{request_id} was updated."
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def create_history_deletion_announcement(request_id):
    from request.models import CharityAnnouncementForRequest

    CharityAnnouncementForRequest.objects.create(
        beneficiary_request_id=request_id,
        charity_announcement_for_request_title="History Deleted",
        charity_announcement_for_request_description=f"A history record of request #{request_id} was deleted."
    )

@shared_task
def create_child_update_announcement(request_id):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title="Child Request Updated",
            charity_announcement_for_request_description=f"A child request of request #{request_id} was updated."
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def create_child_deletion_announcement(request_id):
    from request.models import CharityAnnouncementForRequest

    CharityAnnouncementForRequest.objects.create(
        beneficiary_request_id=request_id,
        charity_announcement_for_request_title="Child Request Deleted",
        charity_announcement_for_request_description=f"A child request of request #{request_id} was deleted."
    )

@shared_task
def create_recurring_update_announcement(request_id):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title="Recurring Info Updated",
            charity_announcement_for_request_description=f"The recurring info of request #{request_id} was updated."
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def create_recurring_deletion_announcement(request_id):
    from request.models import CharityAnnouncementForRequest

    CharityAnnouncementForRequest.objects.create(
        beneficiary_request_id=request_id,
        charity_announcement_for_request_title="Recurring Info Deleted",
        charity_announcement_for_request_description=f"The recurring info of request #{request_id} was deleted."
    )

@shared_task
def create_onetime_update_announcement(request_id):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title="One-Time Info Updated",
            charity_announcement_for_request_description=f"The one-time info of request #{request_id} was updated."
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def create_onetime_deletion_announcement(request_id):
    from request.models import CharityAnnouncementForRequest

    CharityAnnouncementForRequest.objects.create(
        beneficiary_request_id=request_id,
        charity_announcement_for_request_title="One-Time Info Deleted",
        charity_announcement_for_request_description=f"The one-time info of request #{request_id} was deleted."
    )

@shared_task
def create_stage_change_announcement(request_id, new_stage_name):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        readable_stage = new_stage_name.replace("_", " ").title()
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title=f"Request Moved to {readable_stage}",
            charity_announcement_for_request_description=f"Request #{request_id} has been moved to '{readable_stage}' stage."
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def create_child_stage_change_announcement(request_id, new_stage_name):
    from request.models import CharityAnnouncementForRequest

    readable_stage = new_stage_name.replace("_", " ").title()
    CharityAnnouncementForRequest.objects.create(
        beneficiary_request_id=request_id,
        charity_announcement_for_request_title=f"Child Request Moved to {readable_stage}",
        charity_announcement_for_request_description=f"A child request for request #{request_id} has moved to '{readable_stage}' stage."
    )

