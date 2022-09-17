from rest_framework import permissions

from .models import User


class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = User.objects.get(pk=request.user.id)
        return user.is_authenticated() and user.is_user


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        user = User.objects.get(pk=request.user.id)
        return user.is_authenticated() and user.is_manager


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = User.objects.get(pk=request.user.id)
        return user.is_authenticated() and user.is_admin


class IsAdminOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        user = User.objects.get(pk=request.user.id)
        return request.user.is_authenticated() and (
            user.is_admin or user.is_manager
        )
