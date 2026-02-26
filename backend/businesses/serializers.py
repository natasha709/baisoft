# Data Serializers for Business and User Management
# This module defines how data is converted between JSON (API) and Python objects (models).
# Serializers handle validation, data transformation, and business logic for API endpoints.
#
# Key Features:
# - User registration with automatic business creation
# - Password handling with security validations
# - Business permissions and role management
# - User invitation system support
# - Data validation and error handling

from rest_framework import serializers
from .models import Business, User


class BusinessSerializer(serializers.ModelSerializer):
    """
    Business Data Serializer
    
    Handles serialization of business data for API responses.
    Used when admins view or manage business settings.
    
    Fields:
    - id: Unique business identifier
    - name: Business name (e.g., "Acme Corp")
    - can_create_users: Whether business can invite new users
    - can_assign_roles: Whether business can assign roles to users
    - created_at/updated_at: Timestamps (read-only)
    """
    class Meta:
        model = Business
        fields = ['id', 'name', 'can_create_users', 'can_assign_roles', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """
    User Data Serializer
    
    Main serializer for user data in API responses. Handles user profiles,
    role information, and business associations.
    
    Special Fields:
    - business_name: Computed field showing user's business name
    - password: Write-only for security (never returned in responses)
    - password_change_required: Read-only flag for invitation system
    
    Used for:
    - User profile display
    - User management by admins
    - Login responses
    - User invitation system
    """
    business_name = serializers.CharField(source='business.name', read_only=True)  # Display business name in user data
    password = serializers.CharField(write_only=True, required=False)  # Never expose passwords in API responses
    password_change_required = serializers.BooleanField(read_only=True)  # Flag for invitation system

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'business', 'business_name', 
                  'password', 'is_active', 'password_change_required']
        read_only_fields = ['id', 'password_change_required']

    def create(self, validated_data):
        """
        Create new user with proper password handling
        
        Handles password encryption and user creation.
        If no password provided, sets unusable password (for invitation system).
        """
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)  # Encrypt password
        else:
            user.set_unusable_password()  # For users created via invitation
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Update existing user with proper password handling
        
        Updates user fields and handles password changes securely.
        """
        password = validated_data.pop('password', None)
        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        # Handle password update if provided
        if password:
            instance.set_password(password)  # Encrypt new password
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    """
    User Registration Serializer
    
    Handles new user registration with automatic business creation.
    This is used when business owners first sign up for the platform.
    
    Process:
    1. Validate user data and business information
    2. Create the user account
    3. Create associated business with user as owner
    4. Set up business permissions
    
    Fields:
    - User fields: email, password, first_name, last_name, role
    - Business fields: business_name, can_create_users, can_assign_roles
    
    Security:
    - Password minimum length validation
    - Email uniqueness validation
    - Automatic admin role assignment for business owners
    """
    password = serializers.CharField(write_only=True, min_length=8)  # Enforce password security
    business_name = serializers.CharField(write_only=True)  # Business name for new business
    can_create_users = serializers.BooleanField(write_only=True, default=True)  # Business permission
    can_assign_roles = serializers.BooleanField(write_only=True, default=True)  # Business permission

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'role', 'business_name', 'can_create_users', 'can_assign_roles']

    def create(self, validated_data):
        """
        Create new user and associated business
        
        Registration workflow:
        1. Extract business data from user data
        2. Create user account with encrypted password
        3. Create business with user as owner
        4. Associate user with the business
        5. Set default admin role for business owner
        
        This creates a complete business setup in one operation.
        """
        # Extract business-specific data
        business_name = validated_data.pop('business_name')
        can_create_users = validated_data.pop('can_create_users', True)
        can_assign_roles = validated_data.pop('can_assign_roles', True)
        role = validated_data.get('role', 'admin')  # Business owners are admins by default

        # Create user account first (needed as business owner)
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],  # Automatically encrypted
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=role
        )
        
        # Create associated business with permissions
        business = Business.objects.create(
            name=business_name,
            can_create_users=can_create_users,  # Can this business invite users?
            can_assign_roles=can_assign_roles,  # Can this business assign roles?
            owner=user  # Set the user as business owner
        )
        
        # Link user to their business
        user.business = business
        user.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    User Login Serializer
    
    Simple serializer for login credentials validation.
    Used by login endpoint to validate email and password format.
    
    Fields:
    - email: User's email address
    - password: User's password (could be temporary password)
    
    Note: Actual authentication happens in the view, not here.
    """
    email = serializers.EmailField()  # Validate email format
    password = serializers.CharField(write_only=True)  # Never expose password in responses


class ChangePasswordSerializer(serializers.Serializer):
    """
    Password Change Serializer
    
    Critical component of the user invitation system. When users receive
    temporary passwords via email, they use this serializer to set their
    own secure password.
    
    Validation Rules:
    - New password must be at least 8 characters
    - New password must match confirmation
    - New password must be different from old password
    
    Fields:
    - old_password: Current password (temporary for new users)
    - new_password: User's chosen new password
    - confirm_password: Confirmation of new password
    
    Security Features:
    - Password confirmation validation
    - Prevents reusing old password
    - Minimum length enforcement
    """
    old_password = serializers.CharField(write_only=True)  # Current password for verification
    new_password = serializers.CharField(write_only=True, min_length=8)  # Enforce password security
    confirm_password = serializers.CharField(write_only=True)  # Password confirmation

    def validate(self, data):
        """
        Custom validation for password change
        
        Security checks:
        1. New password must match confirmation
        2. New password must be different from old password
        3. Both enforced at serializer level for security
        
        Returns validated data or raises ValidationError
        """
        # Ensure password confirmation matches
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords do not match")
        
        # Prevent password reuse (security best practice)
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError("New password must be different from old password")
        
        return data
