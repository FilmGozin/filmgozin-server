# FilmGozin Server

A Django REST API server for the movie recommendation system.

## Features

- User authentication: Signup, Login
- User profiles: User Preferences, Email verification, Phone number verification via SMS
- Movie recommendations based on: similar movie name or questionnare
- Blog system

## Authentication Endpoints

### User Signup

- **URL**: `/api/user/signup/`
- **Method**: `POST`
- **Fields**:
  - `username` (required): Unique username
  - `email` (required): Valid email address
  - `password` (required): Strong password
  - `password_repeat` (required): Must match password
- **Response**: User data sent

### User Login

- **URL**: `/api/user/login/`
- **Method**: `POST`
- **Fields**:
  - `email` (required): User's email
  - `password` (required): User's password
- **Response**: User data and authentication token

### Email Verification

- **URL**: `/api/user/verify-email/`
- **Method**: `POST`
- **Fields**:
  - `token` (required): Verification token from email
- **Response**: Confirmation message

### Resend Verification Email

- **URL**: `/api/user/request-verification/`
- **Method**: `POST`
- **Authentication**: Required
- **Response**: Confirmation message

## Existing Endpoints

### Phone Verification

- **Request OTP**: `/api/user/request-phonenumber-otp/`
- **Verify OTP**: `/api/user/verify-phonenumber/`

### User Profile

- **Profile**: `/api/user/profile/`
- **Contact**: `/api/user/contact/`

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Configure email settings in `filmgozin_server/settings.py`:

   ```python
   EMAIL_HOST_USER = 'your-email@gmail.com'
   EMAIL_HOST_PASSWORD = 'your-app-password'
   FRONTEND_URL = 'https://your-frontend-url.com'
   ```

3. Run migrations:

   ```bash
   python manage.py migrate
   ```

4. Start the server:
   ```bash
   python manage.py runserver
   ```

## Testing

Run the test suite to verify all functionality:

```bash
# Run all tests
python manage.py test --settings=test_settings

# Run only user app tests
python manage.py test user.tests --settings=test_settings

# Run specific test class
python manage.py test user.tests.AuthenticationAPITest --settings=test_settings
```

The test suite includes comprehensive tests for:

- User model functionality
- Authentication API endpoints
- Email verification process
- Profile creation
- Error handling and validation

## Email Configuration

The application uses Django's email backend to send verification emails. Configure your email provider settings in `settings.py`:

- For Gmail: Use SMTP with TLS
- For other providers: Adjust host, port, and security settings accordingly

## Security Notes

- Passwords are validated using Django's built-in password validators
- Email verification tokens expire after 24 hours
- Authentication uses Django REST Framework's TokenAuthentication
- All sensitive endpoints require authentication except signup, login
