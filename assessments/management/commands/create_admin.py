from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = "Create the Render admin user"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("ADMIN_USERNAME")
        password = os.environ.get("ADMIN_PASSWORD")

        if not username or not password:
            self.stdout.write("ADMIN_USERNAME or ADMIN_PASSWORD not set.")
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"User {username} already exists.")
            return

        User.objects.create_superuser(
            username=username,
            password=password,
        )

        self.stdout.write(f"Created superuser {username}.")
