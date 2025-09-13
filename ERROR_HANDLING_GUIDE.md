# Error Handling Guide - FilmGozin API

## Error Response Format

All error responses now follow this consistent format:

```json
{
  "error": "Human-readable error title",
  "details": "Detailed explanation or validation errors"
}
```

## HTTP Status Codes

The API uses appropriate HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data or validation errors
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side errors
- `503 Service Unavailable`: External services unavailable (email, SMS, cache)

## Authentication Endpoints Error Handling

### 1. User Signup (`POST /api/user/signup/`)

**Validation Errors (400 Bad Request):**

```json
{
  "error": "Validation failed",
  "details": {
    "username": ["Username is required."],
    "email": ["Please enter a valid email address."],
    "password": ["This password is too short."],
    "password_repeat": [
      "Passwords don't match. Please make sure both passwords are identical."
    ]
  }
}
```

**Duplicate User Errors (400 Bad Request):**

```json
{
  "error": "Username already exists",
  "details": "This username is already taken. Please choose a different username."
}
```

```json
{
  "error": "Email already exists",
  "details": "A user with this email address already exists. Please use a different email or try logging in."
}
```

**Database Constraint Errors (400 Bad Request):**

```json
{
  "error": "Database integrity error",
  "details": "User creation failed due to database constraints. Please check your input data."
}
```

**Database Errors (500 Internal Server Error):**

```json
{
  "error": "Database error",
  "details": "Failed to create user due to database issues. Please try again later."
}
```

**Profile Creation Errors (500 Internal Server Error):**

```json
{
  "error": "Failed to create user profile",
  "details": "Specific error message"
}
```

### 2. User Login (`POST /api/user/login/`)

**Invalid Credentials (400 Bad Request):**

```json
{
  "error": "Login failed",
  "details": {
    "non_field_errors": [
      "Invalid email address or password. Please check your credentials and try again."
    ]
  }
}
```

**Disabled Account (400 Bad Request):**

```json
{
  "error": "Login failed",
  "details": {
    "non_field_errors": [
      "Your account has been disabled. Please contact support for assistance."
    ]
  }
}
```

**Authentication Token Errors (500 Internal Server Error):**

```json
{
  "error": "Authentication failed",
  "details": "Failed to create authentication token"
}
```

### 3. Email Verification (`POST /api/user/verify-email/`)

**Invalid Token (400 Bad Request):**

```json
{
  "error": "Invalid or expired verification token",
  "details": "The verification token is not valid or has expired"
}
```

**Invalid Token Format (400 Bad Request):**

```json
{
  "error": "Invalid token format",
  "details": {
    "token": ["Verification token is required."]
  }
}
```

### 4. Resend Verification Email (`POST /api/user/resend-verification/`)

**Already Verified (400 Bad Request):**

```json
{
  "error": "Email is already verified",
  "details": "No verification email needed"
}
```

**Email Service Unavailable (503 Service Unavailable):**

```json
{
  "error": "Failed to send verification email",
  "details": "Email service is currently unavailable. Please try again later."
}
```

## Phone Verification Endpoints Error Handling

### 5. Request Phone OTP (`POST /api/user/request-phonenumber-otp/`)

**Invalid Phone Number (400 Bad Request):**

```json
{
  "error": "Invalid phone number",
  "details": {
    "phone_number": ["Please enter a valid phone number."]
  }
}
```

**Cache Service Unavailable (503 Service Unavailable):**

```json
{
  "error": "Cache service unavailable",
  "details": "Failed to store OTP code"
}
```

**SMS Service Unavailable (503 Service Unavailable):**

```json
{
  "error": "Failed to send OTP",
  "details": "SMS service is currently unavailable. Please try again later."
}
```

### 6. Verify Phone Number (`POST /api/user/verify-phonenumber/`)

**Invalid OTP (400 Bad Request):**

```json
{
  "error": "Invalid OTP",
  "details": "The provided OTP code is incorrect"
}
```

**Expired OTP (400 Bad Request):**

```json
{
  "error": "OTP expired or invalid",
  "details": "The OTP code has expired or was never sent"
}
```

**Phone Number Already Exists (400 Bad Request):**

