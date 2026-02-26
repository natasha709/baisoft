# Product Management API Views
# This module contains all API endpoints for product CRUD operations with approval workflow.
# It implements role-based permissions and business isolation for the marketplace system.
#
# Key Features:
# - Product CRUD with role-based permissions (Editor creates, Approver approves)
# - Three-stage approval workflow (Draft → Pending → Approved)
# - Business isolation (users only see products from their business)
# - Public product listing for customers (approved products only)
# - Audit trail tracking (who created, who approved, when)
# - Permission validation at every operation

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from django.utils import timezone
from businesses.models import Business
from .models import Product
from .serializers import ProductSerializer, ProductCreateSerializer, PublicProductSerializer
from .permissions import ProductPermission


class ProductViewSet(viewsets.ModelViewSet):
    """
    Product Management API ViewSet
    
    This is the main API for product operations in the marketplace system.
    It handles the complete product lifecycle from creation to approval.
    
    Endpoints:
    - GET /api/products/                    # List products (filtered by permissions)
    - POST /api/products/                   # Create new product (Editors only)
    - GET /api/products/{id}/               # Get product details
    - PUT/PATCH /api/products/{id}/         # Update product (Editors only)
    - DELETE /api/products/{id}/            # Delete product (Admins only)
    - POST /api/products/{id}/approve/      # Approve product (Approvers only)
    - POST /api/products/{id}/submit_for_approval/  # Submit for approval (Editors only)
    
    Permission Matrix:
    - Admin: Full access (create, edit, approve, delete)
    - Editor: Create and edit products, submit for approval
    - Approver: Approve products, view all
    - Viewer: View all products
    - Public: View approved products only (no authentication required)
    
    Business Isolation:
    - Users only see products from businesses they have access to
    - Superusers can see all products across all businesses
    - Public users see approved products from all businesses
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        """
        Dynamic permission assignment based on request type
        
        Permission Logic:
        - Public product listing: No authentication required
        - All other operations: Authentication + role-based permissions required
        
        This allows customers to browse approved products without logging in,
        while protecting business operations behind authentication.
        """
        # Public product listing doesn't require authentication
        if self.action == 'list' and self.request.query_params.get('public') == 'true':
            return [AllowAny()]
        
        # All other operations require authentication and role permissions
        return [IsAuthenticated(), ProductPermission()]

    def get_queryset(self):
        """
        Filter products based on user permissions and request type
        
        Filtering Logic:
        1. Public requests: Only approved products (for customer browsing)
        2. Unauthenticated: No products (security)
        3. Superusers: All products (platform administration)
        4. Regular users: Products from businesses they have access to
        
        Business Access Rules:
        - Business owners: See products from businesses they own
        - Business members: See products from their associated business
        - Cross-business access: Users can be owners of multiple businesses
        """
        # Public listing - customers browsing approved products
        if self.request.query_params.get('public') == 'true':
            return Product.objects.filter(status='approved')
        
        # Security: unauthenticated users get no products
        if not self.request.user.is_authenticated:
            return Product.objects.none()
        
        # Superusers see everything (platform administration)
        if self.request.user.is_superuser:
            return Product.objects.all()
        
        # Regular users: products from businesses they have access to
        # This includes businesses they own OR their associated business
        return Product.objects.filter(
            Q(business__owner=self.request.user) |  # Businesses they own
            Q(business=self.request.user.business)  # Their associated business
        ).distinct()

    def get_serializer_class(self):
        """
        Choose appropriate serializer based on request type
        
        Serializer Selection:
        - Public listing: Limited fields for customer browsing
        - Product creation: Validation-focused serializer
        - Regular operations: Full product serializer with audit fields
        """
        # Public listing uses minimal serializer (no sensitive business data)
        if self.action == 'list' and self.request.query_params.get('public') == 'true':
            return PublicProductSerializer
        
        # Product creation uses specialized serializer with business validation
        if self.action == 'create':
            return ProductCreateSerializer
        
        # Default: full serializer with all fields and audit trail
        return ProductSerializer

    def perform_create(self, serializer):
        """
        Create new product with role-based permission validation
        
        Creation Workflow:
        1. Validate user has 'create_product' permission (Editors and Admins)
        2. Validate business access (users can only create in accessible businesses)
        3. Set audit fields (created_by, business, initial status)
        4. Create product in 'draft' status
        
        Business Validation:
        - Superusers: Can create products in any business
        - Regular users: Can only create in businesses they own or are members of
        - Default business: User's associated business if none specified
        
        Security Features:
        - Permission check before any database operations
        - Business access validation prevents cross-business product creation
        - Automatic audit trail setup
        """
        # Permission check: only Editors and Admins can create products
        if not self.request.user.has_permission('create_product'):
            raise PermissionDenied("You don't have permission to create products")
        
        # Business validation and assignment
        business = serializer.validated_data.get('business')
        
        if not self.request.user.is_superuser:
            # Validate business access for regular users
            if business:
                # Check if user has access to the specified business
                has_access = Business.objects.filter(
                    Q(id=business.id) & (
                        Q(owner=self.request.user) |  # User owns the business
                        Q(id=self.request.user.business_id)  # User is member of business
                    )
                ).exists()
                
                if not has_access:
                    raise PermissionDenied("You don't have access to this business")
            else:
                # Default to user's associated business
                business = self.request.user.business

        # Create product with audit trail and initial status
        serializer.save(
            created_by=self.request.user,  # Track who created the product
            business=business,  # Assign to validated business
            status='draft'  # All products start as drafts
        )

    def perform_update(self, serializer):
        """
        Update existing product with permission validation
        
        Update Rules:
        1. Only Editors and Admins can edit products
        2. Regular users cannot change business assignment (security)
        3. Superusers have full update access
        
        Security Features:
        - Permission validation before update
        - Business assignment protection (prevents moving products between businesses)
        - Maintains audit trail integrity
        """
        # Permission check: only Editors and Admins can edit products
        if not self.request.user.has_permission('edit_product'):
            raise PermissionDenied("You don't have permission to edit products")
        
        # Security: prevent regular users from changing business assignment
        if not self.request.user.is_superuser:
            # Remove business field from update data to prevent tampering
            serializer.validated_data.pop('business', None)
            
        # Perform the update (audit fields like updated_at are handled automatically)
        serializer.save()

    def perform_destroy(self, instance):
        """
        Delete product with permission validation
        
        Deletion Rules:
        - Only Admins can delete products
        - Maintains referential integrity (audit trail preserved via SET_NULL)
        
        Note: In production, consider soft deletion to preserve audit trails
        """
        # Permission check: only Admins can delete products
        if not self.request.user.has_permission('delete_product'):
            raise PermissionDenied("You don't have permission to delete products")
        
        # Perform deletion (related audit records are preserved via SET_NULL)
        instance.delete()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve Product Endpoint - Core of the approval workflow
        
        This endpoint allows Approvers to approve products that are pending approval.
        It's a critical part of the quality control process.
        
        Approval Workflow:
        1. Validate user has 'approve_product' permission (Approvers and Admins)
        2. Validate product is in 'pending_approval' status
        3. Update product status to 'approved'
        4. Record approval audit trail (who approved, when)
        5. Make product visible to customers
        
        Business Rules:
        - Only products in 'pending_approval' status can be approved
        - Products already approved cannot be re-approved
        - Approval creates permanent audit trail
        
        Response: Updated product data with approval information
        """
        product = self.get_object()
        
        # Permission check: only Approvers and Admins can approve products
        if not request.user.has_permission('approve_product'):
            return Response(
                {'error': "You don't have permission to approve products"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Business rule: cannot re-approve already approved products
        if product.status == 'approved':
            return Response(
                {'error': 'Product is already approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Business rule: only pending products can be approved
        if product.status != 'pending_approval':
            return Response(
                {'error': 'Only products pending approval can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Perform approval with full audit trail
        product.status = 'approved'
        product.approved_by = request.user  # Record who approved
        product.approved_at = timezone.now()  # Record when approved
        product.save()
        
        # Return updated product data
        serializer = self.get_serializer(product)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def submit_for_approval(self, request, pk=None):
        """
        Submit Product for Approval Endpoint
        
        This endpoint allows Editors to submit their draft products for approval.
        It moves products from 'draft' to 'pending_approval' status.
        
        Submission Workflow:
        1. Validate user has 'edit_product' permission (Editors and Admins)
        2. Validate product is in 'draft' status
        3. Update product status to 'pending_approval'
        4. Product becomes visible to Approvers for review
        
        Business Rules:
        - Only draft products can be submitted for approval
        - Once submitted, product cannot be edited until approved or rejected
        - Submission triggers approval workflow
        
        Response: Updated product data with new status
        """
        product = self.get_object()

        # Permission check: only Editors and Admins can submit for approval
        if not request.user.has_permission('edit_product'):
            return Response(
                {'error': "You don't have permission to submit products for approval"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Business rule: only draft products can be submitted
        if product.status != 'draft':
            return Response(
                {'error': 'Only draft products can be submitted for approval'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Move product to pending approval status
        product.status = 'pending_approval'
        product.save()
        
        # Return updated product data
        serializer = self.get_serializer(product)
        return Response(serializer.data)
