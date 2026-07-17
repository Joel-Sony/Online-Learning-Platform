"""
Fix remaining 13 lessons that have a broken Unsplash URL (photo no longer exists).
Replace with a working Cloudinary photo.
"""
from django.core.management.base import BaseCommand
from courses.models import Lesson

OLD_URL = "https://images.unsplash.com/photo-1515879218367-8466d910y1984?w=800&q=80"
NEW_URL = "https://res.cloudinary.com/dvex86jfq/image/upload/v1784263822/unsplash/1519389950473-47ba0277781c.jpg"


class Command(BaseCommand):
    help = "Fix lessons with broken Unsplash URLs"

    def handle(self, *args, **options):
        qs = Lesson.objects.filter(content__contains=OLD_URL)
        count = qs.count()
        for lesson in qs:
            lesson.content = lesson.content.replace(OLD_URL, NEW_URL)
            lesson.save(update_fields=["content"])
        self.stdout.write(self.style.SUCCESS(f"Fixed {count} lessons"))
