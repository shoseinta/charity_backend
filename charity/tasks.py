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
            charity_announcement_for_request_title="درخواست ایجاد شد",
            charity_announcement_for_request_description=f".توسط خیریه برای شما ایجاد شد {request_id} درخواست به شماره",
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
            charity_announcement_for_request_title=f"درخواست بروزرسانی شد",
            charity_announcement_for_request_description=f"توسط خیریه بروزرسانی شد {request_id} درخواست شما به شماره"
        )
    except BeneficiaryRequest.DoesNotExist:
        pass  # Optionally log or retry

@shared_task
def delete_request_announcement(request_id):
    try:
        CharityAnnouncementToBeneficiary.objects.create(
            charity_announcement_for_request_title=f"حذف درخواست",
            charity_announcement_for_request_description=f"توسط خیریه حذف گردید {request_id} درخواست شما به شماره"
        )
    except:
        pass  # Optionally log or retry

# charity/tasks.py

# @shared_task
# def create_history_announcement(request_id):
#     from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

#     try:
#         request = BeneficiaryRequest.objects.get(pk=request_id)
#         CharityAnnouncementForRequest.objects.create(
#             beneficiary_request=request,
#             charity_announcement_for_request_title="History Created",
#             charity_announcement_for_request_description=f"For request #{request_id}, a history record was created."
#         )
#     except BeneficiaryRequest.DoesNotExist:
#         pass

@shared_task
def create_child_request_announcement(request_id):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title="ایجاد درخواست جزیی",
            charity_announcement_for_request_description=f"توسط حیریه یک درخواست جزیی ایجاد گردید {request_id} برای درخواست شما به شماره"
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

# @shared_task
# def create_history_update_announcement(request_id):
#     from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

#     try:
#         request = BeneficiaryRequest.objects.get(pk=request_id)
#         CharityAnnouncementForRequest.objects.create(
#             beneficiary_request=request,
#             charity_announcement_for_request_title="History Updated",
#             charity_announcement_for_request_description=f"A history record of request #{request_id} was updated."
#         )
#     except BeneficiaryRequest.DoesNotExist:
#         pass

# @shared_task
# def create_history_deletion_announcement(request_id):
#     from request.models import CharityAnnouncementForRequest

#     CharityAnnouncementForRequest.objects.create(
#         beneficiary_request_id=request_id,
#         charity_announcement_for_request_title="History Deleted",
#         charity_announcement_for_request_description=f"A history record of request #{request_id} was deleted."
#     )

@shared_task
def create_child_update_announcement(request_id):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title="بروزرسانی درخواست جزیی",
            charity_announcement_for_request_description=f"توسط خیریه بروزرسانی شد {request_id} درخواست جزیی مربوط به درخواست شما به شماره"
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def create_child_deletion_announcement(request_id):
    from request.models import CharityAnnouncementForRequest

    CharityAnnouncementForRequest.objects.create(
        beneficiary_request_id=request_id,
        charity_announcement_for_request_title="حذف درخواست جزیی",
        charity_announcement_for_request_description=f"توسط خیریه حذف گردید {request_id} درخواست جریی مربوط به درخواست شما به شماره"
    )

@shared_task
def create_recurring_update_announcement(request_id):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title="بروزرسانی بازه دریافت کمک",
            charity_announcement_for_request_description=f"توسط خیریه بروزرسانی شد {request_id} بازه زمانی دریافت کمک مربوط به درخواست شما به شماره"
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def create_recurring_deletion_announcement(request_id):
    from request.models import CharityAnnouncementForRequest

    CharityAnnouncementForRequest.objects.create(
        beneficiary_request_id=request_id,
        charity_announcement_for_request_title="حذف بازه زمانی دریافت کمک",
        charity_announcement_for_request_description=f"توسط خیریه حذف گردید {request_id} بازه زمانی دریافت کمک مربوط به درخواست شما به شماره"
    )

@shared_task
def create_onetime_update_announcement(request_id):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title="بروزرسانی بازه دریافت کمک",
            charity_announcement_for_request_description=f"توسط خیریه بروزرسانی شد {request_id} بازه زمانی دریافت کمک مربوط به درخواست شما به شماره"
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def create_onetime_deletion_announcement(request_id):
    from request.models import CharityAnnouncementForRequest

    CharityAnnouncementForRequest.objects.create(
        beneficiary_request_id=request_id,
        charity_announcement_for_request_title="حذف بازه زمانی دریافت کمک",
        charity_announcement_for_request_description=f"توسط خیریه حذف گردید {request_id} بازه زمانی دریافت کمک مربوط به درخواست شما به شماره"
    )

@shared_task
def create_stage_change_announcement(request_id, new_stage_name):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        readable_stage = new_stage_name.replace("_", " ").title()
        if readable_stage == 'Submitted':
            readable_stage = 'ارسال شده'
        elif readable_stage == 'Pending Review':
            readable_stage = 'در انتظار بررسی'
        elif readable_stage == 'Under Evaluation':
            readable_stage = 'در حال ارزیابی'
        elif readable_stage == 'Approved':
            readable_stage = 'تایید شده'
        elif readable_stage == 'Rejected':
            readable_stage = 'رد شده'
        elif readable_stage == 'In Progress':
            readable_stage = 'در حال انجام'
        elif readable_stage == 'Completed':
            readable_stage = 'تکمیل شده'
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title=f"بروز رسانی وضعیت درخواست",
            charity_announcement_for_request_description=f"تغییر پیدا کرد «{readable_stage}» توسط خیریه به {request_id} وضعیت درخواست شما به شماره"
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def create_child_stage_change_announcement(request_id, new_stage_name):
    from request.models import CharityAnnouncementForRequest

    readable_stage = new_stage_name.replace("_", " ").title()
    if readable_stage == 'Submitted':
        readable_stage = 'ارسال شده'
    elif readable_stage == 'Pending Review':
        readable_stage = 'در انتظار بررسی'
    elif readable_stage == 'Under Evaluation':
        readable_stage = 'در حال ارزیابی'
    elif readable_stage == 'Approved':
        readable_stage = 'تایید شده'
    elif readable_stage == 'Rejected':
        readable_stage = 'رد شده'
    elif readable_stage == 'In Progress':
        readable_stage = 'در حال انجام'
    elif readable_stage == 'Completed':
        readable_stage = 'تکمیل شده'
    CharityAnnouncementForRequest.objects.create(
        beneficiary_request_id=request_id,
        charity_announcement_for_request_title=f"بروزرسانی وضعیت درخواست جزیی",
        charity_announcement_for_request_description=f"تغییر پیدا کرد «{readable_stage}» توسط خیریه به {request_id} وضعیت درخواست جزیی مربوط به درخواست شما به شماره"
        )

