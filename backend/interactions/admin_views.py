from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Prefetch
from .models import Review, ReviewReport
from .serializers import ReviewSerializer

class AdminReviewModerationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'])
    def flagged(self, request):
        reviews = Review.objects.filter(is_flagged=True).prefetch_related(
            Prefetch('reports', queryset=ReviewReport.objects.select_related('reported_by'))
        ).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        data = serializer.data
        for i, review in enumerate(reviews):
            reports_data = []
            for report in review.reports.all():
                reports_data.append({
                    'id': report.id,
                    'reason': report.reason,
                    'reported_by': report.reported_by.username,
                    'created_at': report.created_at,
                })
            data[i]['reports'] = reports_data
        return Response(data)

    @action(detail=True, methods=['post'])
    def delete_review(self, request, pk=None):
        from django.shortcuts import get_object_or_404
        review = get_object_or_404(Review, pk=pk)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def unflag(self, request, pk=None):
        from django.shortcuts import get_object_or_404
        review = get_object_or_404(Review, pk=pk)
        review.is_flagged = False
        review.save(update_fields=['is_flagged'])
        return Response({'status': 'unflagged'})
