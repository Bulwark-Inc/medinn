# Ecommerce Backend - Accounts API Documentation

## Overview
This section of the API handles user authentication, registration, email verification, and password management. It uses JWT (JSON Web Tokens) for secure authentication with refresh tokens stored in HTTP-only cookies.

### Features:
- **User Registration**: Create new user accounts (customer or seller)
- **Login/Logout**: Secure authentication with JWT tokens
- **Token Refresh**: Automatic token renewal using refresh tokens
- **Email Verification**: Verify user email addresses with token-based system
- **Password Reset**: Forgot password functionality with secure token links
- **Current User**: Retrieve authenticated user information
- **Auto-generated Usernames**: Usernames are automatically created from first and last names

---

## API Endpoints

### 1. **User Registration**
- **Endpoint**: `POST /api/accounts/register/`
- **Description**: Create a new user account (customer or seller)
- **Authentication**: Not required
- **Request Body**:

```json
{
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_seller": false,
    "password": "SecurePassword123!",
    "password2": "SecurePassword123!"
}
```

**Fields**:
- `email`: User's email address (required, must be unique)
- `first_name`: User's first name (required)
- `last_name`: User's last name (required)
- `is_seller`: Boolean flag to indicate if user is a seller (optional, default: false)
- `password`: User's password (required, must meet validation requirements)
- `password2`: Password confirmation (required, must match password)

**Response**:

```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "message": "User registered successfully"
}
```

- **Success Status Code**: `201 Created`
- **Refresh Token**: Set in HTTP-only cookie named `refresh_token`
- **Email Verification**: A verification email is automatically sent to the user's email address

**Error Responses**:
- **400 Bad Request**: 
  - Passwords don't match
  - Email already exists
  - Password doesn't meet requirements
  - Missing required fields

**Notes**:
- Username is automatically generated from first name and last name (e.g., "johndoe", "johndoe-1234" if duplicate)
- User account is created but `email_verified` is set to `false` until verified
- Password must meet Django's password validation requirements (length, complexity, etc.)

---

### 2. **User Login**
- **Endpoint**: `POST /api/accounts/login/`
- **Description**: Authenticate a user and receive access tokens
- **Authentication**: Not required
- **Request Body**:

```json
{
    "email": "user@example.com",
    "password": "SecurePassword123!"
}
```

**Response**:

```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "message": "Login successful"
}
```

- **Success Status Code**: `200 OK`
- **Refresh Token**: Set in HTTP-only cookie named `refresh_token`

**Error Responses**:
- **400 Bad Request**:
  - Invalid email or password
  - Account is disabled
  - Email is not verified

**Cookie Information**:
- **Name**: `refresh_token`
- **Attributes**: HttpOnly, Secure (in production), SameSite=Lax
- **Purpose**: Used for refreshing access tokens without requiring re-login

---

### 3. **Refresh Access Token**
- **Endpoint**: `POST /api/accounts/token/refresh/`
- **Description**: Get a new access token using the refresh token stored in cookies
- **Authentication**: Not required (uses refresh token from cookie)
- **Request Body**: None (refresh token is read from cookies)

**Response**:

```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

- **Success Status Code**: `200 OK`

**Error Responses**:
- **400 Bad Request**: Refresh token missing from cookies
- **401 Unauthorized**: Invalid or expired refresh token

**Usage Note**: This endpoint should be called when the access token expires (typically every 5-15 minutes)

---

### 4. **User Logout**
- **Endpoint**: `POST /api/accounts/logout/`
- **Description**: Logout the current user and invalidate tokens
- **Authentication**: Required
- **Request Body**: None

**Response**:

```json
{
    "message": "Logged out successfully"
}
```

- **Success Status Code**: `200 OK`
- **Refresh Token**: Removed from cookies
- **Token Blacklisting**: Refresh token is added to blacklist (if SimpleJWT blacklist is enabled)

**Headers**:
```http
Authorization: Bearer <your-access-token>
```

---

### 5. **Get Current User**
- **Endpoint**: `GET /api/accounts/me/`
- **Description**: Retrieve information about the currently authenticated user
- **Authentication**: Required

**Response**:

```json
{
    "email": "user@example.com",
    "username": "johndoe",
    "email_verified": true
}
```

- **Success Status Code**: `200 OK`

**Error Responses**:
- **401 Unauthorized**: No valid access token provided

**Headers**:
```http
Authorization: Bearer <your-access-token>
```

---

### 6. **Verify Email**
- **Endpoint**: `POST /api/accounts/verify-email/`
- **Description**: Verify a user's email address using the token sent via email
- **Authentication**: Not required
- **Request Body**:

```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response**:

