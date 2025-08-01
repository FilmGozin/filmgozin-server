# FilmGozin API - Postman Guide

## Setup Instructions

### 1. Import Postman Collection
1. Open Postman
2. Click **Import** button
3. Create a new collection called "FilmGozin API"
4. Add the following requests

## Authentication Setup

### Step 1: Login Request
**Method**: POST  
**URL**: `https://filmgozin-server.liara.run/api/user/login/`  
**Headers**: 
- Content-Type: application/json

**Body** (raw JSON):
```json
{
    "email": "your-email@example.com",
    "password": "your-password"
}
```

**Response**:
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "your-username",
        "phone_number": null,
        "email": "your-email@example.com",
        "is_phone_verified": false,
        "is_email_verified": true
    },
    "token": "your-auth-token-here"
}
```

### Step 2: Set Authentication Token
**Option A: Manual Header**
- Add header: `Authorization: Token your-auth-token-here`

**Option B: Postman Authorization Tab**
1. Go to **Authorization** tab
2. Select **Type**: `Token`
3. Paste your token in the **Token** field

**Option C: Environment Variable**
1. Create environment variable `auth_token`
2. Set value to your token
3. Use `{{auth_token}}` in Authorization header

## API Endpoints

### User Management

#### 1. User Signup
**Method**: POST  
**URL**: `https://filmgozin-server.liara.run/api/user/signup/`  
**Body**:
```json
{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123",
    "password_repeat": "password123"
}
```

#### 2. Get User Profile
**Method**: GET  
**URL**: `https://filmgozin-server.liara.run/api/user/profile/`  
**Auth**: Required (Token)

#### 3. Update User Profile
**Method**: PUT  
**URL**: `https://filmgozin-server.liara.run/api/user/profile/`  
**Auth**: Required (Token)  
**Body**:
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "bio": "My bio",
    "city": "Tehran",
    "gender": "M"
}
```

#### 4. Contact Message
**Method**: POST  
**URL**: `https://filmgozin-server.liara.run/api/user/contact/`  
**Body**:
```json
{
    "name": "Your Name",
    "email": "your-email@example.com",
    "message": "Your message here"
}
```

### Movie Management

#### 1. Movie Search
**Method**: GET  
**URL**: `https://filmgozin-server.liara.run/api/movie/search/?q=inception`  
**Query Parameters**:
- `q`: Search query (required)
- `page`: Page number (optional)
- `page_size`: Items per page (optional)

#### 2. Get Movie Details
**Method**: GET  
**URL**: `https://filmgozin-server.liara.run/api/movie/movies/1/`

#### 3. Get Genres
**Method**: GET  
**URL**: `https://filmgozin-server.liara.run/api/movie/genres/`

#### 4. Similar Movies
**Method**: POST  
**URL**: `https://filmgozin-server.liara.run/api/movie/similar/`  
**Body**:
```json
{
    "movie_name": "Inception",
    "limit": 10
}
```

#### 5. Get Recommendation Questions
**Method**: GET  
**URL**: `https://filmgozin-server.liara.run/api/movie/questions/`  
**Query Parameters**:
- `lang`: Language (en/fa)

#### 6. Submit User Answers
**Method**: POST  
**URL**: `https://filmgozin-server.liara.run/api/movie/answers/`  
**Auth**: Required (Token)  
**Body**:
```json
[
    {
        "question": 1,
        "answer_value": ["action", "drama"]
    },
    {
        "question": 2,
        "answer_value": [2010, 2020]
    }
]
```

#### 7. Get Recommendations
**Method**: GET  
**URL**: `https://filmgozin-server.liara.run/api/movie/recommendations/`  
**Auth**: Required (Token)

#### 8. Like Movie
**Method**: POST  
**URL**: `https://filmgozin-server.liara.run/api/movie/movies/1/like/`  
**Auth**: Required (Token)

#### 9. Add to Watchlist
**Method**: POST  
**URL**: `https://filmgozin-server.liara.run/api/movie/movies/1/watchlist/`  
**Auth**: Required (Token)

#### 10. Rate Movie
**Method**: POST  
**URL**: `https://filmgozin-server.liara.run/api/movie/movies/1/rate/`  
**Auth**: Required (Token)  
**Body**:
```json
{
    "rating": 8.5
}
```

#### 11. Get User Preferences
**Method**: GET  
**URL**: `https://filmgozin-server.liara.run/api/movie/preferences/`  
**Auth**: Required (Token)

## Common Response Formats

### Success Response
```json
{
    "message": "Operation successful",
    "data": {...},
    "count": 10,
    "results": [...]
}
```

### Error Response
```json
{
    "error": "Error title",
    "details": "Detailed error message"
}
```

### Paginated Response
```json
{
    "count": 100,
    "next": "https://api.example.com/endpoint/?page=2",
    "previous": null,
    "results": [...]
}
```

## Testing Checklist

### ✅ Authentication
- [ ] Login request works
- [ ] Token is received
- [ ] Token is properly set in headers

### ✅ User Endpoints
- [ ] Signup works
- [ ] Profile retrieval works
- [ ] Profile update works
- [ ] Contact message works

### ✅ Movie Endpoints
- [ ] Movie search works
- [ ] Movie details work
- [ ] Genre list works
- [ ] Similar movies work
- [ ] Recommendations work
- [ ] User preferences work

### ✅ Error Handling
- [ ] Invalid credentials return proper error
- [ ] Missing required fields return proper error
- [ ] Invalid data formats return proper error

## Troubleshooting

### Common Issues

#### 1. 401 Unauthorized
- Check if token is properly set
- Verify token hasn't expired
- Ensure Authorization header format is correct

#### 2. 400 Bad Request
- Check request body format
- Verify all required fields are present
- Check data types (e.g., rating should be number)

#### 3. 500 Internal Server Error
- Check server logs
- Verify database migrations are applied
- Contact support if issue persists

#### 4. Contact Message Error
- Ensure phone_number field is removed from database
- Run migrations: `python3 manage.py migrate user`

### Environment Variables
Create a Postman environment with these variables:
- `base_url`: `https://filmgozin-server.liara.run`
- `auth_token`: Your authentication token
- `user_email`: Your email for testing
- `user_password`: Your password for testing

Then use `{{base_url}}/api/endpoint` in your URLs.

## Sample Postman Collection

You can create a collection with these requests:

1. **Login** - POST {{base_url}}/api/user/login/
2. **Signup** - POST {{base_url}}/api/user/signup/
3. **Get Profile** - GET {{base_url}}/api/user/profile/
4. **Update Profile** - PUT {{base_url}}/api/user/profile/
5. **Contact Message** - POST {{base_url}}/api/user/contact/
6. **Movie Search** - GET {{base_url}}/api/movie/search/
7. **Movie Details** - GET {{base_url}}/api/movie/movies/1/
8. **Get Genres** - GET {{base_url}}/api/movie/genres/
9. **Similar Movies** - POST {{base_url}}/api/movie/similar/
10. **Get Questions** - GET {{base_url}}/api/movie/questions/
11. **Submit Answers** - POST {{base_url}}/api/movie/answers/
12. **Get Recommendations** - GET {{base_url}}/api/movie/recommendations/
13. **Like Movie** - POST {{base_url}}/api/movie/movies/1/like/
14. **Add to Watchlist** - POST {{base_url}}/api/movie/movies/1/watchlist/
15. **Rate Movie** - POST {{base_url}}/api/movie/movies/1/rate/
16. **Get Preferences** - GET {{base_url}}/api/movie/preferences/ 