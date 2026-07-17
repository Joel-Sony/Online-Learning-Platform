"""
Update all lesson content in the database to replace Unsplash URLs
with Cloudinary URLs using the mapping file.
"""
import json
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from courses.models import Lesson


class Command(BaseCommand):
    help = "Replace Unsplash URLs in lesson content with Cloudinary URLs"

    def handle(self, *args, **options):
        mapping_path = Path(settings.BASE_DIR) / "cloudinary_mapping.json"
        if not mapping_path.exists():
            mapping_path = Path("/app/cloudinary_mapping.json")
        if not mapping_path.exists():
            self.stdout.write(self.style.ERROR(f"cloudinary_mapping.json not found at {mapping_path}"))
            return

        with open(mapping_path) as f:
            mapping = json.load(f)

        sorted_mapping = sorted(mapping.items(), key=lambda x: -len(x[0]))
        updated = 0
        total = 0

        for lesson in Lesson.objects.all():
            if not lesson.content:
                continue
            total += 1
            new_content = lesson.content
            changed = False
            for old_url, new_url in sorted_mapping:
                if old_url in new_content:
                    new_content = new_content.replace(old_url, new_url)
                    changed = True
            if changed:
                lesson.content = new_content
                lesson.save(update_fields=["content"])
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Updated {updated} of {total} lessons with Cloudinary URLs"
        ))
