import urllib.request
import uuid
import re
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from courses.models import Course
from courses.thumbnail_defaults import THUMBNAIL_URLS

UNSPLASH_FALLBACKS = {
    "development": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=800&auto=format&fit=crop",
    "coding": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=800&auto=format&fit=crop",
    "python": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=800&auto=format&fit=crop",
    "react": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?q=80&w=800&auto=format&fit=crop",
    "django": "https://images.unsplash.com/photo-1555099962-4199c345e5dd?q=80&w=800&auto=format&fit=crop",
    "design": "https://images.unsplash.com/photo-1561070791-2526d30994b5?q=80&w=800&auto=format&fit=crop",
    "ux": "https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e?q=80&w=800&auto=format&fit=crop",
    "business": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?q=80&w=800&auto=format&fit=crop",
    "strategy": "https://images.unsplash.com/photo-1552664730-d307ca884978?q=80&w=800&auto=format&fit=crop",
    "finance": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=800&auto=format&fit=crop",
    "marketing": "https://images.unsplash.com/photo-1533750349088-cd871a92f312?q=80&w=800&auto=format&fit=crop",
    "seo": "https://images.unsplash.com/photo-1571721795195-a2ca2d3370a9?q=80&w=800&auto=format&fit=crop",
    "photography": "https://images.unsplash.com/photo-1452587925148-ce544e77e70d?q=80&w=800&auto=format&fit=crop",
    "camera": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?q=80&w=800&auto=format&fit=crop",
    "data": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=800&auto=format&fit=crop",
    "machine": "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?q=80&w=800&auto=format&fit=crop",
    "default": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=800&auto=format&fit=crop"
}

def download_image(url, filename):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            return ContentFile(response.read(), name=filename)
    except Exception as e:
        print(f"    ✗ Download failed from {url}: {e}")
        return None

class Command(BaseCommand):
    help = "Attach Unsplash photos to all courses thumbnails except Egyptian History and Cooking courses"

    def handle(self, *args, **options):
        courses = Course.objects.all()
        updated = 0
        skipped = 0
        failed = 0

        for course in courses:
            title_lower = course.title.lower()
            
            # Check if it should be skipped (Egyptian History or Cooking)
            if "egyptian history" in title_lower or "cooking" in title_lower:
                self.stdout.write(self.style.WARNING(f"  ⚠ Skipping excluded course: {course.title}"))
                skipped += 1
                continue

            # Determine Unsplash URL
            source_url = THUMBNAIL_URLS.get(course.title)
            unsplash_url = None

            if source_url:
                # Try to extract the unsplash photo ID from Cloudinary URL if mapped
                match = re.search(r'unsplash/([^./]+)', source_url)
                if match:
                    photo_id = match.group(1)
                    unsplash_url = f"https://images.unsplash.com/photo-{photo_id}?q=80&w=800&auto=format&fit=crop"
                else:
                    unsplash_url = source_url
            
            if not unsplash_url:
                # If not mapped, check keywords in title or category
                category_lower = course.category.lower()
                matched_key = None
                
                # Check keywords in title
                for key in UNSPLASH_FALLBACKS.keys():
                    if key != "default" and key in title_lower:
                        matched_key = key
                        break
                
                # Check keywords in category if title didn't match
                if not matched_key:
                    for key in UNSPLASH_FALLBACKS.keys():
                        if key != "default" and key in category_lower:
                            matched_key = key
                            break
                
                if matched_key:
                    unsplash_url = UNSPLASH_FALLBACKS[matched_key]
                    self.stdout.write(f"  → Found keyword match '{matched_key}' for '{course.title}'")
                else:
                    unsplash_url = UNSPLASH_FALLBACKS["default"]
                    self.stdout.write(f"  → Using default fallback for '{course.title}'")

            self.stdout.write(f"  → Attaching Unsplash photo to: {course.title}")
            ext = ".jpg"
            fname = f"course_{uuid.uuid4().hex[:8]}{ext}"
            
            image_data = download_image(unsplash_url, fname)
            if image_data:
                # Save via the model field — CloudinaryStorage intercepts this
                # and uploads the file to Cloudinary automatically.
                course.thumbnail.save(fname, image_data, save=True)
                self.stdout.write(self.style.SUCCESS(f"    ✓ Successfully attached and uploaded to Cloudinary: {course.thumbnail.url}"))
                updated += 1
            else:
                self.stdout.write(self.style.ERROR(f"    ✗ Failed to attach thumbnail for: {course.title}"))
                failed += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone — updated: {updated}, skipped: {skipped}, failed: {failed}"
        ))
