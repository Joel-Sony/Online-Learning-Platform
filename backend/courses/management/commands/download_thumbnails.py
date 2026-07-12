import urllib.request
import uuid
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from courses.models import Course

THUMBNAIL_URLS = {
    "Complete Python Bootcamp: From Zero to Hero": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80",
    "Full-Stack Web Development with React & Django": "https://images.unsplash.com/photo-1555099962-4199c345e5dd?w=800&q=80",
    "UI/UX Design Masterclass: Design Thinking to Prototype": "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=800&q=80",
    "Machine Learning & AI: From Fundamentals to Deployment": "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=800&q=80",
    "Business Strategy & Entrepreneurship": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&q=80",
    "Photography Masterclass: The Complete Guide": "https://images.unsplash.com/photo-1452587925148-ce544e77e70d?w=800&q=80",
    "Data Science with Python: Pandas, NumPy & Visualization": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80",
    "Digital Marketing: SEO, Ads & Social Media Strategy": "https://images.unsplash.com/photo-1533750349088-cd871a92f312?w=800&q=80",
    "Advanced React: Patterns, Performance & Architecture": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&q=80",
    "Brand Identity Design: From Concept to Style Guide": "https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=800&q=80",
    "Venture Capital & Startup Finance": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
    "Landscape & Nature Photography": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80",
}


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

            if course.thumbnail and course.thumbnail.storage.exists(course.thumbnail.name):
                self.stdout.write(f"  ✓ {course.title} — thumbnail exists")
                skipped += 1
                continue

            ext = ".jpg"
            fname = f"course_{uuid.uuid4().hex[:8]}{ext}"
            image_data = download_image(source_url, fname)
            if image_data:
                course.thumbnail.save(fname, image_data, save=True)
                self.stdout.write(f"  ✓ {course.title} — downloaded")
                downloaded += 1
            else:
                self.stdout.write(f"  ✗ {course.title} — download failed")
                failed += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone — downloaded: {downloaded}, skipped: {skipped}, failed: {failed}"
        ))
