from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        # Handle different object types
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        # All permissions are only allowed to the owner of the object.
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user


class IsSeller(permissions.BasePermission):
    """
    Custom permission to only allow sellers to access certain views.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_seller


class IsSellerOwner(permissions.BasePermission):
    """
    Custom permission to only allow seller owners to edit their seller profile.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_seller

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user