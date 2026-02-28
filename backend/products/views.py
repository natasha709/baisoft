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
    - GET /api/products/
    - POST /api/products/
    - GET /api/products/{id}/
    - PUT/PATCH /api/products/{id}/
    - DELETE /api/products/{id}/
    - POST /api/products/{id}/approve/
    - POST /api/products/{id}/submit_for_approval/

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

        if self.action == 'list' and self.request.query_params.get('public') == 'true':
            return [AllowAny()]

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

        if self.request.query_params.get('public') == 'true':
            return Product.objects.filter(status='approved')

        if not self.request.user.is_authenticated:
            return Product.objects.none()

        if self.request.user.is_superuser:
            return Product.objects.all()

        return Product.objects.filter(
            Q(business__owner=self.request.user) |
            Q(business=self.request.user.business)
        ).distinct()

    def get_serializer_class(self):
        """
        Choose appropriate serializer based on request type

        Serializer Selection:
        - Public listing: Limited fields for customer browsing
        - Product creation: Validation-focused serializer
        - Regular operations: Full product serializer with audit fields
        """

        if self.action == 'list' and self.request.query_params.get('public') == 'true':
            return PublicProductSerializer

        if self.action == 'create':
            return ProductCreateSerializer

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

        if not self.request.user.has_permission('create_product'):
            raise PermissionDenied("You don't have permission to create products")

        business = serializer.validated_data.get('business')

        if not self.request.user.is_superuser:

            if business:

                has_access = Business.objects.filter(
                    Q(id=business.id) & (
                        Q(owner=self.request.user) |
                        Q(id=self.request.user.business_id)
                    )
                ).exists()

                if not has_access:
                    raise PermissionDenied("You don't have access to this business")
            else:

                business = self.request.user.business

        serializer.save(
            created_by=self.request.user,
            business=business,
            status='draft'
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

        if not self.request.user.has_permission('edit_product'):
            raise PermissionDenied("You don't have permission to edit products")

        if not self.request.user.is_superuser:

            serializer.validated_data.pop('business', None)

        serializer.save()

    def perform_destroy(self, instance):
        """
        Delete product with permission validation

        Deletion Rules:
        - Only Admins can delete products
        - Maintains referential integrity (audit trail preserved via SET_NULL)

        Note: In production, consider soft deletion to preserve audit trails
        """

        if not self.request.user.has_permission('delete_product'):
            raise PermissionDenied("You don't have permission to delete products")

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

        if not request.user.has_permission('approve_product'):
            return Response(
                {'error': "You don't have permission to approve products"},
                status=status.HTTP_403_FORBIDDEN
            )

        if product.status == 'approved':
            return Response(
                {'error': 'Product is already approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if product.status != 'pending_approval':
            return Response(
                {'error': 'Only products pending approval can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        product.status = 'approved'
        product.approved_by = request.user
        product.approved_at = timezone.now()
        product.save()

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

        if not request.user.has_permission('edit_product'):
            return Response(
                {'error': "You don't have permission to submit products for approval"},
                status=status.HTTP_403_FORBIDDEN
            )

        if product.status != 'draft':
            return Response(
                {'error': 'Only draft products can be submitted for approval'},
                status=status.HTTP_400_BAD_REQUEST
            )

        product.status = 'pending_approval'
        product.save()

        serializer = self.get_serializer(product)
        return Response(serializer.data)
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """
        Export Product Report Endpoint (CSV)

        Generates a downloadable CSV report of products.
        Follows the same visibility rules as the product listing:
        - Superusers: All products across all businesses
        - Regular Users: Products from their associated business
        """
        import csv
        from django.http import HttpResponse

        products = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="product_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Description', 'Price', 'Status', 'Business', 'Created By', 'created AT', 'Approved by', 'Approved at'])

        for product in products:
            writer.writerow([
                product.id,
                product.name,
                product.description,
                product.price,
                product.get_status_display(),
                product.business_name_snapshot or product.business.name,
                product.created_by.email if product.created_by else 'N/A',
                product.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                product.approved_by.email if product.approved_by else 'N/A',
                product.approved_at.strftime("%Y-%m-%d %H:%M:%S") if product.approved_at else 'N/A'
            ])

        return response
