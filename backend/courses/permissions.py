from rest_framework import permissions


class IsMentorOrReadOnly(permissions.BasePermission):
    """Allow safe methods for anyone; write only for MENTOR or ADMIN role."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None)
        return role in ('MENTOR', 'ADMIN') or request.user.is_staff


def get_mentor_for_object(obj):
    """
    Recursively walks up model relations until it finds a 'mentor' field.
    Supports Course, Module, Lesson, Quiz, QuizQuestion, QuizChoice.
    """
    current = obj
    while current is not None:
        if hasattr(current, 'mentor'):
            return current.mentor
        elif hasattr(current, 'course'):
            current = current.course
        elif hasattr(current, 'module'):
            current = current.module
        elif hasattr(current, 'quiz'):
            current = current.quiz
        elif hasattr(current, 'question'):
            current = current.question
        else:
            break
    return None


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission: allow if request user is an admin
    (is_staff OR role==ADMIN) or if they own the object (mentor).
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write operations require MENTOR or ADMIN role
        role = getattr(request.user, 'role', None)
        return role in ('MENTOR', 'ADMIN') or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user.is_staff or getattr(request.user, 'role', None) == 'ADMIN':
            return True

        # Safe methods are always fine
        if request.method in permissions.SAFE_METHODS:
            return True

        # Resolve mentor and check ownership
        mentor = get_mentor_for_object(obj)
        if mentor is not None:
            return mentor == request.user

        return False
