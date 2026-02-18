from rest_framework import serializers
from .models import Product


class PublicProductSerializer(serializers.ModelSerializer):
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
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    approved_by_email = serializers.EmailField(source='approved_by.email', read_only=True)
    business_name = serializers.CharField(source='business_name_snapshot', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'status',
            'business', 'business_name', 'created_by', 'created_by_email',
            'approved_by', 'approved_by_email', 'created_at', 'updated_at', 'approved_at'
        ]
        read_only_fields = ['id', 'created_by', 'approved_by', 'approved_at', 'created_at', 'updated_at']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'business']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value
