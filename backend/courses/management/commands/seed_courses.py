"""
seed_courses.py

Management command to:
1. Delete all existing courses, enrollments, progress, modules, lessons
2. Create 5 instructor accounts (MENTOR role)
3. Create 1 student account
4. Create 12 rich courses across various categories with Unsplash thumbnail URLs
5. Publish all courses
6. Enroll the student in a selection of courses
"""

import urllib.request
import os
import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


INSTRUCTORS = [
    {
        "username": "alex_morgan",
        "email": "alex.morgan@platform.dev",
        "password": "Instructor@123",
        "first_name": "Alex",
        "last_name": "Morgan",
        "bio": "Senior Software Engineer at Google with 12 years of experience in distributed systems and cloud architecture.",
    },
    {
        "username": "priya_sharma",
        "email": "priya.sharma@platform.dev",
        "password": "Instructor@123",
        "first_name": "Priya",
        "last_name": "Sharma",
        "bio": "UX/Product Design Lead. Former Airbnb designer. Passionate about human-centered design and accessibility.",
    },
    {
        "username": "carlos_vega",
        "email": "carlos.vega@platform.dev",
        "password": "Instructor@123",
        "first_name": "Carlos",
        "last_name": "Vega",
        "bio": "Entrepreneur and MBA Professor. Founded 3 startups. Expert in business strategy and venture capital.",
    },
    {
        "username": "yuki_tanaka",
        "email": "yuki.tanaka@platform.dev",
        "password": "Instructor@123",
        "first_name": "Yuki",
        "last_name": "Tanaka",
        "bio": "Data Scientist and AI Researcher. PhD from MIT. 8 years working on machine learning at scale.",
    },
    {
        "username": "sofia_bell",
        "email": "sofia.bell@platform.dev",
        "password": "Instructor@123",
        "first_name": "Sofia",
        "last_name": "Bell",
        "bio": "Creative Director and award-winning photographer. Has worked with National Geographic and major fashion brands.",
    },
]

STUDENT = {
    "username": "demo_student",
    "email": "student@platform.dev",
    "password": "Student@123",
    "first_name": "Jamie",
    "last_name": "Lee",
}

