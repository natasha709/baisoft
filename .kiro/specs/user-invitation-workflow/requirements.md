# User Invitation Workflow - Requirements

## Feature Overview
Implement a secure user invitation system where admins can invite users without setting passwords. New users receive an email with a temporary password, login, and set their own password before accessing their role-specific dashboard.

## User Stories

### 1. Admin Invites User
**As an** admin  
**I want to** invite users to my business without creating passwords for them  
**So that** users can securely set their own passwords

**Acceptance Criteria:**
- Admin can create user with email, name, and role only (no password field)
- System generates a secure temporary password automatically
- Temporary password is sent to user's email
- User account is created in "pending" state until password is changed
- Admin sees confirmation that invitation was sent

### 2. User Receives Invitation Email
**As a** new user  
**I want to** receive an email with my temporary credentials  
**So that** I can access the system for the first time

**Acceptance Criteria:**
- Email contains temporary password
- Email contains login link to the application
- Email explains that password must be changed on first login
- Email is professional and branded
- Email includes business name and admin contact

### 3. User First Login with Temporary Password
**As a** new user  
**I want to** login with my temporary password  
**So that** I can set my own secure password

**Acceptance Criteria:**
- User can login with email and temporary password
- After successful login, user is immediately redirected to password change page
- User cannot access any other pages until password is changed
- Temporary password expires after 7 days
- Clear instructions are shown on password change page

### 4. User Sets New Password
**As a** new user  
**I want to** set my own password  
**So that** I have secure credentials I control

**Acceptance Criteria:**
- Password must be at least 8 characters
- Password must be different from temporary password
- User must confirm password (enter twice)
- Password strength indicator is shown
- Clear validation messages for password requirements
- After setting password, temporary password is invalidated

### 5. User Accesses Role-Specific Dashboard
**As a** user with a new password  
**I want to** be redirected to my appropriate dashboard  
**So that** I can start using the system based on my role

**Acceptance Criteria:**
- Admin role → Full dashboard with user management
- Editor role → Dashboard with product create/edit
- Approver role → Dashboard with product approval
- Viewer role → Dashboard with read-only access
- User sees welcome message with their role explained
- User account status changes from "pending" to "active"

## Technical Requirements

### Backend Changes
1. **User Model Updates:**
   - Add `password_change_required` boolean field (default: True for invited users)
   - Add `temporary_password_expires` datetime field
   - Add `invitation_sent_at` datetime field

2. **Email Service:**
   - Configure Django email backend (SMTP)
   - Create email templates for invitation
   - Implement send_invitation_email function
   - Handle email sending errors gracefully

3. **API Endpoints:**
   - `POST /api/auth/users/` - Modified to not require password, generate temp password
   - `POST /api/auth/change-password/` - New endpoint for password change
   - `GET /api/auth/me/` - Include password_change_required in response

4. **Authentication Middleware:**
   - Check if password change is required after login
   - Block access to other endpoints if password change required

### Frontend Changes
1. **User Creation Form:**
   - Remove password field
   - Add email preview/confirmation
   - Show success message with "Invitation sent"

2. **Password Change Page:**
   - New page at `/change-password`
   - Password strength indicator
   - Validation messages
   - Cannot be bypassed

3. **Login Flow:**
   - After login, check if password change required
   - Redirect to `/change-password` if needed
   - Otherwise redirect to role-specific dashboard

4. **Role-Based Routing:**
   - Implement role-based dashboard routing
   - Different landing pages per role

## Security Considerations
- Temporary passwords must be cryptographically secure (random)
- Temporary passwords expire after 7 days
- Temporary passwords are one-time use
- Email sending failures are logged
- Rate limiting on password change attempts
- HTTPS required for all authentication flows

## Email Configuration
- SMTP server configuration in .env
- Email templates with company branding
- Fallback for email sending failures
- Email delivery confirmation

## Edge Cases
1. User never receives email → Admin can resend invitation
2. Temporary password expires → User requests new invitation
3. User forgets new password → Standard password reset flow
4. Email bounces → Admin is notified
5. User tries to access system before changing password → Blocked and redirected

## Dependencies
- Django email backend configuration
- SMTP server credentials
- Email template system
- Frontend routing guards

## Success Metrics
- 100% of invited users receive email within 1 minute
- 90% of users successfully change password on first attempt
- 0% of users can bypass password change requirement
- All users land on correct role-specific dashboard

## Out of Scope (Future Enhancements)
- Custom email templates per business
- SMS-based invitations
- Multi-factor authentication
- Password complexity rules configuration
- Bulk user invitations
- User self-registration with approval

## Notes
- This is a critical security feature
- Email delivery must be reliable
- User experience should be smooth and clear
- Admin should have visibility into invitation status
