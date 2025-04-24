from django.core.management.base import BaseCommand
from meilisearch import Client
from django.conf import settings
from request.models import BeneficiaryRequest
from django.db.models import Prefetch
import time

class Command(BaseCommand):
    help = "Sync all beneficiary requests to MeiliSearch"

    def handle(self, *args, **kwargs):
        client = Client(settings.MEILISEARCH_URL, settings.MEILISEARCH_MASTER_KEY)

        try:
            client.index("requests").delete()
        except Exception:
            pass  # if index doesn't exist, skip

        client.create_index("requests", {"primaryKey": "id"})
        index = client.index("requests")

        queryset = BeneficiaryRequest.objects.select_related(
            "beneficiary_user_registration__beneficiary_user_information",
            "beneficiary_user_registration__beneficiary_user_address__province",
            "beneficiary_user_registration__beneficiary_user_address__city",
            "beneficiary_request_type_layer1",
            "beneficiary_request_type_layer2"
        )

        documents = []
        for req in queryset:
            reg = req.beneficiary_user_registration
            info = getattr(reg, "beneficiary_user_information", None)
            address = getattr(reg, "beneficiary_user_address", None)
            province = address.province.province_name if address and address.province else ""
            city = address.city.city_name if address and address.city else ""
            full_name = " ".join(filter(None, [info.first_name if info else "", info.last_name if info else ""])).strip()

            documents.append({
                "id": req.pk,
                "beneficiary_request_type_layer1_name": req.beneficiary_request_type_layer1.beneficiary_request_type_layer1_name,
                "beneficiary_request_type_layer2_name": req.beneficiary_request_type_layer2.beneficiary_request_type_layer2_name,
                "beneficiary_request_title": req.beneficiary_request_title,
                "beneficiary_request_description": req.beneficiary_request_description,
                "full_name": full_name,
                "beneficiary_id": reg.beneficiary_id,
                "identification_number": reg.identification_number,
                "phone_number": reg.phone_number,
                "email": reg.email,
                "province_name": province,
                "city_name": city,
            })

        response = index.add_documents(documents)
        task_id = response.task_uid

        while True:
            task = client.get_task(task_id)
            if task.status in ["succeeded", "failed"]:
                break
            time.sleep(0.2)

        if task.status == "succeeded":
            self.stdout.write(self.style.SUCCESS(f"✅ Successfully synced {len(documents)} requests to MeiliSearch."))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Sync failed: {task.error.message}"))
