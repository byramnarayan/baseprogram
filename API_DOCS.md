# API Documentation

Complete reference for all API endpoints in the FastAPI User Management system.

## Base URL

```
http://localhost:8000
```

## Authentication

Most endpoints require authentication via JWT token. Include the token in the Authorization header:

```
Authorization: Bearer <your_token_here>
```

---

## Authentication Endpoints

### Register User

Create a new user account.

**Endpoint:** `POST /api/auth/register`

**Authentication:** Not required

**Request Body:**
```json
{
  "name": "John Doe",
  "username": "johndoe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "address": "123 Main St, City, Country",
  "password": "SecurePass123"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "John Doe",
  "username": "johndoe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "address": "123 Main St, City, Country",
  "photo": null,
  "image_path": "/static/profile_pics/default.jpg",
  "points": 0
}
```

**Errors:**
- `400 Bad Request` - Username or email already exists
- `422 Unprocessable Entity` - Invalid input data

---

### Login

Authenticate and receive a JWT token.

**Endpoint:** `POST /api/auth/token`

**Authentication:** Not required

**Request Body:** (application/x-www-form-urlencoded)
```
username=john@example.com&password=SecurePass123
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401 Unauthorized` - Invalid credentials

**Note:** The `username` field should contain the email address.

---

### Logout

Logout the current user (client-side operation).

**Endpoint:** `POST /api/auth/logout`

**Authentication:** Not required

**Response:** `204 No Content`

**Note:** This endpoint exists for consistency. Actual logout is handled client-side by deleting the token.

---

## User Endpoints

### Get Current User

Get the authenticated user's profile.

**Endpoint:** `GET /api/users/me`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "John Doe",
  "username": "johndoe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "address": "123 Main St, City, Country",
  "photo": null,
  "image_path": "/static/profile_pics/default.jpg",
  "points": 150
}
```

**Errors:**
- `401 Unauthorized` - Invalid or missing token

---

### Update Current User

Update the authenticated user's profile.

**Endpoint:** `PATCH /api/users/me`

**Authentication:** Required

**Request Body:** (all fields optional)
```json
{
  "name": "Jane Doe",
  "username": "janedoe",
  "photo": "newphoto.jpg"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Jane Doe",
  "username": "janedoe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "address": "123 Main St, City, Country",
  "photo": "newphoto.jpg",
  "image_path": "/media/profile_pics/newphoto.jpg",
  "points": 150
}
```

**Errors:**
- `400 Bad Request` - Username already taken
- `401 Unauthorized` - Invalid or missing token
- `422 Unprocessable Entity` - Invalid input data

---

### Delete Current User

Permanently delete the authenticated user's account.

**Endpoint:** `DELETE /api/users/me`

**Authentication:** Required

**Response:** `204 No Content`

**Errors:**
- `401 Unauthorized` - Invalid or missing token

**Warning:** This action cannot be undone!

---

### Get User by ID

Get a user's public profile.

**Endpoint:** `GET /api/users/{user_id}`

**Authentication:** Not required

**Path Parameters:**
- `user_id` (integer) - ID of the user to retrieve

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "John Doe",
  "username": "johndoe",
  "photo": null,
  "image_path": "/static/profile_pics/default.jpg",
  "points": 150
}
```

**Errors:**
- `404 Not Found` - User does not exist

**Note:** This endpoint returns only public information (no email, phone, or address).

---

## Leaderboard Endpoints

### Get Leaderboard

Get users ranked by points.

**Endpoint:** `GET /api/leaderboard`

**Authentication:** Not required

**Query Parameters:**
- `limit` (integer, optional) - Maximum number of users to return (1-1000, default: 100)
- `offset` (integer, optional) - Number of users to skip (default: 0)

**Example:** `GET /api/leaderboard?limit=10&offset=0`

**Response:** `200 OK`
```json
[
  {
    "id": 5,
    "name": "Alice Smith",
    "username": "alice",
    "photo": "alice.jpg",
    "image_path": "/media/profile_pics/alice.jpg",
    "points": 500
  },
  {
    "id": 2,
    "name": "Bob Johnson",
    "username": "bob",
    "photo": null,
    "image_path": "/static/profile_pics/default.jpg",
    "points": 350
  }
]
```

**Pagination Example:**
- Page 1: `?limit=10&offset=0`
- Page 2: `?limit=10&offset=10`
- Page 3: `?limit=10&offset=20`

---

## Data Models

### UserCreate (Request)

```json
{
  "name": "string (1-100 chars)",
  "username": "string (1-50 chars)",
  "email": "valid email address",
  "phone": "string (1-15 chars)",
  "address": "string (optional)",
  "password": "string (min 8 chars)"
}
```

### UserUpdate (Request)

```json
{
  "name": "string (1-100 chars, optional)",
  "username": "string (1-50 chars, optional)",
  "photo": "string (optional)"
}
```

### UserPrivate (Response)

```json
{
  "id": "integer",
  "name": "string",
  "username": "string",
  "email": "string",
  "phone": "string",
  "address": "string or null",
  "photo": "string or null",
  "image_path": "string",
  "points": "integer"
}
```

### UserPublic (Response)

```json
{
  "id": "integer",
  "name": "string",
  "username": "string",
  "photo": "string or null",
  "image_path": "string",
  "points": "integer"
}
```

### Token (Response)

```json
{
  "access_token": "string (JWT token)",
  "token_type": "string (always 'bearer')"
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Request successful, no content to return
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## Example Usage

### Complete Registration and Login Flow

```bash
# 1. Register a new user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "username": "johndoe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "password": "SecurePass123"
  }'

# 2. Login to get token
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=SecurePass123"

# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# 3. Get current user profile
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer eyJ..."

# 4. Update profile
curl -X PATCH "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe"}'

# 5. View leaderboard
curl -X GET "http://localhost:8000/api/leaderboard?limit=10"

# 6. Delete account
curl -X DELETE "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer eyJ..."
```

---

## Interactive Documentation

For interactive API testing, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- View all endpoints
- See request/response schemas
- Test endpoints directly in the browser
- Authenticate and make requests

---

## Rate Limiting

Currently, there is no rate limiting implemented. For production use, consider adding:
- Rate limiting middleware
- Request throttling
- IP-based restrictions

---

## Versioning

This API is currently version 1.0. Future versions may include:
- API versioning in URL (`/api/v2/...`)
- Deprecation notices
- Migration guides

---

## Support

For questions or issues:
1. Check the inline code comments
2. Review the LEARNING.md guide
3. Consult the FastAPI documentation
4. Test endpoints using /docs interface
