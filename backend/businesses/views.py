from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import Business, User
from .serializers import BusinessSerializer, UserSerializer, RegisterSerializer, LoginSerializer, ChangePasswordSerializer
from .email_service import generate_temporary_password, send_invitation_email, set_temporary_password_expiry
from .permissions import UserManagementPermission


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
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
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password (required for first-time users)"""
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        
        # Verify old password
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if temporary password has expired
        if user.temporary_password_expires and timezone.now() > user.temporary_password_expires:
            return Response({'error': 'Temporary password has expired. Please contact your administrator.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.password_change_required = False
        user.temporary_password_expires = None
        user.save()
        
        return Response({'message': 'Password changed successfully'})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Business.objects.all()
        return Business.objects.filter(id=self.request.user.business_id)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, UserManagementPermission]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        if self.request.user.role == 'admin':
            return User.objects.filter(business=self.request.user.business)
        return User.objects.filter(id=self.request.user.id)

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            # superusers may create any user (respect incoming business if provided)
            user = serializer.save()
        else:
            if self.request.user.role != 'admin':
                raise PermissionDenied("You don't have permission to create users")

            # Force business isolation server-side (ignore any business sent by client)
            user = serializer.save(business=self.request.user.business)
        
        # Generate temporary password
        temp_password = generate_temporary_password()
        
        # Create user with temporary password
        user.set_password(temp_password)
        
        # Set password change requirement and expiry
        set_temporary_password_expiry(user)
        
        # Send invitation email
        email_sent = send_invitation_email(user, temp_password, self.request.user)
        
        if not email_sent:
            # Log the error but don't fail the user creation
            print(f"Warning: Failed to send invitation email to {user.email}")
        
        return user

    def perform_update(self, serializer):
        # Only admins/superusers can update users via this viewset.
        if not self.request.user.is_superuser and self.request.user.role != 'admin':
            raise PermissionDenied("You don't have permission to update users")

        if self.request.user.is_superuser:
            serializer.save()
            return

        # Admin can update users, but cannot move users across businesses.
        serializer.save(business=self.request.user.business)

    def perform_destroy(self, instance):
        # Only admins/superusers can delete users.
        if not self.request.user.is_superuser and self.request.user.role != 'admin':
            raise PermissionDenied("You don't have permission to delete users")

        # Admin can only delete users in their own business
        if not self.request.user.is_superuser and instance.business_id != self.request.user.business_id:
            raise PermissionDenied("You can't delete users outside your business")

        instance.delete()
