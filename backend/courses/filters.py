import django_filters
from django.db.models import Avg
from .models import Course

class CourseFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    duration_min = django_filters.NumberFilter(field_name="total_duration", lookup_expr='gte')
    duration_max = django_filters.NumberFilter(field_name="total_duration", lookup_expr='lte')
    min_rating = django_filters.NumberFilter(method='filter_by_rating')

    class Meta:
        model = Course
        fields = {
            'category': ['exact'],
            'level': ['exact'],
            'language': ['exact'],
            'is_free': ['exact'],
        }

    def filter_by_rating(self, queryset, name, value):
        return queryset.filter(avg_rating__gte=value)
