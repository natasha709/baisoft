from rest_framework.permissions import BasePermission

class UserManagementPermission(BasePermission):
    """
    Tight permission rules for UserViewSet:
    - Admin/superuser can manage users in their business
    - Non-admins can only retrieve themselves (read-only)
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if getattr(user, "role", None) == "admin":
            business = getattr(user, "business", None)
            if not business:
                return False

            if view.action == "create" and not business.can_create_users:
                return False

            return True

        return view.action in ["retrieve"]

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if getattr(user, "role", None) == "admin":
            return getattr(obj, "business_id", None) == getattr(user, "business_id", None)

        return getattr(obj, "id", None) == getattr(user, "id", None)