```json
{
    "message": "Email verified successfully"
}
```

- **Success Status Code**: `200 OK`

**Error Responses**:
- **400 Bad Request**: Invalid or expired token
- **404 Not Found**: User not found

**Flow**:
1. User registers and receives an email with a verification link
2. Link contains token: `https://yourfrontend.com/verify-email?token=...`
3. Frontend sends the token to this endpoint
4. User's `email_verified` flag is set to `true`

---

### 7. **Resend Verification Email**
- **Endpoint**: `POST /api/accounts/resend-email-verification/`
- **Description**: Resend the email verification link to a user
- **Authentication**: Not required
- **Request Body**:

```json
{
    "email": "user@example.com"
}
```

**Response**:

```json
{
    "detail": "Verification email resent successfully."
}
```

- **Success Status Code**: `200 OK`

**Error Responses**:
- **400 Bad Request**: 
  - Email is required
  - Email is already verified
- **404 Not Found**: User not found

---

### 8. **Forgot Password (Request Reset)**
- **Endpoint**: `POST /api/accounts/forgot-password/`
- **Description**: Request a password reset link via email
- **Authentication**: Not required
- **Request Body**:

```json
{
    "email": "user@example.com"
}
```

**Response**:

```json
{
    "detail": "Password reset email sent."
}
```

- **Success Status Code**: `200 OK`

**Error Responses**:
- **400 Bad Request**: Email is required
- **404 Not Found**: User not found

**Flow**:
1. User enters their email address
2. System sends email with reset link: `https://yourfrontend.com/reset-password?token=...`
3. Email contains a time-limited token

---

### 9. **Reset Password**
- **Endpoint**: `POST /api/accounts/reset-password/`
- **Description**: Reset user password using the token from the reset email
- **Authentication**: Not required
- **Request Body**:

```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "new_password": "NewSecurePassword123!"
}
```

**Response**:

```json
{
    "detail": "Password reset successfully."
}
```

- **Success Status Code**: `200 OK`

**Error Responses**:
- **400 Bad Request**: 
  - Token and new password are required
  - Invalid or expired token
- **404 Not Found**: User not found

**Notes**:
- Token expires after a set time (typically 1 hour)
- Password must meet Django's validation requirements

---

## Authentication Flow

### Registration & Login Flow

```
1. User Registration
   ├─> POST /api/accounts/register/
   ├─> Receive access token + refresh token (cookie)
   ├─> Receive verification email
   └─> User can access protected routes

2. Email Verification (Required for login)
   ├─> User clicks link in email
   ├─> POST /api/accounts/verify-email/
   └─> email_verified = true

3. User Login
   ├─> POST /api/accounts/login/
   ├─> Receive access token + refresh token (cookie)
   └─> User can access protected routes

4. Token Refresh (When access token expires)
   ├─> POST /api/accounts/token/refresh/
   ├─> Automatically uses refresh token from cookie
   └─> Receive new access token

5. User Logout
   ├─> POST /api/accounts/logout/
   ├─> Refresh token blacklisted
   └─> Refresh token removed from cookie
```

### Password Reset Flow

