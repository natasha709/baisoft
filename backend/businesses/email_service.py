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
    """Send invitation email to new user with temporary password using a professional template"""
    subject = f'Welcome to {user.business.name} - Product Marketplace'
    
    login_url = "http://localhost:3000/login"
    support_email = invited_by.email
    current_year = timezone.now().year
    
    # Plain text version
    text_message = f"""
Hello {user.first_name} {user.last_name},

You have been invited to join {user.business.name} on the Product Marketplace platform by {invited_by.first_name} {invited_by.last_name}.

Your account has been created with the following details:

Email: {user.email}
Role: {user.get_role_display()}
Temporary Password: {temporary_password}

IMPORTANT: This temporary password will expire in 7 days and must be changed on your first login.

To get started:
1. Visit: {login_url}
2. Login with your email and temporary password
3. You will be prompted to create your own secure password

Best regards,
Product Marketplace Team
    """
    
    # HTML version
    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Product Marketplace</title>
    <style>
        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333333;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
            background-color: #f4f6f8;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            overflow: hidden;
        }}
        .header {{
            background-color: #2F80ED;
            padding: 30px 40px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            color: #ffffff;
            font-size: 24px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        .content {{
            padding: 40px;
        }}
        .greeting {{
            font-size: 18px;
            margin-bottom: 20px;
            color: #1a1f36;
        }}
        .info-box {{
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 20px;
            margin: 25px 0;
        }}
        .info-item {{
            margin-bottom: 10px;
            font-size: 14px;
        }}
        .info-label {{
            font-weight: 600;
            color: #64748b;
            display: inline-block;
            width: 80px;
        }}
        .password-display {{
            background: #ffffff;
            border: 1px dashed #cbd5e1;
            padding: 10px;
            margin-top: 15px;
            text-align: center;
            font-family: monospace;
            font-size: 18px;
            letter-spacing: 2px;
            color: #2F80ED;
            font-weight: bold;
            border-radius: 4px;
        }}
        .expiry-note {{
            font-size: 12px;
            color: #ef4444;
            margin-top: 5px;
            text-align: center;
        }}
        .button-container {{
            text-align: center;
            margin: 35px 0;
        }}
        .button {{
            display: inline-block;
            padding: 14px 30px;
            background-color: #2F80ED;
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 16px;
            box-shadow: 0 2px 4px rgba(47, 128, 237, 0.2);
            transition: background-color 0.2s;
        }}
        .button:hover {{
            background-color: #2563eb;
        }}
        .footer {{
            background-color: #f8fafc;
            padding: 20px 40px;
            text-align: center;
            border-top: 1px solid #e2e8f0;
            font-size: 12px;
            color: #94a3b8;
        }}
        .footer a {{
            color: #64748b;
            text-decoration: none;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Product Marketplace</h1>
        </div>
        <div class="content">
            <h2 class="greeting">Hello {user.first_name},</h2>
            
            <p>You have been invited to join <strong>{user.business.name}</strong> on the Product Marketplace platform.</p>
            <p>Your account has been created for you. Please use the credentials below to log in for the first time.</p>
            
            <div class="info-box">
                <div class="info-item">
                    <span class="info-label">Email:</span>
                    <span>{user.email}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Role:</span>
                    <span>{user.get_role_display()}</span>
                </div>
                
                <div class="password-display">
                    {temporary_password}
                </div>
                <div class="expiry-note">
                    ⚠️ Temporary password expires in 7 days
                </div>
            </div>
            
            <div class="button-container">
                <a href="{login_url}" class="button">Access Your Dashboard</a>
            </div>
        </div>
        <div class="footer">
            <p>This invitation was sent by {invited_by.first_name} {invited_by.last_name} ({invited_by.email}).</p>
            <p>
                Product Marketplace Inc.<br>
                &copy; {current_year} All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
    """
    
    try:
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
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
