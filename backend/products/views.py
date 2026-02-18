from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .models import Product
from .serializers import ProductSerializer, ProductCreateSerializer, PublicProductSerializer
from .permissions import ProductPermission


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action == 'list' and self.request.query_params.get('public') == 'true':
            return [AllowAny()]
        return [IsAuthenticated(), ProductPermission()]

    def get_queryset(self):
        # Public listing - only approved products
        if self.request.query_params.get('public') == 'true':
            return Product.objects.filter(status='approved')
        
        # Authenticated users
        if not self.request.user.is_authenticated:
            return Product.objects.none()
        
        # Superuser sees all
        if self.request.user.is_superuser:
            return Product.objects.all()
        
        # Users see products from their business
        return Product.objects.filter(business=self.request.user.business)

    def get_serializer_class(self):
        if self.action == 'list' and self.request.query_params.get('public') == 'true':
            return PublicProductSerializer
        if self.action == 'create':
            return ProductCreateSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        if not self.request.user.has_permission('create_product'):
            raise PermissionDenied("You don't have permission to create products")
        
        # Superusers can select business, regular users are tied to their business
        business = serializer.validated_data.get('business')
        if not self.request.user.is_superuser or not business:
            business = self.request.user.business

        serializer.save(
            created_by=self.request.user,
            business=business,
            status='draft'
        )

    def perform_update(self, serializer):
        if not self.request.user.has_permission('edit_product'):
            raise PermissionDenied("You don't have permission to edit products")
        
        # Prevent non-superusers from changing the business
        if not self.request.user.is_superuser:
            serializer.validated_data.pop('business', None)
            
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.has_permission('delete_product'):
            raise PermissionDenied("You don't have permission to delete products")
        instance.delete()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
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
