from rest_framework import serializers
from .models import Product

class PublicProductSerializer(serializers.ModelSerializer):
    """
    Public Product Serializer for Customer Browsing

    This serializer is used when customers browse approved products without authentication.
    It includes only the essential information needed for product discovery and purchasing decisions.

    Security Features:
    - No sensitive business information exposed
    - No internal status or audit fields
    - Only approved products are serialized with this class
    - Business name from snapshot (historical data integrity)

    Fields:
    - id: Product identifier for frontend routing
    - name: Product name for display
    - description: Product details for customer information
    - price: Product price for purchasing decisions
    - business_name: Business name (from snapshot for historical accuracy)

    Use Cases:
    - Product catalog browsing
    - Search results display
    - Product comparison
    - Customer-facing product listings
    """
    business_name = serializers.CharField(source='business_name_snapshot', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'business_name',
        ]
        read_only_fields = fields

class ProductSerializer(serializers.ModelSerializer):
    """
    Full Product Serializer for Business Management

    This is the main serializer for product management operations.
    It includes all product fields plus audit trail information for business users.

    Audit Trail Fields:
    - created_by_email: Email of user who created the product
    - approved_by_email: Email of user who approved the product
    - business_name: Business name snapshot for historical data
    - Timestamps: created_at, updated_at, approved_at

    Permission Context:
    - Used by authenticated business users (Editors, Approvers, Admins)
    - Includes workflow status information
    - Shows complete audit trail for compliance

    Fields:
    - Core: id, name, description, price, status
    - Relationships: business, created_by, approved_by
    - Audit: emails, timestamps, business name snapshot
    - Workflow: status for approval process tracking
    """

    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    approved_by_email = serializers.EmailField(source='approved_by.email', read_only=True)
    business_name = serializers.CharField(source='business_name_snapshot', read_only=True)

    class Meta:
        model = Product
        fields = [

            'id', 'name', 'description', 'price', 'status',

            'business', 'business_name',

            'created_by', 'created_by_email',
            'approved_by', 'approved_by_email',

            'created_at', 'updated_at', 'approved_at'
        ]

        read_only_fields = [
            'id', 'created_by', 'approved_by', 'approved_at',
            'created_at', 'updated_at'
        ]

    def validate_price(self, value):
        """
        Price validation for business rules

        Validation Rules:
        - Price cannot be negative (business rule)
        - Price must be a valid decimal (handled by model field)
        - Maximum precision: 10 digits, 2 decimal places (model constraint)

        Args:
            value: Price value to validate

        Returns:
            Validated price value

        Raises:
            ValidationError: If price is negative
        """
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value

class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Product Creation Serializer

    Specialized serializer for product creation with business validation.
    Used when Editors create new products through the API.

    Features:
    - Business selection validation (handled in view)
    - Price validation with business rules
    - Minimal fields for product creation
    - Automatic audit trail setup (handled in view)

    Business Logic:
    - Products start in 'draft' status (set in view)
    - created_by field set automatically (view handles this)
    - Business assignment validated based on user permissions

    Fields:
    - name: Product name (required)
    - description: Product description (required)
    - price: Product price with validation (required)
    - business: Business assignment (optional, defaults to user's business)

    Workflow:
    1. Editor fills out product information
    2. Serializer validates data (price, required fields)
    3. View validates business access and sets audit fields
    4. Product created in 'draft' status
    5. Editor can later submit for approval
    """
    business = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'price',
            'business'
        ]

    def validate_price(self, value):
        """
        Price validation for product creation

        Same validation rules as the main ProductSerializer.
        Ensures consistent price validation across all product operations.

        Args:
            value: Price value to validate

        Returns:
            Validated price value

        Raises:
            ValidationError: If price is negative
        """
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value
