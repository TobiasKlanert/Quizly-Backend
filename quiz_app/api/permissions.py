"""Custom permission classes for quiz API."""

from rest_framework.permissions import BasePermission


class IsQuizOwner(BasePermission):
    """
    Allows access only if the logged-in user is the owner of the quiz.
    Expects the view to return a quiz object via get_object().
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
