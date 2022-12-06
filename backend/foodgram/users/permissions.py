from rest_framework import permissions


class IsAdminorOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        print('HAS PERMISSION')
        return request.user.is_authenticated or (
            request.user.is_authenticated and request.user.is_admin)

    def has_object_permission(self, request, view, obj):
        print('HAS PERMISSION OBJ')
        verdict = (
            request.user.is_authenticated and request.user.is_admin
        ) or request.user.username == obj.user.username
        return verdict


class IsAuth(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated
