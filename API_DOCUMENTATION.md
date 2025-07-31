# FilmGozin API Documentation

## Authentication Endpoints

### 1. User Signup

**Endpoint:** `POST /api/user/signup/`

**Description:** Register a new user account with email verification.

**Request Body:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123!",
    "password_repeat": "SecurePassword123!"
}
```

**Response (201 Created):**
```json
{
    "message": "User registered successfully. Please check your email to verify your account.",
    "user": {
        "id": 1,
        "username": "john_doe",
        "phone_number": null,
        "email": "john@example.com",
        "is_phone_verified": false,
        "is_email_verified": false
    }
}
```

**Validation Rules:**
- Username must be unique
- Email must be unique and valid format
- Password must meet Django's password validation requirements
- Password repeat must match password

### 2. User Login

**Endpoint:** `POST /api/user/login/`

**Description:** Authenticate user and return access token.

**Request Body:**
```json
{
    "email": "john@example.com",
    "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "john_doe",
        "phone_number": null,
        "email": "john@example.com",
        "is_phone_verified": false,
        "is_email_verified": false
    },
    "token": "your-auth-token-here"
}
```

**Error Response (400 Bad Request):**
```json
{
    "non_field_errors": ["Invalid email or password"]
}
```

### 3. Email Verification

**Endpoint:** `POST /api/user/verify-email/`

**Description:** Verify user's email address using token from email.

**Request Body:**
```json
{
    "token": "verification-token-from-email"
}
```

**Response (200 OK):**
```json
{
    "message": "Email verified successfully",
    "user": {
        "id": 1,
        "username": "john_doe",
        "phone_number": null,
        "email": "john@example.com",
        "is_phone_verified": false,
        "is_email_verified": true
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "Invalid or expired verification token"
}
```

### 4. Resend Verification Email

**Endpoint:** `POST /api/user/resend-verification/`

**Description:** Resend email verification link to user.

**Headers:** `Authorization: Token your-auth-token-here`

**Response (200 OK):**
```json
{
    "message": "Verification email sent successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "Email is already verified"
}
```

## Phone Verification Endpoints

### 5. Request Phone Number OTP

**Endpoint:** `POST /api/user/request-phonenumber-otp/`

**Description:** Request OTP for phone number verification.

**Request Body:**
```json
{
    "phone_number": "+1234567890"
}
```

**Response (200 OK):**
```json
{
    "message": "OTP sent successfully"
}
```

### 6. Verify Phone Number

**Endpoint:** `POST /api/user/verify-phonenumber/`

**Description:** Verify phone number using OTP.

**Request Body:**
```json
{
    "phone_number": "+1234567890",
    "code": "123456"
}
```

**Response (200 OK):**
```json
{
    "message": "Phone number verified successfully",
    "user": {
        "id": 1,
        "username": "john_doe",
        "phone_number": "+1234567890",
        "email": "john@example.com",
        "is_phone_verified": true,
        "is_email_verified": false
    },
    "token": "your-auth-token-here"
}
```

## Authentication

Most endpoints require authentication using Token Authentication. Include the token in the request headers:

```
Authorization: Token your-auth-token-here
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Email Verification Process

1. User signs up with email and password
2. System sends verification email with unique token
3. User clicks link in email or submits token via API
4. System verifies token and marks email as verified
5. User can now access protected features

## Security Features

- Passwords are hashed using Django's secure hashing
- Email verification tokens expire after 24 hours
- Tokens are unique and randomly generated
- All sensitive operations require authentication
- Password validation follows Django's security standards

## Testing

Run the comprehensive test suite to verify all functionality:

```bash
# Run all tests
python manage.py test --settings=test_settings

# Run only user app tests
python manage.py test user.tests --settings=test_settings

# Run specific test class
python manage.py test user.tests.AuthenticationAPITest --settings=test_settings
```

The test suite includes 22 test cases covering:
- User model functionality
- Authentication API endpoints
- Email verification process
- Profile creation
- Error handling and validation
- Phone number verification 