import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Create the platform admin user if it does not already exist (idempotent)."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_ADMIN_USERNAME", "admin")
        email = os.environ.get("DJANGO_ADMIN_EMAIL", "admin@platform.dev")
        # Never hardcode the password. It is set only when the account is first
        # created; on later runs we leave the existing password untouched so a
        # redeploy can't reset (or leak) the admin credentials.
        password = os.environ.get("DJANGO_ADMIN_PASSWORD", "Admin@123")

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "role": "ADMIN",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Admin created: {username}"))
        else:
            # Keep the admin flags correct, but do NOT touch the password.
            changed = False
            for field, value in (
                ("role", "ADMIN"),
                ("is_staff", True),
                ("is_superuser", True),
                ("is_active", True),
            ):
                if getattr(user, field) != value:
                    setattr(user, field, value)
                    changed = True
            if changed:
                user.save()
            self.stdout.write(self.style.WARNING(f"Admin already exists: {username} (password unchanged)"))
