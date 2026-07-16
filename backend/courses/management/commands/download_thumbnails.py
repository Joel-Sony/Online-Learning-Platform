import urllib.request
import uuid
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from courses.models import Course
from courses.thumbnail_defaults import THUMBNAIL_URLS


def download_image(url, filename):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            return ContentFile(response.read(), name=filename)
    except Exception:
        return None


class Command(BaseCommand):
    help = "Download thumbnail images for courses that are missing their files."

    def handle(self, *args, **options):
        courses = Course.objects.all()
        downloaded = 0
        skipped = 0
        failed = 0

        for course in courses:
            source_url = THUMBNAIL_URLS.get(course.title)
            if not source_url:
                self.stdout.write(f"  ⚠ No URL mapping for: {course.title}")
                skipped += 1
                continue

            # A truthy FieldFile means a file path/public_id is stored —
            # the image already exists on Cloudinary. No network call needed.
            if course.thumbnail:
                self.stdout.write(f"  ✓ {course.title} — thumbnail exists")
                skipped += 1
                continue

            ext = ".jpg"
            fname = f"course_{uuid.uuid4().hex[:8]}{ext}"
            image_data = download_image(source_url, fname)
            if image_data:
                # Save via the model field — CloudinaryStorage intercepts this
                # and uploads the file to Cloudinary automatically.
                course.thumbnail.save(fname, image_data, save=True)
                self.stdout.write(f"  ✓ {course.title} — uploaded to Cloudinary")
                downloaded += 1
            else:
                self.stdout.write(f"  ✗ {course.title} — download failed")
                failed += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone — downloaded: {downloaded}, skipped: {skipped}, failed: {failed}"
        ))