```
1. Forgot Password
   ├─> POST /api/accounts/forgot-password/
   └─> Receive reset email with token

2. Reset Password
   ├─> POST /api/accounts/reset-password/
   └─> Password updated, can now login
```

---

## Token Management

### Access Token
- **Type**: JWT Bearer Token
- **Lifespan**: Short-lived (typically 5-15 minutes)
- **Storage**: Stored in memory or localStorage by frontend
- **Usage**: Sent in `Authorization` header for protected endpoints

### Refresh Token
- **Type**: JWT Token
- **Lifespan**: Long-lived (typically 7-30 days)
- **Storage**: HTTP-only cookie (cannot be accessed by JavaScript)
- **Usage**: Automatically sent with requests to `/api/accounts/token/refresh/`
- **Security**: HttpOnly, Secure (production), SameSite=Lax

### Token Security Best Practices
1. Always use HTTPS in production
2. Store access tokens in memory or sessionStorage (not localStorage if possible)
3. Refresh tokens are automatically handled via HTTP-only cookies
4. Implement token refresh before expiration
5. Clear tokens on logout

---

## User Model

### Fields:
- **id**: Integer (Primary key)
- **email**: Email address (unique, used for login)
- **username**: Auto-generated from first_name and last_name (unique)
- **first_name**: User's first name
- **last_name**: User's last name
- **is_active**: Boolean (default: true) - Account status
- **is_staff**: Boolean (default: false) - Admin access
- **is_seller**: Boolean (default: false) - Seller account flag
- **email_verified**: Boolean (default: false) - Email verification status
- **date_joined**: DateTime (auto-generated) - Account creation date

### Username Generation:
- Automatically created from first_name and last_name
- Format: `firstnamelastname` (e.g., "johndoe")
- If duplicate exists, adds random 4-digit suffix (e.g., "johndoe-1234")
- All lowercase, no spaces

---

## Example Frontend Implementation

### 1. **User Registration**

```js
async function register(userData) {
    const response = await fetch('/api/accounts/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: userData.email,
            first_name: userData.firstName,
            last_name: userData.lastName,
            is_seller: userData.isSeller || false,
            password: userData.password,
            password2: userData.password2
        }),
        credentials: 'include' // Important for cookies
    });
    
    if (response.ok) {
        const data = await response.json();
        // Store access token
        localStorage.setItem('access_token', data.access);
        console.log('Registration successful! Check your email for verification.');
        return data;
    } else {
        const error = await response.json();
        console.error('Registration failed:', error);
        throw error;
    }
}
```

### 2. **User Login**

```js
async function login(email, password) {
    const response = await fetch('/api/accounts/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password }),
        credentials: 'include' // Important for cookies
    });
    
    if (response.ok) {
        const data = await response.json();
        // Store access token
        localStorage.setItem('access_token', data.access);
        console.log('Login successful!');
        return data;
    } else {
        const error = await response.json();
        console.error('Login failed:', error);
        throw error;
    }
}
```

### 3. **Automatic Token Refresh**

```js
async function refreshAccessToken() {
    const response = await fetch('/api/accounts/token/refresh/', {
        method: 'POST',
        credentials: 'include' // Sends refresh token cookie
    });
    
    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access);
        return data.access;
    } else {
        // Refresh token expired or invalid
        console.log('Session expired. Please login again.');
        // Redirect to login page
        window.location.href = '/login';
        return null;
    }
}

// Helper function to make authenticated requests
async function authenticatedFetch(url, options = {}) {
    let token = localStorage.getItem('access_token');
    
    // Add authorization header
    options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };
    options.credentials = 'include';
    
    let response = await fetch(url, options);
    
    // If token expired, refresh and retry
    if (response.status === 401) {
        token = await refreshAccessToken();
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
            response = await fetch(url, options);
        }
    }
    
    return response;
}
```

### 4. **Get Current User**

```js
async function getCurrentUser() {
    const response = await authenticatedFetch('/api/accounts/me/');
    
    if (response.ok) {
        const user = await response.json();
        console.log('Current user:', user);
        return user;
    } else {
        console.error('Failed to get current user');
        return null;
    }
}
```

