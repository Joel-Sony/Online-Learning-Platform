from rest_framework import permissions

class IsMentorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'MENTOR'

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        # Course object
        if hasattr(obj, 'mentor'):
            return obj.mentor == request.user
        
        # Module object
        if hasattr(obj, 'course'):
            return obj.course.mentor == request.user
            
        # Lesson object
        if hasattr(obj, 'module'):
            return obj.module.course.mentor == request.user
            
        return False
