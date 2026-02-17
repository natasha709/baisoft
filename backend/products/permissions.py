from rest_framework import permissions


class ProductPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Check role-based permissions
        if view.action == 'create':
            return request.user.has_permission('create_product')
        elif view.action in ['update', 'partial_update']:
            return request.user.has_permission('edit_product')
        elif view.action == 'destroy':
            return request.user.has_permission('delete_product')
        elif view.action == 'approve':
            return request.user.has_permission('approve_product')
        elif view.action == 'submit_for_approval':
            return request.user.has_permission('edit_product')
        
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Users can only access products from their business
        return obj.business == request.user.business
