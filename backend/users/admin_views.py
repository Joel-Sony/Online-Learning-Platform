from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .serializers import AdminUserSerializer
from notifications.utils import create_notification

User = get_user_model()

class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user.pk == request.user.pk:
            return Response({'error': 'You cannot delete yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def ban(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        status_msg = "deactivated" if not user.is_active else "activated"
        return Response({'status': f'User {status_msg}'})

class AdminMentorApprovalViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'])
    def pending(self, request):
        pending_mentors = User.objects.filter(role='MENTOR', is_mentor_approved=False)
        serializer = AdminUserSerializer(pending_mentors, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        mentor = get_object_or_404(User, pk=pk, role='MENTOR')
        mentor.is_mentor_approved = True
        mentor.save()
        
        create_notification(
            recipient=mentor,
            type='ANNOUNCEMENT',
            message="Your mentor application has been approved! You can now create courses."
        )
        return Response({'status': 'Mentor approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        mentor = get_object_or_404(User, pk=pk, role='MENTOR')
        create_notification(
            recipient=mentor,
            type='ANNOUNCEMENT',
            message="Your mentor application was not approved at this time."
        )
        return Response({'status': 'Mentor rejected'})
