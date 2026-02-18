from rest_framework import serializers
from .models import Business, User


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['id', 'name', 'can_create_users', 'can_assign_roles', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='business.name', read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    password_change_required = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'business', 'business_name', 
                  'password', 'is_active', 'password_change_required']
        read_only_fields = ['id', 'password_change_required']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    business_name = serializers.CharField(write_only=True)
    can_create_users = serializers.BooleanField(write_only=True, default=True)
    can_assign_roles = serializers.BooleanField(write_only=True, default=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'role', 'business_name', 'can_create_users', 'can_assign_roles']

    def create(self, validated_data):
        business_name = validated_data.pop('business_name')
        can_create_users = validated_data.pop('can_create_users', True)
        can_assign_roles = validated_data.pop('can_assign_roles', True)
        role = validated_data.get('role', 'admin')

        # Create user first to assign as owner
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=role
        )
        
        business = Business.objects.create(
            name=business_name,
            can_create_users=can_create_users,
            can_assign_roles=can_assign_roles,
            owner=user  # Set the user as owner
        )
        
        # Assign the user to the business
        user.business = business
        user.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords do not match")
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError("New password must be different from old password")
        return data
