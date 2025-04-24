from django.core.management.base import BaseCommand
from meilisearch import Client
from django.conf import settings
from beneficiary.models import BeneficiaryUserRegistration
import time


class Command(BaseCommand):
    help = "Sync beneficiaries to MeiliSearch"

    def handle(self, *args, **kwargs):
        client = Client(settings.MEILISEARCH_URL, settings.MEILISEARCH_MASTER_KEY)

        # Step 1: Reset the index to prevent primary key conflict
        try:
            client.index("beneficiaries").delete()
            self.stdout.write(self.style.WARNING("⚠️ Deleted existing 'beneficiaries' index due to primary key conflict."))
        except Exception as e:
            self.stdout.write(self.style.NOTICE("ℹ️ No existing index to delete."))

        # Step 2: Create index with explicit primary key
        client.create_index("beneficiaries", {"primaryKey": "id"})
        index = client.index("beneficiaries")

        # Step 3: Prepare data
        beneficiaries = BeneficiaryUserRegistration.objects.select_related(
            "beneficiary_user_information",
            "beneficiary_user_address__province",
            "beneficiary_user_address__city"
        ).prefetch_related("beneficiary_user_additional_info")

        data = []
        for reg in beneficiaries:
            info = getattr(reg, "beneficiary_user_information", None)
            address = getattr(reg, "beneficiary_user_address", None)
            province = address.province.province_name if address and address.province else ""
            city = address.city.city_name if address and address.city else ""
            tags = [i.beneficiary_user_additional_info_title for i in reg.beneficiary_user_additional_info.all()]
            full_name = " ".join(filter(None, [info.first_name if info else "", info.last_name if info else ""])).strip()

            data.append({
                "id": reg.pk,
                "full_name": full_name,
                "first_name": info.first_name if info else "",
                "last_name": info.last_name if info else "",
                "identification_number": reg.identification_number,
                "beneficiary_id": reg.beneficiary_id,
                "phone_number": reg.phone_number,
                "email": reg.email,
                "province": province,
                "city": city,
                "tags": tags,
            })

        if not data:
            self.stdout.write(self.style.WARNING("⚠️ No beneficiaries found to sync."))
            return

        # Step 4: Add documents
        response = index.add_documents(data)
        task_id = response.task_uid

        self.stdout.write(f"🔄 Documents sent. Task UID: {task_id}")

        # Step 5: Wait for indexing to complete
        while True:
            task = client.get_task(task_id)
            if task.status in ["succeeded", "failed"]:
                break
            time.sleep(0.3)

        if task.status == "succeeded":
            self.stdout.write(self.style.SUCCESS(f"✅ Successfully synced {len(data)} beneficiaries to MeiliSearch."))
        else:
            error = task.error
            self.stdout.write(self.style.ERROR(f"❌ Failed to sync. Error: {error}"))