# Each course has: title, description, category, level, price, is_free, tags, instructor_username, thumbnail_url, modules
COURSES = [
    {
        "title": "Complete Python Bootcamp: From Zero to Hero",
        "description": "Master Python programming from absolute basics to advanced concepts. Build real projects, learn web scraping, automation, data analysis, and more. Perfect for beginners and professionals looking to add Python to their skill set.",
        "category": "Development",
        "level": "BEGINNER",
        "price": Decimal("49.00"),
        "is_free": False,
        "language": "English",
        "tags": "python, programming, beginner, web-scraping",
        "instructor": "alex_morgan",
        "thumbnail_url": "https://res.cloudinary.com/dvex86jfq/image/upload/v1784264615/unsplash/1526374965328-7f61d4dc18c5.jpg",
        "modules": [
            {"title": "Python Fundamentals", "lessons": [
                {"title": "Introduction to Python", "video_url": "https://www.youtube.com/watch?v=K5KVEU3aaeQ"},
                "Variables and Data Types", "Control Flow", "Functions & Scope"
            ]},
            {"title": "Object-Oriented Programming", "lessons": ["Classes and Objects", "Inheritance", "Polymorphism", "Decorators"]},
            {"title": "Real-World Projects", "lessons": ["Web Scraper", "CLI Tool", "File Automation", "API Integration"]},
        ],
    },
    {
        "title": "Full-Stack Web Development with React & Django",
        "description": "Build production-ready web applications from scratch. Learn React for the frontend and Django REST Framework for the backend. Includes JWT auth, Stripe payments, deployment to AWS, and Docker containerization.",
        "category": "Development",
        "level": "INTERMEDIATE",
        "price": Decimal("79.00"),
        "is_free": False,
        "language": "English",
        "tags": "react, django, full-stack, javascript",
        "instructor": "alex_morgan",
        "thumbnail_url": "https://res.cloudinary.com/dvex86jfq/image/upload/v1784265111/unsplash/1555099962-4199c345e5dd.jpg",
        "modules": [
            {"title": "React Fundamentals", "lessons": [
                {"title": "Component Architecture", "video_url": "https://www.youtube.com/watch?v=c-QsfbznSXI"},
                "State & Props", "Hooks Deep Dive", "Context API"
            ]},
            {"title": "Django REST Framework", "lessons": ["Models & Serializers", "API Views", "Authentication", "Permissions"]},
            {"title": "Integration & Deployment", "lessons": ["Connecting Frontend & Backend", "Docker Setup", "AWS Deployment", "CI/CD Pipeline"]},
        ],
    },
    {
        "title": "UI/UX Design Masterclass: Design Thinking to Prototype",
        "description": "Learn to design stunning, user-friendly interfaces using Figma. Covers design thinking methodology, wireframing, prototyping, usability testing, and a complete case study building a real mobile app design from scratch.",
        "category": "Design",
        "level": "BEGINNER",
        "price": Decimal("0.00"),
        "is_free": True,
        "language": "English",
        "tags": "ux, ui, figma, design-thinking",
        "instructor": "priya_sharma",
        "thumbnail_url": "https://res.cloudinary.com/dvex86jfq/image/upload/v1784265112/unsplash/1561070791-2526d30994b5.jpg",
        "modules": [
            {"title": "Design Thinking", "lessons": [
                {"title": "Empathize Phase", "video_url": "https://www.youtube.com/watch?v=c9Wg6Cb_YlU"},
                "Define & Ideate", "Prototyping Basics", "Usability Testing"
            ]},
            {"title": "Figma Mastery", "lessons": ["Figma Interface Tour", "Auto Layout", "Components & Variants", "Interactive Prototypes"]},
        ],
    },
    {
        "title": "Machine Learning & AI: From Fundamentals to Deployment",
        "description": "A comprehensive guide to machine learning using Python, scikit-learn, TensorFlow, and PyTorch. Learn supervised and unsupervised learning, neural networks, NLP, and how to deploy ML models to production with FastAPI.",
        "category": "Development",
        "level": "ADVANCED",
        "price": Decimal("99.00"),
        "is_free": False,
        "language": "English",
        "tags": "machine-learning, AI, tensorflow, deep-learning",
        "instructor": "yuki_tanaka",
        "thumbnail_url": "https://res.cloudinary.com/dvex86jfq/image/upload/v1784265111/unsplash/1677442135703-1787eea5ce01.jpg",
        "modules": [
            {"title": "ML Foundations", "lessons": [
                {"title": "Linear Regression", "video_url": "https://www.youtube.com/watch?v=i_LwzRVP7bg"},
                "Classification Algorithms", "Model Evaluation", "Feature Engineering"
            ]},
            {"title": "Deep Learning", "lessons": ["Neural Network Basics", "CNNs for Vision", "RNNs & LSTMs", "Transfer Learning"]},
            {"title": "NLP & Deployment", "lessons": ["Text Processing", "Transformers & BERT", "FastAPI Serving", "Docker + AWS SageMaker"]},
        ],
    },
    {
        "title": "Business Strategy & Entrepreneurship",
        "description": "Learn how successful companies are built from the ground up. Covers market analysis, business model canvas, fundraising, product-market fit, scaling operations, and leadership. Taught by a serial entrepreneur with 3 exits.",
        "category": "Business",
        "level": "INTERMEDIATE",
        "price": Decimal("59.00"),
        "is_free": False,
        "language": "English",
        "tags": "business, entrepreneurship, strategy, startup",
        "instructor": "carlos_vega",
        "thumbnail_url": "https://res.cloudinary.com/dvex86jfq/image/upload/v1784265112/unsplash/1552664730-d307ca884978.jpg",
        "modules": [
            {"title": "Foundations of Strategy", "lessons": [
                {"title": "Porter's 5 Forces", "video_url": "https://www.youtube.com/watch?v=fXQrCn4lW7E"},
                "SWOT Analysis", "Business Model Canvas", "Value Proposition Design"
            ]},
            {"title": "Building & Scaling", "lessons": ["Finding Product-Market Fit", "Fundraising 101", "Team Building", "Growth Hacking"]},
        ],
    },
    {
        "title": "Photography Masterclass: The Complete Guide",
        "description": "From camera basics to professional techniques — learn composition, lighting, portrait, landscape, and street photography. Includes photo editing in Adobe Lightroom and a step-by-step guide to building your photography portfolio.",
        "category": "Photography",
        "level": "BEGINNER",
        "price": Decimal("44.00"),
        "is_free": False,
        "language": "English",
        "tags": "photography, lightroom, portrait, composition",
        "instructor": "sofia_bell",
        "thumbnail_url": "https://res.cloudinary.com/dvex86jfq/image/upload/v1784263470/unsplash/1452587925148-ce544e77e70d.jpg",
        "modules": [
            {"title": "Camera Fundamentals", "lessons": [
                {"title": "Understanding Exposure", "video_url": "https://www.youtube.com/watch?v=yhAmMUi2NmM"},
                "Aperture & Depth of Field", "Shutter Speed & Motion", "ISO & Noise"
            ]},
            {"title": "Composition & Lighting", "lessons": ["Rule of Thirds", "Golden Hour", "Studio Lighting Setup", "Natural Light Portraits"]},
            {"title": "Post-Processing", "lessons": ["Lightroom Workflow", "Color Grading", "Skin Retouching", "Exporting for Web & Print"]},
        ],
    },
    {
        "title": "Data Science with Python: Pandas, NumPy & Visualization",
        "description": "Master the complete data science workflow: data collection, cleaning, exploration, visualization, and storytelling. Includes end-to-end projects analyzing real datasets from Kaggle, using Pandas, NumPy, Matplotlib, Seaborn, and Plotly.",
        "category": "Development",
        "level": "INTERMEDIATE",
        "price": Decimal("64.00"),
        "is_free": False,
        "language": "English",
        "tags": "data-science, pandas, python, visualization",
        "instructor": "yuki_tanaka",
        "thumbnail_url": "https://res.cloudinary.com/dvex86jfq/image/upload/v1784265143/unsplash/1551288049-bebda4e38f71.jpg",
        "modules": [
            {"title": "Data Manipulation", "lessons": [
                {"title": "Pandas DataFrames", "video_url": "https://www.youtube.com/watch?v=7eh4d6sabA0"},
                "Data Cleaning Techniques", "Merging & Grouping", "Time Series Analysis"
            ]},
            {"title": "Visualization", "lessons": ["Matplotlib Basics", "Seaborn Statistical Plots", "Interactive Plotly Charts", "Dashboard with Streamlit"]},
        ],
    },
    {
        "title": "Digital Marketing: SEO, Ads & Social Media Strategy",
        "description": "Learn modern digital marketing from scratch. Build a complete digital marketing strategy covering SEO, Google Ads, Meta Ads, email marketing, content strategy, and analytics. Includes hands-on campaigns and real budget management.",
        "category": "Marketing",
        "level": "BEGINNER",
        "price": Decimal("39.00"),
        "is_free": False,
        "language": "English",
        "tags": "marketing, seo, google-ads, social-media",
        "instructor": "carlos_vega",
        "thumbnail_url": "https://res.cloudinary.com/dvex86jfq/image/upload/v1784265144/unsplash/1533750349088-cd871a92f312.jpg",
        "modules": [
            {"title": "SEO Fundamentals", "lessons": [
                {"title": "Keyword Research", "video_url": "https://www.youtube.com/watch?v=h95cQkEWBx0"},
                "On-Page SEO", "Link Building", "Technical SEO Audit"
            ]},
            {"title": "Paid Advertising", "lessons": ["Google Ads Setup", "Meta Ads Manager", "Retargeting Campaigns", "ROI & Attribution"]},
            {"title": "Content & Email", "lessons": ["Content Calendar Strategy", "Copywriting for Conversions", "Email Sequences", "Analytics with GA4"]},
        ],
    },
    {
        "title": "Advanced React: Patterns, Performance & Architecture",
        "description": "Take your React skills to the next level. Deep dive into advanced patterns (compound components, render props, HOC), performance optimization with memoization, code splitting, React Query, Zustand, and architecting large-scale applications.",
        "category": "Development",
        "level": "ADVANCED",
        "price": Decimal("74.00"),
        "is_free": False,
        "language": "English",
        "tags": "react, advanced, performance, architecture",
        "instructor": "alex_morgan",
        "thumbnail_url": "https://res.cloudinary.com/dvex86jfq/image/upload/v1784265144/unsplash/1633356122544-f134324a6cee.jpg",
        "modules": [
            {"title": "Advanced Patterns", "lessons": [
                {"title": "Compound Components", "video_url": "https://www.youtube.com/watch?v=9Vuz4BbPkXc"},
                "Render Props", "Custom Hooks", "Higher-Order Components"
            ]},
            {"title": "Performance", "lessons": ["React.memo & useMemo", "Code Splitting", "Virtualization", "Bundle Analysis"]},
            {"title": "State Management", "lessons": ["Context at Scale", "Zustand", "React Query", "Optimistic Updates"]},
        ],
    },
    {
        "title": "Brand Identity Design: From Concept to Style Guide",
        "description": "Create powerful brand identities from scratch. Learn logo design principles, typography pairing, color psychology, building comprehensive style guides, and presenting work to clients. Includes a complete branding project walkthrough.",
        "category": "Design",
        "level": "INTERMEDIATE",
        "price": Decimal("54.00"),
        "is_free": False,
        "language": "English",
        "tags": "branding, logo-design, typography, identity",
        "instructor": "priya_sharma",
        "thumbnail_url": "https://res.cloudinary.com/dvex86jfq/image/upload/v1784263889/unsplash/1524758631624-e2822e304c36.jpg",
        "modules": [
            {"title": "Brand Strategy", "lessons": [
                {"title": "Brand Discovery Workshop", "video_url": "https://www.youtube.com/watch?v=y_2P5o_msuo"},
                "Competitive Analysis", "Positioning & Differentiation", "Moodboarding"
            ]},
            {"title": "Visual Identity", "lessons": ["Logo Design Process", "Typography System", "Color Palette", "Photography Style"]},
            {"title": "Style Guide Creation", "lessons": ["Brand Guidelines Structure", "Component Library", "Client Presentation", "Brand Rollout"]},
        ],
    },
    {
        "title": "Venture Capital & Startup Finance",
        "description": "Understand the financial machinery behind startups. Learn how VCs evaluate deals, model financials, structure term sheets, negotiate valuations, and exit strategies. Includes real case studies from Y Combinator, Sequoia, and a16z portfolio companies.",
        "category": "Business",
        "level": "ADVANCED",
        "price": Decimal("89.00"),
        "is_free": False,
        "language": "English",
        "tags": "venture-capital, finance, startups, investment",
        "instructor": "carlos_vega",
        "thumbnail_url": "https://res.cloudinary.com/dvex86jfq/image/upload/v1784265174/unsplash/1611974789855-9c2a0a7236a3.jpg",
        "modules": [
            {"title": "VC Fundamentals", "lessons": [
                {"title": "How VC Funds Work", "video_url": "https://www.youtube.com/watch?v=1qy1GX6gugw"},
                "Deal Sourcing", "Due Diligence", "Cap Table Basics"
            ]},
            {"title": "Valuation & Terms", "lessons": ["Pre-money vs Post-money", "Term Sheet Negotiation", "Dilution & Options", "SAFE vs Priced Rounds"]},
        ],
    },
    {
        "title": "Landscape & Nature Photography",
        "description": "Capture breathtaking landscapes and nature scenes like a professional. Learn to plan shoots using weather apps and golden hour calculators, master long exposure photography, understand ND filters, and develop a signature editing style in Lightroom.",
        "category": "Photography",
        "level": "INTERMEDIATE",
        "price": Decimal("0.00"),
        "is_free": True,
        "language": "English",
        "tags": "landscape, nature, long-exposure, lightroom",
        "instructor": "sofia_bell",
        "thumbnail_url": "https://res.cloudinary.com/dvex86jfq/image/upload/v1784263630/unsplash/1506905925346-21bda4d32df4.jpg",
        "modules": [
            {"title": "Planning & Field Craft", "lessons": [
                {"title": "Location Scouting", "video_url": "https://www.youtube.com/watch?v=tQ9gPQAk8xY"},
                "Golden Hour & Blue Hour", "Weather & Light Planning", "Gear for Landscapes"
            ]},
            {"title": "Techniques", "lessons": ["Long Exposure Basics", "ND Filters", "Focus Stacking", "Panoramic Stitching"]},
            {"title": "Post-Processing", "lessons": ["RAW Processing Workflow", "Sky Replacement", "Dodging & Burning", "Signature Style Development"]},
        ],
    },
]

