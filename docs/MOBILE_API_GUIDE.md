# Mobile App JSON API Guide

## Overview

Your HRMS system now has a complete **JSON REST API** for mobile app development. All endpoints return JSON responses and support both **session-based** and **JWT token-based** authentication.

---

## API Base URL

```
http://localhost:5000/api
```

Or in production:
```
https://your-production-url.com/api
```

---

## Authentication Methods

### 1. JWT Token Authentication (Recommended for Mobile)

**Token-based authentication using JWT headers**

#### Step 1: Login to get JWT Token

**POST** `/api/auth/login`

```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Login successful",
  "timestamp": "2024-01-15T10:30:00.123456",
  "data": {
    "user_id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "HR Manager",
    "company_id": 1,
    "employee_id": 5,
    "profile_image_path": "/static/uploads/profile.jpg",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400
  }
}
```

#### Step 2: Use Token in Subsequent Requests

Add the token to the **Authorization header** in all protected API calls:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**In Postman:**
1. Go to **Authorization** tab
2. Select **Bearer Token**
3. Paste the token from login response

#### Step 3: Refresh Token (Optional)

**POST** `/api/auth/refresh-token`

Headers:
```
Authorization: Bearer <your_token>
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Token refreshed",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400
  }
}
```

---

## API Endpoints

### Authentication Endpoints

#### 1. Login
**POST** `/api/auth/login`
- Returns JWT token for subsequent requests
- Token valid for 24 hours

#### 2. Register
**POST** `/api/auth/register`

```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "password": "securePassword123",
  "company_id": 1
}
```

#### 3. Logout
**POST** `/api/auth/logout`

Headers:
```
Authorization: Bearer <token>
```

#### 4. Refresh Token
**POST** `/api/auth/refresh-token`

Headers:
```
Authorization: Bearer <token>
```

---

### User Profile Endpoints

#### 1. Get Current User Profile
**GET** `/api/user/profile`