### 5. **Email Verification**

```js
async function verifyEmail(token) {
    const response = await fetch('/api/accounts/verify-email/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token })
    });
    
    if (response.ok) {
        const data = await response.json();
        console.log('Email verified successfully!');
        return data;
    } else {
        const error = await response.json();
        console.error('Verification failed:', error);
        throw error;
    }
}

// Usage in a verification page component
// Get token from URL query parameter
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');
if (token) {
    verifyEmail(token);
}
```

### 6. **Resend Verification Email**

```js
async function resendVerification(email) {
    const response = await fetch('/api/accounts/resend-email-verification/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
    });
    
    if (response.ok) {
        console.log('Verification email resent!');
        return await response.json();
    } else {
        const error = await response.json();
        console.error('Failed to resend email:', error);
        throw error;
    }
}
```

### 7. **Forgot Password**

```js
async function forgotPassword(email) {
    const response = await fetch('/api/accounts/forgot-password/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
    });
    
    if (response.ok) {
        console.log('Password reset email sent!');
        return await response.json();
    } else {
        const error = await response.json();
        console.error('Failed to send reset email:', error);
        throw error;
    }
}
```

### 8. **Reset Password**

```js
async function resetPassword(token, newPassword) {
    const response = await fetch('/api/accounts/reset-password/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: token,
            new_password: newPassword
        })
    });
    
    if (response.ok) {
        console.log('Password reset successfully!');
        return await response.json();
    } else {
        const error = await response.json();
        console.error('Password reset failed:', error);
        throw error;
    }
}

// Usage in a reset password page component
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');
// User enters new password, then:
resetPassword(token, newPassword);
```

### 9. **User Logout**

```js
async function logout() {
    const response = await authenticatedFetch('/api/accounts/logout/', {
        method: 'POST'
    });
    
    if (response.ok) {
        // Clear stored access token
        localStorage.removeItem('access_token');
        console.log('Logged out successfully');
        // Redirect to login page
        window.location.href = '/login';
    } else {
        console.error('Logout failed');
    }
}
```

### 10. **Complete React Hook Example**

```js
// useAuth.js - Custom React Hook
import { useState, useEffect, createContext, useContext } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        // Check if user is logged in on mount
        checkAuth();
    }, []);
    
    async function checkAuth() {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const response = await fetch('/api/accounts/me/', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    credentials: 'include'
                });
                
                if (response.ok) {
                    const userData = await response.json();
                    setUser(userData);
                } else {
                    // Try to refresh token
                    const newToken = await refreshAccessToken();
                    if (newToken) {
                        checkAuth(); // Retry with new token
                    }
                }
            } catch (error) {
                console.error('Auth check failed:', error);
            }
        }
        setLoading(false);
    }
    
    async function register(userData) {
        const response = await fetch('/api/accounts/register/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData),
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            await checkAuth();
            return data;
        }
        throw await response.json();
    }
    
    async function login(email, password) {
        const response = await fetch('/api/accounts/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            await checkAuth();
            return data;
        }
        throw await response.json();
    }
    
    async function logout() {
        try {
            await fetch('/api/accounts/logout/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                credentials: 'include'
            });
        } finally {
            localStorage.removeItem('access_token');
            setUser(null);
        }
    }
    
    const value = {
        user,
        loading,
        register,
        login,
        logout,
        refreshAuth: checkAuth
    };
    
    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}
```

---

## Error Handling

### Common Error Responses

**400 Bad Request**:
```json
{
    "password": ["Passwords do not match"],
    "email": ["This field must be unique."]
}
```

**401 Unauthorized**:
```json
{
    "detail": "Invalid or expired refresh token"
}
```

**404 Not Found**:
```json
{
    "detail": "User not found."
}
```

### Validation Errors