```json
{
  "error": "Phone number already exists",
  "details": "This phone number is already registered with another account"
}
```

**Username Conflict (400 Bad Request):**

```json
{
  "error": "Username conflict",
  "details": "Unable to create unique username for this phone number"
}
```

**Database Errors (500 Internal Server Error):**

```json
{
  "error": "Database error",
  "details": "Failed to process verification due to database issues"
}
```

## Profile Management Error Handling

### Profile Update (`PUT/PATCH /api/user/profile/`)

**Profile Not Found (404 Not Found):**

```json
{
  "error": "Profile not found",
  "details": "User profile not found"
}
```

**Validation Errors (400 Bad Request):**

```json
{
  "error": "Validation failed",
  "details": {
    "email": ["Please enter a valid email address."],
    "first_name": ["First name cannot exceed 100 characters."]
  }
}
```

**Update Failed (500 Internal Server Error):**

```json
{
  "error": "Profile update failed",
  "details": "Specific error message"
}
```

## Contact Form Error Handling

### Contact Message (`POST /api/user/contact/`)

**Validation Errors (400 Bad Request):**

```json
{
  "error": "Invalid contact message data",
  "details": {
    "name": ["Name is required."],
    "email": ["Please enter a valid email address."],
    "message": ["Message is required."]
  }
}
```

**Save Failed (500 Internal Server Error):**

```json
{
  "error": "Failed to save contact message",
  "details": "Specific error message"
}
```

## Questionnaire Error Handling

### Questionnaire Operations (`GET/POST/DELETE /api/user/questionnaire/`)

**Profile Not Found (404 Not Found):**

```json
{
  "error": "Profile not found",
  "details": "User profile does not exist"
}
```

**Invalid Answers Format (400 Bad Request):**

```json
{
  "error": "Invalid answers format",
  "details": "Answers must be a JSON object"
}
```

**Operation Failed (500 Internal Server Error):**

```json
{
  "error": "Failed to save questionnaire",
  "details": "Specific error message"
}
```

## Field-Level Error Messages

### User Signup Fields

- **Username**: Required, unique, max 150 characters
- **Email**: Required, valid format, unique
- **Password**: Required, meets Django validation requirements
- **Password Repeat**: Must match password exactly

### User Login Fields

- **Email**: Required, valid format
- **Password**: Required

### Phone Verification Fields

- **Phone Number**: Required, valid international format
- **OTP Code**: Required, exactly 6 characters

### Profile Fields

- **Email**: Valid format (optional)
- **First Name**: Max 100 characters (optional)
- **Last Name**: Max 100 characters (optional)

### Contact Form Fields

- **Name**: Required, max 100 characters
- **Email**: Valid format (optional)
- **Message**: Required

## Testing Error Handling

The error handling system is thoroughly tested with 22 test cases covering:

- Validation errors
- Database errors
- Service unavailability
- Authentication failures
- Profile management errors
- Contact form validation
- Questionnaire operations

Run tests with:

```bash
python manage.py test user.tests --settings=test_settings
```

### Database Error Fix Verification

To verify that the database errors are fixed, run:

```bash
python3 test_fixes.py
```

This will test both signup and phone verification endpoints to ensure they no longer return database errors.

## Best Practices

1. **Always check the `error` field** for the error type
2. **Use the `details` field** for specific error information
3. **Handle 503 errors** for service unavailability gracefully
4. **Display user-friendly messages** based on error types
5. **Log detailed errors** on the server side for debugging

## Migration Notes

If you're updating from the previous version:

1. Update your error handling code to check for the new `error` and `details` fields
2. Replace direct field access with `response.data['details'][field_name]`
3. Handle the new 503 status code for service unavailability
4. Update any hardcoded error message checks
5. **Run migrations** to ensure database schema is up to date:
   ```bash
   python manage.py migrate --settings=test_settings
   ```

## Database Schema Requirements

**Important**: Ensure all migrations are applied before testing:

```bash
python manage.py migrate --settings=test_settings
```

The User model now properly handles:

- Phone-only users with placeholder emails
- Unique constraints for username, email, and phone number
- Proper validation for required fields
- Better error handling for database constraints