Headers:
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Profile retrieved",
  "data": {
    "user_id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": "HR Manager",
    "phone": "+65-98765432",
    "profile_image_path": "/static/uploads/profile.jpg",
    "designation": "HR Manager",
    "department": "Human Resources",
    "company": "Acme Corp"
  }
}
```

---

### Employee Management Endpoints

#### 1. Get Employees List (Paginated)
**GET** `/api/employees?page=1&per_page=20&search=john&status=active`

Headers:
```
Authorization: Bearer <token>
```

Query Parameters:
- `page` - Page number (default: 1)
- `per_page` - Records per page (default: 20, max: 100)
- `search` - Search by name or email
- `status` - Filter by status: `active`, `inactive`, or `all` (default: active)

**Response (200):**
```json
{
  "status": "success",
  "message": "Employees retrieved",
  "data": {
    "employees": [
      {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "employee_id": "EMP001",
        "phone": "+65-98765432",
        "designation": "Software Engineer",
        "department": "IT",
        "status": "active"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 150,
      "pages": 8
    }
  }
}
```

#### 2. Get Employee Details
**GET** `/api/employees/{employee_id}`

Headers:
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Employee details retrieved",
  "data": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+65-98765432",
    "employee_id": "EMP001",
    "nric": "S1234567A",
    "date_of_birth": "1990-05-15",
    "designation": "Software Engineer",
    "department": "IT",
    "company": "Acme Corp",
    "joining_date": "2020-01-15",
    "status": "active",
    "profile_image_path": "/static/uploads/emp1.jpg"
  }
}
```

---

### Attendance Endpoints

#### 1. Get Attendance Records
**GET** `/api/attendance?employee_id=1&from_date=2024-01-01&to_date=2024-01-31&page=1&per_page=50`

Headers:
```
Authorization: Bearer <token>
```

Query Parameters:
- `employee_id` - Filter by employee
- `from_date` - From date (YYYY-MM-DD)
- `to_date` - To date (YYYY-MM-DD)
- `page` - Page number
- `per_page` - Records per page

**Response (200):**
```json
{
  "status": "success",
  "message": "Attendance records retrieved",
  "data": {
    "records": [
      {
        "id": 1,
        "employee_id": 1,
        "date": "2024-01-15",
        "check_in": "2024-01-15T09:05:30",
        "check_out": "2024-01-15T18:15:45",
        "status": "present",
        "duration_hours": 8.5
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 50,
      "total": 22,
      "pages": 1
    }
  }
}
```

#### 2. Mark Attendance (Check In/Out)
**POST** `/api/attendance/mark`

Headers:
```
Authorization: Bearer <token>
Content-Type: application/json
```

Request Body:
```json
{
  "employee_id": 1,
  "action": "check_in",
  "latitude": 1.3521,
  "longitude": 103.8198
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Attendance check_in recorded",
  "data": {
    "employee_id": 1,
    "date": "2024-01-15",
    "check_in": "2024-01-15T09:05:30",
    "check_out": null
  }
}
```

---

### Leave Management Endpoints

#### 1. Get Leave Requests
**GET** `/api/leave/requests?employee_id=1&status=pending&page=1&per_page=20`

Headers:
```
Authorization: Bearer <token>
```

Query Parameters:
- `employee_id` - Filter by employee
- `status` - Filter by status: `pending`, `approved`, `rejected`
- `page` - Page number
- `per_page` - Records per page

**Response (200):**
```json
{
  "status": "success",
  "message": "Leave requests retrieved",
  "data": {
    "requests": [
      {
        "id": 1,
        "employee_id": 1,
        "employee_name": "John Doe",
        "from_date": "2024-01-15",
        "to_date": "2024-01-17",
        "leave_type": "Annual Leave",
        "reason": "Personal reasons",
        "status": "pending",
        "created_at": "2024-01-14T10:30:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 5,
      "pages": 1
    }
  }
}
```

#### 2. Create Leave Request
**POST** `/api/leave/request`

Headers:
```
Authorization: Bearer <token>
Content-Type: application/json
```

Request Body:
```json
{
  "employee_id": 1,
  "from_date": "2024-01-15",
  "to_date": "2024-01-17",
  "leave_type": "Annual Leave",
  "reason": "Personal reasons"
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "Leave request created",
  "data": {
    "id": 1,
    "employee_id": 1,
    "from_date": "2024-01-15",
    "to_date": "2024-01-17",
    "status": "pending"
  }
}
```

---

### Payroll Endpoints

#### 1. Get Payslips
**GET** `/api/payroll/payslips?employee_id=1&from_date=2024-01-01&to_date=2024-01-31&page=1&per_page=20`

Headers:
```
Authorization: Bearer <token>
```

Query Parameters:
- `employee_id` - Filter by employee
- `from_date` - From date (YYYY-MM-DD)
- `to_date` - To date (YYYY-MM-DD)
- `page` - Page number
- `per_page` - Records per page

**Response (200):**
```json
{
  "status": "success",
  "message": "Payslips retrieved",
  "data": {
    "payslips": [
      {
        "id": 1,
        "employee_id": 1,
        "pay_period_start": "2024-01-01",
        "pay_period_end": "2024-01-31",
        "basic_salary": 5000.00,
        "total_earnings": 5500.00,
        "total_deductions": 800.00,
        "net_salary": 4700.00,
        "status": "paid"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 12,
      "pages": 1
    }
  }
}
```

---

### Dashboard Endpoints

#### 1. Get Dashboard Statistics
**GET** `/api/dashboard/stats`

Headers:
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Dashboard statistics retrieved",
  "data": {
    "total_employees": 150,
    "present_today": 145,
    "pending_leave_requests": 5,
    "attendance_rate": 96.67
  }
}
```

---

### Health Check Endpoint

#### 1. API Health Check (No Authentication Required)
**GET** `/api/health`

**Response (200):**
```json
{
  "status": "success",
  "message": "API is healthy",
  "timestamp": "2024-01-15T10:30:00.123456",
  "data": {
    "database": "connected",
    "timestamp": "2024-01-15T10:30:00.123456"
  }
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "status": "error",
  "message": "Error description",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

### Common HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid input parameters
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists (e.g., duplicate email)
- `500 Internal Server Error` - Server error

### Example Error Response

**POST** `/api/auth/login` with invalid credentials

```json
{
  "status": "error",
  "message": "Invalid username or password",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

---

## Testing with Postman

### Quick Start

1. **Create a new collection** called "HRMS Mobile API"

2. **Create a folder** for Authentication

3. **Create POST request for Login:**
   - URL: `http://localhost:5000/api/auth/login`
   - Body (JSON):
   ```json
   {
     "username": "superadmin",
     "password": "default_password"
   }
   ```
   - Click **Send**

4. **Copy the token** from response

5. **Create a variable** for the token:
   - Click **Collections > ... > Edit**
   - Go to **Variables** tab
   - Create variable: `token` with the copied value

6. **For protected endpoints**, set Authorization:
   - Type: **Bearer Token**
   - Token: `{{token}}`

---

## Mobile App Implementation Example (React Native / Flutter)

### Login Example (JavaScript/React Native)

```javascript
// Login
async function login(username, password) {
  const response = await fetch('http://localhost:5000/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password })
  });
  
  const data = await response.json();
  
  if (data.status === 'success') {
    const { token } = data.data;
    // Save token to secure storage
    await AsyncStorage.setItem('auth_token', token);
    return data.data;
  } else {
    throw new Error(data.message);
  }
}

// Mark Attendance
async function checkIn(employeeId) {
  const token = await AsyncStorage.getItem('auth_token');
  
  const response = await fetch('http://localhost:5000/api/attendance/mark', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      employee_id: employeeId,
      action: 'check_in'
    })
  });
  
  return await response.json();
}

// Get Employee Profile
async function getProfile() {
  const token = await AsyncStorage.getItem('auth_token');
  
  const response = await fetch('http://localhost:5000/api/user/profile', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
}
```

---

## Rate Limiting & Best Practices

- **Token expiration**: 24 hours
- **Pagination**: Use `per_page=20` for optimal performance
- **Always use HTTPS** in production
- **Store tokens securely** on mobile devices (use platform-specific secure storage)
- **Handle token refresh** before it expires
- **Implement proper error handling** for network failures

---

## Support & Documentation

For issues or additional endpoints, contact the development team or check the routes file at:
```
/hrm/routes_api.py
```

---

**Last Updated:** January 2024
**API Version:** 1.0