from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ReviewViewSet, ReviewReportViewSet

# SimpleRouter (not DefaultRouter): several apps are mounted at the same
# `api/` prefix, and each DefaultRouter would register its own competing
# `api-root` view at that prefix. SimpleRouter omits the root view.
router = SimpleRouter()
router.register(r'reviews', ReviewViewSet)
router.register(r'reports', ReviewReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
