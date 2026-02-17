import secrets
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


def generate_temporary_password(length=12):
    """Generate a secure temporary password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password


def send_invitation_email(user, temporary_password, invited_by):
    """Send invitation email to new user with temporary password"""
    subject = f'Welcome to {user.business.name} - Product Marketplace'
    
    message = f"""
Hello {user.first_name} {user.last_name},

You have been invited to join {user.business.name} on the Product Marketplace platform by {invited_by.first_name} {invited_by.last_name}.

Your account has been created with the following details:

Email: {user.email}
Role: {user.get_role_display()}
Temporary Password: {temporary_password}

IMPORTANT: This temporary password will expire in 7 days and must be changed on your first login.

To get started:
1. Visit: http://localhost:3000/login
2. Login with your email and temporary password
3. You will be prompted to create your own secure password
4. After setting your password, you'll be redirected to your dashboard

Your Role: {user.get_role_display()}
{get_role_description(user.role)}

If you have any questions, please contact {invited_by.email}.

Best regards,
Product Marketplace Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False


def get_role_description(role):
    """Get description of what each role can do"""
    descriptions = {
        'admin': 'As an Admin, you have full access to manage products, users, and all system features.',
        'editor': 'As an Editor, you can create and edit products, but cannot approve or delete them.',
        'approver': 'As an Approver, you can approve products for publication, but cannot create or edit them.',
        'viewer': 'As a Viewer, you have read-only access to view products and information.',
    }
    return descriptions.get(role, '')


def set_temporary_password_expiry(user):
    """Set expiry date for temporary password (7 days from now)"""
    user.temporary_password_expires = timezone.now() + timedelta(days=7)
    user.invitation_sent_at = timezone.now()
    user.password_change_required = True
    user.save()