**Registration Validation**:
- Email must be valid and unique
- Password must meet strength requirements
- Both passwords must match
- First and last names are required

**Login Validation**:
- Email must exist
- Password must be correct
- Account must be active
- Email must be verified

---

## Security Considerations

### Password Requirements
- Minimum length (typically 8 characters)
- Cannot be too similar to user information
- Cannot be a commonly used password
- Cannot be entirely numeric

### Token Security
- **Access Tokens**: Short-lived, stored in memory/localStorage
- **Refresh Tokens**: Long-lived, stored in HTTP-only cookies
- **HTTPS**: Always use HTTPS in production
- **CORS**: Configure CORS properly for cookie-based authentication

### Email Security
- Verification tokens expire after set time
- Password reset tokens expire after set time
- Tokens are single-use (where applicable)
- Email addresses are case-insensitive

### Rate Limiting
Consider implementing rate limiting for:
- Login attempts (prevent brute force)
- Password reset requests (prevent abuse)
- Email verification resends (prevent spam)

---

## Configuration Requirements

### Django Settings

```python
# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@yourapp.com'

# Frontend URL (for email links)
FRONTEND_URL = 'https://yourfrontend.com'

# Cookie Settings
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True  # Set to True in production
SESSION_COOKIE_SAMESITE = 'Lax'
```

---

## Testing Endpoints

### Using cURL

**Register**:
```bash
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","first_name":"Test","last_name":"User","password":"TestPass123!","password2":"TestPass123!","is_seller":false}'
```

**Login**:
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}' \
  -c cookies.txt
```

**Get Current User**:
```bash
curl -X GET http://localhost:8000/api/accounts/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -b cookies.txt
```

**Refresh Token**:
```bash
curl -X POST http://localhost:8000/api/accounts/token/refresh/ \
  -b cookies.txt
```

**Logout**:
```bash
curl -X POST http://localhost:8000/api/accounts/logout/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -b cookies.txt
```

---

## Troubleshooting

### Common Issues

**Issue**: "Email is not verified" error on login
- **Solution**: User must verify email first. Use resend verification endpoint if needed.

**Issue**: Refresh token not working
- **Solution**: Ensure cookies are being sent with requests (`credentials: 'include'`)

**Issue**: CORS errors with cookies
- **Solution**: Configure Django CORS settings to allow credentials from your frontend domain

**Issue**: Password validation errors
- **Solution**: Ensure password meets all Django validation requirements

**Issue**: Username conflicts
- **Solution**: The system auto-generates unique usernames with random suffixes

---

## Best Practices for Frontend Developers

1. **Token Storage**:
   - Store access tokens in memory or sessionStorage
   - Never store refresh tokens in localStorage (they're in HTTP-only cookies)

2. **Auto Refresh**:
   - Implement automatic token refresh before expiration
   - Use interceptors/middleware for seamless token management

3. **Error Handling**:
   - Handle 401 errors by attempting token refresh
   - Redirect to login on refresh token expiration

4. **User Feedback**:
   - Show loading states during authentication
   - Display clear error messages from API responses
   - Confirm email verification requirement

5. **Email Verification**:
   - Remind users to verify email if not verified
   - Provide easy resend verification option

6. **Security**:
   - Always use HTTPS in production
   - Clear tokens on logout
   - Implement CSRF protection

7. **UX Considerations**:
   - Remember user preference (seller vs customer)
   - Auto-login after successful registration
   - Provide password strength indicator

---

## Future Enhancements

- Social authentication (Google, Facebook, etc.)
- Two-factor authentication (2FA)
- Account deletion functionality
- Profile update endpoints
- Change password for logged-in users
- Account settings management
- Session management (view/revoke active sessions)
- Email preferences
- Username change functionality

---

## Conclusion

This Accounts API provides a complete authentication system with registration, login, email verification, and password management. The JWT-based authentication with refresh tokens in HTTP-only cookies ensures security while maintaining a smooth user experience.

For any questions or issues, please contact the development team!