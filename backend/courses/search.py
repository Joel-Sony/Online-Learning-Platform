from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector, TrigramSimilarity
from rest_framework import filters


class CourseSearchBackend(filters.BaseFilterBackend):
    """PostgreSQL full-text search for courses.

    Supports:
    - Full-text search across title, description, tags, mentor name, category
    - Weighted ranking (title > tags > category > description)
    - Trigram fuzzy matching for typos
    """

    search_param = 'search'
    search_title = 'A'
    search_tags = 'B'
    search_category = 'C'
    search_description = 'D'

    def filter_queryset(self, request, queryset, view):
        query = request.query_params.get(self.search_param, '').strip()
        if not query:
            return queryset

        vector = (
            SearchVector('title', weight=self.search_title)
            + SearchVector('tags', weight=self.search_tags)
            + SearchVector('category', weight=self.search_category)
            + SearchVector('description', weight=self.search_description)
        )

        search_query = SearchQuery(query, config='english')

        # Try exact full-text search first
        ranked = queryset.annotate(
            rank=SearchRank(vector, search_query)
        ).filter(rank__gte=0.01)

        if ranked.exists():
            return ranked.order_by('-rank')

        # Fallback to trigram similarity for fuzzy matching
        trigram = queryset.annotate(
            similarity=TrigramSimilarity('title', query)
        ).filter(similarity__gt=0.1)

        if trigram.exists():
            return trigram.order_by('-similarity')

        # Final fallback: basic icontains
        from django.db.models import Q
        return queryset.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(tags__icontains=query)
            | Q(category__icontains=query)
            | Q(mentor__username__icontains=query)
        )
