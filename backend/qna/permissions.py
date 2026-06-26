from rest_framework import permissions


class IsEnrolledOrMentorOrAdmin(permissions.BasePermission):
    """
    Allow read for enrolled students, mentor of the course, and admins.
    Allow write (create question/reply) for enrolled students + mentor + admin.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admins always pass
        if request.user.role == 'ADMIN':
            return True

        # Mentors always pass (course-level check happens in the view)
        if request.user.role == 'MENTOR':
            return True

        # For students, enrollment is checked per-view using course_id from the URL
        return True  # Final enrollment check is in the view


class IsMentorOrAdminForPin(permissions.BasePermission):
    """Only the course mentor or an admin can pin/unpin questions."""
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'ADMIN':
            return True
        # obj is a Question; check if user is its course's mentor
        return obj.course.mentor == user