# Courses to enroll the student in (by title)
ENROLL_IN = [
    "Complete Python Bootcamp: From Zero to Hero",
    "UI/UX Design Masterclass: Design Thinking to Prototype",
    "Machine Learning & AI: From Fundamentals to Deployment",
    "Business Strategy & Entrepreneurship",
    "Landscape & Nature Photography",
]


def download_image(url, filename):
    """Download an image from a URL and return as ContentFile."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            return ContentFile(response.read(), name=filename)
    except Exception as e:
        print(f"    ⚠ Could not download {url}: {e}")
        return None


class Command(BaseCommand):
    help = "Seed the database with realistic courses, instructors, and enrollments."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("\n🧹 Clearing existing data...\n"))
        self._clear_data()

        self.stdout.write(self.style.WARNING("👥 Creating instructor accounts...\n"))
        instructors = self._create_instructors()

        self.stdout.write(self.style.WARNING("🎓 Creating student account...\n"))
        student = self._create_student()

        self.stdout.write(self.style.WARNING("📚 Creating courses...\n"))
        created_courses = self._create_courses(instructors)

        self.stdout.write(self.style.WARNING("✅ Enrolling student...\n"))
        self._enroll_student(student, created_courses)

        self.stdout.write(self.style.SUCCESS("\n✅ Seed complete!\n"))
        self.stdout.write(self.style.SUCCESS("─" * 50))
        self.stdout.write(self.style.SUCCESS(f"  Instructors created: {len(instructors)}"))
        self.stdout.write(self.style.SUCCESS(f"  Courses created:     {len(created_courses)}"))
        self.stdout.write(self.style.SUCCESS(f"  Enrollments created: {len(ENROLL_IN)}"))
        self.stdout.write(self.style.SUCCESS("─" * 50))
        self.stdout.write(self.style.SUCCESS("\n  Student login:   demo_student / Student@123"))
        self.stdout.write(self.style.SUCCESS("  Instructor:      alex_morgan / Instructor@123"))
        self.stdout.write(self.style.SUCCESS("─" * 50 + "\n"))

    @transaction.atomic
    def _clear_data(self):
        from courses.models import Course, Module, Lesson, Quiz, QuizQuestion, QuizChoice, QuizAttempt
        from enrollments.models import Enrollment
        from progress.models import LessonProgress

        QuizAttempt.objects.all().delete()
        QuizChoice.objects.all().delete()
        QuizQuestion.objects.all().delete()
        Quiz.objects.all().delete()
        LessonProgress.objects.all().delete()
        Enrollment.objects.all().delete()
        Lesson.objects.all().delete()
        Module.objects.all().delete()
        Course.objects.all().delete()
        self.stdout.write("  Cleared courses, modules, lessons, quizzes, enrollments, progress.")


    def _create_instructors(self):
        instructors = {}
        for data in INSTRUCTORS:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "role": "MENTOR",
                    "is_mentor_approved": True,
                }
            )
            if created:
                user.set_password(data["password"])
                user.save()
                action = "Created"
            else:
                user.role = "MENTOR"
                user.is_mentor_approved = True
                user.save()
                action = "Updated"
            instructors[data["username"]] = user
            self.stdout.write(f"  {action}: {user.get_full_name()} (@{user.username})")
        return instructors

    def _create_student(self):
        user, created = User.objects.get_or_create(
            username=STUDENT["username"],
            defaults={
                "email": STUDENT["email"],
                "first_name": STUDENT["first_name"],
                "last_name": STUDENT["last_name"],
                "role": "STUDENT",
            }
        )
        if created:
            user.set_password(STUDENT["password"])
            user.save()
            self.stdout.write(f"  Created student: {user.get_full_name()} (@{user.username})")
        else:
            self.stdout.write(f"  Student already exists: @{user.username}")
        return user

    def _create_courses(self, instructors):
        from courses.models import Course, Module, Lesson

        created_courses = {}
        for course_data in COURSES:
            instructor = instructors.get(course_data["instructor"])
            if not instructor:
                self.stdout.write(self.style.WARNING(f"  Skipping {course_data['title']}: instructor not found"))
                continue

            course = Course.objects.create(
                title=course_data["title"],
                description=course_data["description"],
                category=course_data["category"],
                level=course_data["level"],
                price=course_data["price"],
                is_free=course_data["is_free"],
                language=course_data["language"],
                tags=course_data["tags"],
                mentor=instructor,
                is_published=True,
                status="PUBLISHED",
            )

            # Download and save thumbnail
            self.stdout.write(f"  → Creating: {course.title}")
            ext = ".jpg"
            fname = f"course_{uuid.uuid4().hex[:8]}{ext}"
            image_data = download_image(course_data["thumbnail_url"], fname)
            if image_data:
                course.thumbnail.save(fname, image_data, save=True)
                self.stdout.write(f"    ✓ Thumbnail downloaded")
            else:
                self.stdout.write(f"    ⚠ Using no thumbnail (download failed)")

            # Create modules and lessons
            for mod_idx, mod_data in enumerate(course_data.get("modules", [])):
                module = Module.objects.create(
                    course=course,
                    title=mod_data["title"],
                    order=mod_idx + 1,
                )
                for les_idx, lesson_data in enumerate(mod_data.get("lessons", [])):
                    if isinstance(lesson_data, str):
                        lesson_title = lesson_data
                        lesson_video_url = None
                        lesson_content = ""
                    else:
                        lesson_title = lesson_data["title"]
                        lesson_video_url = lesson_data.get("video_url")
                        lesson_content = lesson_data.get("content", "")
                    Lesson.objects.create(
                        module=module,
                        title=lesson_title,
                        lesson_type="VIDEO",
                        video_url=lesson_video_url,
                        content=lesson_content,
                        duration_minutes=(les_idx + 1) * 12,
                        order=les_idx + 1,
                    )

            created_courses[course.title] = course

        return created_courses

    def _enroll_student(self, student, courses):
        from enrollments.models import Enrollment

        for title in ENROLL_IN:
            course = courses.get(title)
            if not course:
                self.stdout.write(self.style.WARNING(f"  Skipping enrollment: '{title}' not found"))
                continue
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course,
                defaults={"status": "ACTIVE"}
            )
            if created:
                self.stdout.write(f"  Enrolled in: {title}")
            else:
                self.stdout.write(f"  Already enrolled: {title}")
