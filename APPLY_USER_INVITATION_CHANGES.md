# Apply User Invitation Workflow Changes

## Backend Changes

### 1. Create Database Migrations

```bash
cd backend
python manage.py makemigrations
```

### 2. Apply Migrations

```bash
python manage.py migrate
```

### 3. Update Your .env File

Add these email configuration settings to your `backend/.env` file:

```env
# Email Configuration (for development, emails will print to console)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@productmarketplace.com
```

**For Development:** Keep `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` - emails will print to your terminal instead of being sent.

**For Production:** Change to `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend` and configure real SMTP credentials.

### 4. Restart Backend Server

```bash
python manage.py runserver
```

## Frontend Changes

### 1. Restart Frontend Server

```bash
cd frontend
npm run dev
```

## Testing the New Workflow

### 1. Login as Admin

Go to http://localhost:3000/login and login with your admin account.

### 2. Create a New User

1. Click "Manage Users"
2. Click "Create User"
3. Fill in:
   - Email: test@example.com
   - First Name: Test
   - Last Name: User
   - Role: Editor
4. Click "Send Invitation"

### 3. Check Console for Email

Look at your backend terminal - you'll see the invitation email printed with the temporary password.

Example output:
```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Welcome to My Company - Product Marketplace
From: noreply@productmarketplace.com
To: test@example.com

Hello Test User,

You have been invited to join My Company...

Temporary Password: Abc123!@#xyz
```

### 4. Login with Temporary Password

1. Logout from admin account
2. Go to http://localhost:3000/login
3. Login with:
   - Email: test@example.com
   - Password: [the temporary password from email]

### 5. Change Password

You'll be automatically redirected to the password change page:
1. Enter the temporary password
2. Enter your new password (at least 8 characters)
3. Confirm your new password
4. Click "Change Password"

### 6. Access Dashboard

After changing password, you'll be redirected to the dashboard based on your role.

## Features Implemented

✅ Admin creates users without passwords
✅ System generates secure temporary passwords
✅ Invitation emails sent to users (console for dev)
✅ Temporary passwords expire in 7 days
✅ Users must change password on first login
✅ Password strength indicator
✅ Role-based dashboard routing
✅ Cannot bypass password change requirement

## Email Configuration for Production

To send real emails in production:

1. **Gmail Setup:**
   - Enable 2-factor authentication
   - Generate an App Password: https://myaccount.google.com/apppasswords
   - Use the app password in EMAIL_HOST_PASSWORD

2. **Update .env:**
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

3. **Other SMTP Providers:**
   - SendGrid
   - Mailgun
   - AWS SES
   - Postmark

## Troubleshooting

### Emails Not Showing in Console
- Make sure `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`
- Check your backend terminal output

### Password Change Not Working
- Check that migrations were applied
- Verify user has `password_change_required=True`

### Can't Access Dashboard
- Make sure you changed your password
- Check that `password_change_required=False` after change

### Migration Errors
If you get migration conflicts:
```bash
# Delete database and start fresh
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## Next Steps

1. Test the complete workflow
2. Configure real email for production
3. Customize email templates if needed
4. Add resend invitation feature (future enhancement)
