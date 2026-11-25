from django.core.management.base import BaseCommand

from surveys.models import delete_expired_surveys


class Command(BaseCommand):
    help = "Hapus survei yang sudah berumur tujuh hari."

    def handle(self, *args, **options):
        deleted_count = delete_expired_surveys()
        self.stdout.write(f"{deleted_count} survei kedaluwarsa dihapus.")
