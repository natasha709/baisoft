from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Q
from .models import Business, User
from .serializers import BusinessSerializer, UserSerializer, RegisterSerializer, LoginSerializer, ChangePasswordSerializer
from .email_service import generate_temporary_password, send_invitation_email, set_temporary_password_expiry
from .permissions import UserManagementPermission

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    User Registration Endpoint

    Allows new users to create accounts and automatically get JWT tokens.
    This is used when business owners first sign up for the platform.

    Request Body:
    - email: User's email address (must be unique)
    - password: User's chosen password
    - first_name: User's first name
    - last_name: User's last name
    - business_name: Name of their business

    Response:
    - user: User profile data
    - tokens: JWT access and refresh tokens for immediate login
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():

        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    User Login Endpoint

    Authenticates users and provides JWT tokens for API access.
    Handles both regular users and those with temporary passwords.

    Request Body:
    - email: User's email address
    - password: User's password (could be temporary password)

    Response:
    - user: User profile data (includes password_change_required flag)
    - tokens: JWT access and refresh tokens

    Special Cases:
    - If user has temporary password, they'll be redirected to change password
    - Temporary passwords expire after 7 days
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():

        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        if user:

            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Get Current User Profile

    Returns the profile data for the currently authenticated user.
    Used by frontend to get user info after login or page refresh.

    Response:
    - User profile data including role, business, and password change status
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change User Password Endpoint

    This is a critical part of the invitation system. When users receive
    temporary passwords via email, they must use this endpoint to set
    their own secure password on first login.

    Request Body:
    - old_password: Current password (temporary password for new users)
    - new_password: User's chosen new password

    Security Features:
    - Verifies current password before allowing change
    - Checks if temporary password has expired (7 days)
    - Clears password_change_required flag after successful change
    - Removes temporary password expiry date

    Response:
    - Success message or error details
    """
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user

        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        if user.temporary_password_expires and timezone.now() > user.temporary_password_expires:
            return Response({'error': 'Temporary password has expired. Please contact your administrator.'},
                          status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.password_change_required = False
        user.temporary_password_expires = None
        user.save()

        return Response({'message': 'Password changed successfully'})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BusinessViewSet(viewsets.ModelViewSet):
    """
    Business Management API ViewSet

    Handles CRUD operations for businesses with proper access control.
    Supports multi-tenancy where users can only see/manage their own businesses.

    Permissions:
    - Superusers: Can manage all businesses
    - Business owners: Can manage their own businesses
    - Regular users: Can view their associated business

    Features:
    - Automatic business ownership assignment
    - Support for creating initial users when creating a business
    - Business isolation (users only see their own business data)
    """
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter businesses based on user permissions

        Business isolation logic:
        - Superusers: See all businesses (for platform administration)
        - Business owners: See businesses they own
        - Regular users: See only their associated business
        """
        if self.request.user.is_superuser:
            return Business.objects.all()

        return Business.objects.filter(
            Q(owner=self.request.user) |
            Q(id=self.request.user.business_id)
        ).distinct()

    def perform_create(self, serializer):
        """
        Create new business with automatic ownership assignment

        When a business is created:
        1. Current user becomes the owner
        2. Optionally create an initial user for the business
        3. Send invitation email to the initial user

        This supports the workflow where business owners can create
        their company and immediately invite their first employee.
        """
        business = serializer.save(owner=self.request.user)

        initial_user_data = self.request.data.get('initial_user')
        if initial_user_data:
            email = initial_user_data.get('email')
            first_name = initial_user_data.get('first_name', '')
            last_name = initial_user_data.get('last_name', '')
            role = initial_user_data.get('role', 'viewer')

            if email:

                user = User.objects.create(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                    business=business,
                    password_change_required=True
                )

                temp_password = generate_temporary_password()
                user.set_password(temp_password)

                set_temporary_password_expiry(user)
                user.save()

                send_invitation_email(user, temp_password, self.request.user)

class UserViewSet(viewsets.ModelViewSet):
    """
    User Management API ViewSet

    This is the core of the user invitation and management system.
    Handles creating, updating, and deleting users with proper role-based access control.

    Key Features:
    - Role-based permissions (only admins can manage users)
    - Automatic temporary password generation
    - Email invitation system
    - Business isolation (admins can only manage users in their business)
    - Support for user status tracking (pending/active)

    Permissions:
    - Superusers: Can manage all users across all businesses
    - Admins: Can manage users within their own business
    - Other roles: Can only view their own profile
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, UserManagementPermission]

    def get_queryset(self):
        """
        Filter users based on role-based access control

        Access levels:
        - Superusers: See all users (platform administration)
        - Admins: See all users in their business
        - Other roles: See only their own profile

        This ensures business isolation and proper access control.
        """
        if self.request.user.is_superuser:
            return User.objects.all()
        if self.request.user.role == 'admin':
            return User.objects.filter(business=self.request.user.business)
        return User.objects.filter(id=self.request.user.id)

    def perform_create(self, serializer):
        """
        Create new user with invitation system

        This is the core of the user invitation workflow:
        1. Validate that only admins can create users
        2. Create user with temporary password
        3. Set password change requirements and expiry
        4. Send professional invitation email
        5. Handle email failures gracefully

        The created user will have:
        - Temporary password (expires in 7 days)
        - password_change_required = True
        - invitation_sent_at timestamp
        """

        if self.request.user.is_superuser:

            user = serializer.save()
        else:

            if self.request.user.role != 'admin':
                raise PermissionDenied("You don't have permission to create users")

            user = serializer.save(business=self.request.user.business)

        temp_password = generate_temporary_password()

        user.set_password(temp_password)

        set_temporary_password_expiry(user)

        email_sent = send_invitation_email(user, temp_password, self.request.user)

        if not email_sent:
            print(f"Warning: Failed to send invitation email to {user.email}")

        return user

    def perform_update(self, serializer):
        """
        Update user with proper permission checks

        Business rules:
        - Only admins and superusers can update users
        - Admins cannot move users between businesses
        - Role assignment depends on business capabilities
        """

        if not self.request.user.is_superuser and self.request.user.role != 'admin':
            raise PermissionDenied("You don't have permission to update users")

        if self.request.user.is_superuser:

            serializer.save()
            return

        new_role = serializer.validated_data.get('role')
        if new_role and new_role != serializer.instance.role:
            business = self.request.user.business

            if not business or not business.can_assign_roles:

                serializer.validated_data.pop('role', None)

        serializer.save(business=self.request.user.business)

    def perform_destroy(self, instance):
        """
        Delete user with proper permission and business isolation checks

        Security rules:
        - Only admins and superusers can delete users
        - Admins can only delete users in their own business
        - Prevents cross-business user deletion
        """

        if not self.request.user.is_superuser and self.request.user.role != 'admin':
            raise PermissionDenied("You don't have permission to delete users")

        if not self.request.user.is_superuser and instance.business_id != self.request.user.business_id:
            raise PermissionDenied("You can't delete users outside your business")

        instance.delete()
