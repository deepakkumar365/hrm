# HRMS Mobile App API Documentation

## Overview

The HRMS Mobile API provides RESTful JSON endpoints for mobile application development. The system uses a **custom token-based authentication** system (no external JWT library required) with HMAC-SHA256 security.

---

## Base URL

```
Production: https://your-domain.com/api
Development: http://localhost:5000/api
```

## Authentication

### Token Format

Tokens are generated in the format: `base64_payload.hex_signature`

Example:
```
eyJ1c2VyX2lkIjogMSwgImV4cCI6ICIyMDI0LTAxLTAxVDEyOjAwOjAwIn0.a1b2c3d4e5f6...
```

### Token Properties

- **Duration**: 24 hours (86,400 seconds)
- **Security**: HMAC-SHA256 signed with Flask SECRET_KEY
- **Expiration**: Strictly enforced on verification

### How to Use Token

Include the token in the `Authorization` header:

```
Authorization: Bearer <your_token_here>
```

### Example Request

```bash
curl -X GET http://localhost:5000/api/user/profile \
  -H "Authorization: Bearer eyJ1c2VyX2lkIjogMSwgImV4cCI6ICIyMDI0LTAxLTAxVDEyOjAwOjAwIn0.a1b2c3d4e5f6..." \
  -H "Content-Type: application/json"
```

---

## Standard Response Format

All API responses follow this structure:

```json
{
  "status": "success|error",
  "message": "Human-readable message",
  "timestamp": "2024-01-01T12:00:00.000000",
  "data": {}
}
```

### Response Codes

| Code | Status | Meaning |
|------|--------|---------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request format or missing fields |
| 401 | Unauthorized | Invalid/missing token or authentication failed |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists (duplicate) |
| 500 | Server Error | Internal server error |

---

## API Endpoints

### 1. AUTHENTICATION ENDPOINTS

---

#### 1.1 Login

**Endpoint**: `POST /api/auth/login`

**Description**: Authenticate user and receive token for subsequent requests

**Authentication**: Not required

**Request Body**:
```json
{
  "username": "john.doe@example.com",
  "password": "password123"
}
```

**Response (200 - Success)**:
```json
{
  "status": "success",
  "message": "Login successful",
  "timestamp": "2024-01-01T12:00:00.000000",
  "data": {
    "user_id": 1,
    "username": "john.doe",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "HR Manager",
    "role_id": 2,
    "company_id": 1,
    "employee_id": 5,
    "profile_image_path": "/static/uploads/profile_1.jpg",
    "token": "eyJ1c2VyX2lkIjogMSwgImV4cCI6ICIyMDI0LTAxLTAxVDEyOjAwOjAwIn0.a1b2c3d4e5f6...",
    "expires_in": 86400
  }
}
```

**Response (400 - Invalid Request)**:
```json
{
  "status": "error",
  "message": "Username and password are required",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**Response (401 - Invalid Credentials)**:
```json
{
  "status": "error",
  "message": "Invalid username or password",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**Response (403 - Inactive Account)**:
```json
{
  "status": "error",
  "message": "User account is inactive",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john.doe",
    "password": "password123"
  }'
```

---

#### 1.2 Logout

**Endpoint**: `POST /api/auth/logout`

**Description**: Invalidate user session and logout

**Authentication**: ✅ Required (Token)

**Request Body**: Empty

**Response (200 - Success)**:
```json
{
  "status": "success",
  "message": "Logout successful",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json"
```

---

#### 1.3 Register

**Endpoint**: `POST /api/auth/register`

**Description**: Register a new user account

**Authentication**: Not required

**Request Body**:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "password": "securepass123",
  "company_id": 1
}
```

**Response (201 - Created)**:
```json
{
  "status": "success",
  "message": "Registration successful",
  "timestamp": "2024-01-01T12:00:00.000000",
  "data": {
    "user_id": 2,
    "username": "newuser",
    "email": "newuser@example.com"
  }
}
```

**Response (409 - Duplicate)**:
```json
{
  "status": "error",
  "message": "Username already exists",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "password": "securepass123",
    "company_id": 1
  }'
```

---

#### 1.4 Refresh Token

**Endpoint**: `POST /api/auth/refresh-token`

**Description**: Get a new token before current one expires

**Authentication**: ✅ Required (Token)

**Request Body**: Empty

**Response (200 - Success)**:
```json
{
  "status": "success",
  "message": "Token refreshed",
  "timestamp": "2024-01-01T12:00:00.000000",
  "data": {
    "token": "eyJ1c2VyX2lkIjogMSwgImV4cCI6ICIyMDI0LTAxLTAyVDEyOjAwOjAwIn0.b2c3d4e5f6g7...",
    "expires_in": 86400
  }
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:5000/api/auth/refresh-token \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json"
```

---

### 2. USER PROFILE ENDPOINTS

---

#### 2.1 Get Current User Profile

**Endpoint**: `GET /api/user/profile`

**Description**: Retrieve authenticated user's profile information

**Authentication**: ✅ Required (Token)

**Query Parameters**: None

**Response (200 - Success)**:
```json
{
  "status": "success",
  "message": "Profile retrieved",
  "timestamp": "2024-01-01T12:00:00.000000",
  "data": {
    "user_id": 1,
    "username": "john.doe",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": "HR Manager",
    "phone": "+60123456789",
    "profile_image_path": "/static/uploads/profile_1.jpg",
    "designation": "Senior HR Manager",
    "department": "Human Resources",
    "company": "TechCorp Malaysia"
  }
}
```

**Example cURL**:
```bash
curl -X GET http://localhost:5000/api/user/profile \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json"
```

---

### 3. EMPLOYEE MANAGEMENT ENDPOINTS

---

#### 3.1 Get Employees List

**Endpoint**: `GET /api/employees`

**Description**: Retrieve list of employees with pagination and filtering

**Authentication**: ✅ Required (Token)

**Query Parameters**:
- `page` (int, default: 1) - Page number for pagination
- `per_page` (int, default: 20) - Records per page (max: 100)
- `search` (string) - Search by name or email
- `status` (string) - Filter by status: `active`, `inactive`, `all`
- `department_id` (int) - Filter by department
- `designation_id` (int) - Filter by designation

**Response (200 - Success)**:
```json
{
  "status": "success",
  "message": "Employees retrieved",
  "timestamp": "2024-01-01T12:00:00.000000",
  "data": {
    "total": 250,
    "page": 1,
    "per_page": 20,
    "total_pages": 13,
    "employees": [
      {
        "employee_id": 5,
        "user_id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "employee_code": "EMP001",
        "phone": "+60123456789",
        "designation": "Senior HR Manager",
        "department": "Human Resources",
        "status": "active",
        "date_of_joining": "2023-01-15",
        "profile_image_path": "/static/uploads/profile_1.jpg"
      },
      {
        "employee_id": 6,
        "user_id": 2,
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "employee_code": "EMP002",
        "phone": "+60187654321",
        "designation": "HR Executive",
        "department": "Human Resources",
        "status": "active",
        "date_of_joining": "2023-03-20",
        "profile_image_path": "/static/uploads/profile_2.jpg"
      }
    ]
  }
}
```

**Example cURL**:
```bash
# Basic request
curl -X GET "http://localhost:5000/api/employees" \
  -H "Authorization: Bearer <your_token>"

# With pagination
curl -X GET "http://localhost:5000/api/employees?page=2&per_page=50" \
  -H "Authorization: Bearer <your_token>"

# With search filter
curl -X GET "http://localhost:5000/api/employees?search=John&status=active" \
  -H "Authorization: Bearer <your_token>"

# With department filter
curl -X GET "http://localhost:5000/api/employees?department_id=3" \
  -H "Authorization: Bearer <your_token>"
```

---

#### 3.2 Get Employee Details

**Endpoint**: `GET /api/employees/<employee_id>`

**Description**: Retrieve detailed information for a specific employee

**Authentication**: ✅ Required (Token)

**Path Parameters**:
- `employee_id` (int) - Employee ID

**Response (200 - Success)**:
```json
{
  "status": "success",
  "message": "Employee details retrieved",
  "timestamp": "2024-01-01T12:00:00.000000",
  "data": {
    "employee_id": 5,
    "user_id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "employee_code": "EMP001",
    "phone": "+60123456789",
    "nric": "123456789012",
    "date_of_birth": "1990-05-15",
    "gender": "Male",
    "marital_status": "Married",
    "designation": "Senior HR Manager",
    "designation_id": 10,
    "department": "Human Resources",
    "department_id": 3,
    "reporting_manager": "Sarah Johnson",
    "status": "active",
    "date_of_joining": "2023-01-15",
    "profile_image_path": "/static/uploads/profile_1.jpg",
    "address": "123 Main Street, Kuala Lumpur",
    "bank_account": "123456789",
    "basic_salary": 5000.00
  }
}
```

**Example cURL**:
```bash
curl -X GET http://localhost:5000/api/employees/5 \
  -H "Authorization: Bearer <your_token>"
```

---

### 4. ATTENDANCE ENDPOINTS

---

#### 4.1 Get Attendance Records

**Endpoint**: `GET /api/attendance`

**Description**: Retrieve attendance records with pagination and filtering

**Authentication**: ✅ Required (Token)

**Query Parameters**:
- `page` (int, default: 1) - Page number
- `per_page` (int, default: 20) - Records per page
- `employee_id` (int) - Filter by employee
- `from_date` (string, format: YYYY-MM-DD) - Start date
- `to_date` (string, format: YYYY-MM-DD) - End date
- `status` (string) - Filter: `present`, `absent`, `half_day`, `leave`

**Response (200 - Success)**:
```json
{
  "status": "success",
  "message": "Attendance records retrieved",
  "timestamp": "2024-01-01T12:00:00.000000",
  "data": {
    "total": 25,
    "page": 1,
    "per_page": 20,
    "records": [
      {
        "attendance_id": 1,
        "employee_id": 5,
        "employee_name": "John Doe",
        "attendance_date": "2024-01-01",
        "status": "present",
        "check_in_time": "09:00:00",
        "check_out_time": "17:30:00",
        "working_hours": 8.5,
        "notes": "Regular working day"
      },
      {
        "attendance_id": 2,
        "employee_id": 5,
        "employee_name": "John Doe",
        "attendance_date": "2024-01-02",
        "status": "absent",
        "check_in_time": null,
        "check_out_time": null,
        "working_hours": 0,
        "notes": "Approved leave"
      }
    ]
  }
}
```

**Example cURL**:
```bash
# Get all attendance
curl -X GET "http://localhost:5000/api/attendance" \
  -H "Authorization: Bearer <your_token>"

# Get attendance for specific employee in date range
curl -X GET "http://localhost:5000/api/attendance?employee_id=5&from_date=2024-01-01&to_date=2024-01-31" \
  -H "Authorization: Bearer <your_token>"

# Get absent records
curl -X GET "http://localhost:5000/api/attendance?status=absent" \
  -H "Authorization: Bearer <your_token>"
```

---

#### 4.2 Mark Attendance

**Endpoint**: `POST /api/attendance/mark`

**Description**: Mark attendance for user (check-in/check-out)

**Authentication**: ✅ Required (Token)

**Request Body**:
```json
{
  "attendance_date": "2024-01-01",
  "status": "present",
  "check_in_time": "09:00:00",
  "check_out_time": "17:30:00",
  "notes": "Regular day"
}
```

**Response (201 - Created)**:
```json
{
  "status": "success",
  "message": "Attendance marked successfully",
  "timestamp": "2024-01-01T12:00:00.000000",
  "data": {
    "attendance_id": 150,
    "employee_id": 5,
    "attendance_date": "2024-01-01",
    "status": "present",
    "check_in_time": "09:00:00",
    "check_out_time": "17:30:00",
    "working_hours": 8.5
  }
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:5000/api/attendance/mark \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "attendance_date": "2024-01-01",
    "status": "present",
    "check_in_time": "09:00:00",
    "check_out_time": "17:30:00",
    "notes": "Regular day"
  }'
```

---

### 5. LEAVE MANAGEMENT ENDPOINTS

---

#### 5.1 Get Leave Requests

**Endpoint**: `GET /api/leaves`

**Description**: Retrieve leave requests with filtering options

**Authentication**: ✅ Required (Token)

**Query Parameters**:
- `page` (int, default: 1) - Page number
- `per_page` (int, default: 20) - Records per page
- `employee_id` (int) - Filter by employee
- `status` (string) - Filter: `pending`, `approved`, `rejected`, `cancelled`
- `from_date` (string, YYYY-MM-DD) - Start date
- `to_date` (string, YYYY-MM-DD) - End date

**Response (200 - Success)**:
```json
{
  "status": "success",
  "message": "Leave requests retrieved",
  "timestamp": "2024-01-01T12:00:00.000000",
  "data": {
    "total": 12,
    "page": 1,
    "per_page": 20,
    "requests": [
      {
        "leave_id": 1,
        "employee_id": 5,
        "employee_name": "John Doe",
        "leave_type": "Annual Leave",
        "start_date": "2024-02-01",
        "end_date": "2024-02-05",
        "duration_days": 5,
        "status": "approved",
        "reason": "Personal vacation",
        "applied_date": "2024-01-20",
        "approved_by": "Sarah Johnson",
        "approval_date": "2024-01-21"
      },
      {
        "leave_id": 2,
        "employee_id": 5,
        "employee_name": "John Doe",
        "leave_type": "Sick Leave",
        "start_date": "2024-01-10",
        "end_date": "2024-01-10",
        "duration_days": 1,
        "status": "pending",
        "reason": "Medical checkup",
        "applied_date": "2024-01-10",
        "approved_by": null,
        "approval_date": null
      }
    ]
  }
}
```

**Example cURL**:
```bash
# Get all leave requests
curl -X GET "http://localhost:5000/api/leaves" \
  -H "Authorization: Bearer <your_token>"

# Get pending leaves for specific employee
curl -X GET "http://localhost:5000/api/leaves?employee_id=5&status=pending" \
  -H "Authorization: Bearer <your_token>"

# Get leaves in date range
curl -X GET "http://localhost:5000/api/leaves?from_date=2024-01-01&to_date=2024-12-31" \
  -H "Authorization: Bearer <your_token>"
```

---

#### 5.2 Create Leave Request

**Endpoint**: `POST /api/leaves`

**Description**: Submit a new leave request

**Authentication**: ✅ Required (Token)

**Request Body**:
```json
{
  "leave_type": "Annual Leave",
  "start_date": "2024-02-01",
  "end_date": "2024-02-05",
  "reason": "Personal vacation"
}
```

**Response (201 - Created)**:
```json
{
  "status": "success",
  "message": "Leave request created successfully",
  "timestamp": "2024-01-01T12:00:00.000000",
  "data": {
    "leave_id": 100,
    "employee_id": 5,
    "leave_type": "Annual Leave",
    "start_date": "2024-02-01",
    "end_date": "2024-02-05",
    "duration_days": 5,
    "status": "pending",
    "reason": "Personal vacation",
    "applied_date": "2024-01-01"
  }
}
```

**Response (400 - Invalid Request)**:
```json
{
  "status": "error",
  "message": "Leave balance insufficient for requested days",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:5000/api/leaves \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "leave_type": "Annual Leave",
    "start_date": "2024-02-01",
    "end_date": "2024-02-05",
    "reason": "Personal vacation"
  }'
```

---

### 6. PAYROLL ENDPOINTS

---

#### 6.1 Get Payslips

**Endpoint**: `GET /api/payslips`

**Description**: Retrieve payslips with pagination

**Authentication**: ✅ Required (Token)

**Query Parameters**:
- `page` (int, default: 1) - Page number
- `per_page` (int, default: 20) - Records per page
- `employee_id` (int) - Filter by employee
- `year` (int) - Filter by year
- `month` (int) - Filter by month (1-12)

**Response (200 - Success)**:
```json
{
  "status": "success",
  "message": "Payslips retrieved",
  "timestamp": "2024-01-01T12:00:00.000000",
  "data": {
    "total": 24,
    "page": 1,
    "per_page": 20,
    "payslips": [
      {
        "payslip_id": 1,
        "employee_id": 5,
        "employee_name": "John Doe",
        "month": "January",
        "year": 2024,
        "payslip_date": "2024-01-31",
        "basic_salary": 5000.00,
        "allowances": 1000.00,
        "deductions": 750.00,
        "net_salary": 5250.00,
        "status": "paid",
        "paid_date": "2024-02-01"
      },
      {
        "payslip_id": 2,
        "employee_id": 5,
        "employee_name": "John Doe",
        "month": "February",
        "year": 2024,
        "payslip_date": "2024-02-29",
        "basic_salary": 5000.00,
        "allowances": 1000.00,
        "deductions": 750.00,
        "net_salary": 5250.00,
        "status": "pending",
        "paid_date": null
      }
    ]
  }
}
```

**Example cURL**:
```bash
# Get all payslips for current user
curl -X GET "http://localhost:5000/api/payslips" \
  -H "Authorization: Bearer <your_token>"

# Get specific month payslip
curl -X GET "http://localhost:5000/api/payslips?month=1&year=2024" \
  -H "Authorization: Bearer <your_token>"

# Get payslips for specific employee
curl -X GET "http://localhost:5000/api/payslips?employee_id=5" \
  -H "Authorization: Bearer <your_token>"
```

---

### 7. DASHBOARD ENDPOINTS

---

#### 7.1 Get Dashboard Statistics

**Endpoint**: `GET /api/dashboard/stats`

**Description**: Retrieve dashboard statistics and summary data

**Authentication**: ✅ Required (Token)

**Response (200 - Success)**:
```json
{
  "status": "success",
  "message": "Dashboard stats retrieved",
  "timestamp": "2024-01-01T12:00:00.000000",
  "data": {
    "total_employees": 250,
    "active_employees": 245,
    "inactive_employees": 5,
    "departments": 12,
    "designations": 45,
    "today_present": 238,
    "today_absent": 7,
    "today_leave": 5,
    "pending_leave_requests": 8,
    "pending_overtime": 3,
    "payroll_status": "processed",
    "last_payroll_date": "2024-01-31",
    "total_monthly_payroll": 1250000.00
  }
}
```

**Example cURL**:
```bash
curl -X GET http://localhost:5000/api/dashboard/stats \
  -H "Authorization: Bearer <your_token>"
```

---

### 8. HEALTH CHECK ENDPOINT

---

#### 8.1 Health Check

**Endpoint**: `GET /api/health`

**Description**: Check API health status (no authentication required)

**Authentication**: Not required

**Response (200 - Success)**:
```json
{
  "status": "success",
  "message": "API is running",
  "timestamp": "2024-01-01T12:00:00.000000",
  "data": {
    "version": "1.0.0",
    "database": "connected",
    "uptime": "24 hours"
  }
}
```

**Example cURL**:
```bash
curl -X GET http://localhost:5000/api/health
```

---

## Error Handling

### Common Error Responses

**401 - Missing Token**:
```json
{
  "status": "error",
  "message": "Token is missing",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**401 - Invalid Token**:
```json
{
  "status": "error",
  "message": "Invalid or expired token",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**404 - Resource Not Found**:
```json
{
  "status": "error",
  "message": "Employee not found",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**500 - Server Error**:
```json
{
  "status": "error",
  "message": "Internal server error: [error details]",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

---

## Mobile App Implementation Examples

### Python (Requests Library)

```python
import requests
import json

BASE_URL = "http://localhost:5000/api"

class HRMSClient:
    def __init__(self):
        self.token = None
        self.headers = {"Content-Type": "application/json"}
    
    def login(self, username, password):
        """Login and store token"""
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password},
            headers=self.headers
        )
        data = response.json()
        
        if data["status"] == "success":
            self.token = data["data"]["token"]
            self.headers["Authorization"] = f"Bearer {self.token}"
            return data["data"]
        else:
            raise Exception(data["message"])
    
    def get_profile(self):
        """Get user profile"""
        response = requests.get(
            f"{BASE_URL}/user/profile",
            headers=self.headers
        )
        return response.json()
    
    def get_employees(self, page=1, per_page=20, search=""):
        """Get employees list"""
        params = {"page": page, "per_page": per_page, "search": search}
        response = requests.get(
            f"{BASE_URL}/employees",
            headers=self.headers,
            params=params
        )
        return response.json()
    
    def mark_attendance(self, attendance_date, status, check_in, check_out, notes=""):
        """Mark attendance"""
        response = requests.post(
            f"{BASE_URL}/attendance/mark",
            json={
                "attendance_date": attendance_date,
                "status": status,
                "check_in_time": check_in,
                "check_out_time": check_out,
                "notes": notes
            },
            headers=self.headers
        )
        return response.json()
    
    def create_leave_request(self, leave_type, start_date, end_date, reason):
        """Create leave request"""
        response = requests.post(
            f"{BASE_URL}/leaves",
            json={
                "leave_type": leave_type,
                "start_date": start_date,
                "end_date": end_date,
                "reason": reason
            },
            headers=self.headers
        )
        return response.json()

# Usage
client = HRMSClient()
user_data = client.login("john.doe", "password123")
print(f"Logged in as: {user_data['first_name']} {user_data['last_name']}")

profile = client.get_profile()
print(profile)

employees = client.get_employees(page=1)
print(employees)
```

### JavaScript (Fetch API)

```javascript
class HRMSClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
    this.token = null;
  }

  async login(username, password) {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    if (data.status === 'success') {
      this.token = data.data.token;
      return data.data;
    } else {
      throw new Error(data.message);
    }
  }

  async getProfile() {
    const response = await fetch(`${this.baseUrl}/user/profile`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return await response.json();
  }

  async getEmployees(page = 1, perPage = 20, search = '') {
    const params = new URLSearchParams({
      page,
      per_page: perPage,
      search
    });
    
    const response = await fetch(
      `${this.baseUrl}/employees?${params}`,
      { headers: { 'Authorization': `Bearer ${this.token}` } }
    );
    return await response.json();
  }

  async markAttendance(attendanceDate, status, checkIn, checkOut, notes = '') {
    const response = await fetch(`${this.baseUrl}/attendance/mark`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify({
        attendance_date: attendanceDate,
        status,
        check_in_time: checkIn,
        check_out_time: checkOut,
        notes
      })
    });
    return await response.json();
  }

  async createLeaveRequest(leaveType, startDate, endDate, reason) {
    const response = await fetch(`${this.baseUrl}/leaves`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify({
        leave_type: leaveType,
        start_date: startDate,
        end_date: endDate,
        reason
      })
    });
    return await response.json();
  }
}

// Usage
const client = new HRMSClient('http://localhost:5000/api');

(async () => {
  try {
    const userData = await client.login('john.doe', 'password123');
    console.log(`Logged in as: ${userData.first_name} ${userData.last_name}`);
    
    const profile = await client.getProfile();
    console.log(profile);
    
    const employees = await client.getEmployees();
    console.log(employees);
  } catch (error) {
    console.error('Error:', error.message);
  }
})();
```

---

## Best Practices

### 1. Token Management
- **Store token securely** in mobile app (secure storage, not localStorage if possible)
- **Refresh token** before expiration (call `/api/auth/refresh-token` before 24 hours)
- **Clear token** on logout
- **Include token** in all API requests via Authorization header

### 2. Error Handling
- Always check `status` field in response
- Log error messages for debugging
- Implement exponential backoff for retries on 5xx errors
- Handle 401 errors by forcing re-authentication

### 3. Performance
- Use pagination with appropriate `per_page` values
- Filter data server-side when possible
- Cache responses locally when appropriate
- Compress large payloads

### 4. Security
- Always use HTTPS in production
- Validate all user inputs before sending
- Never expose tokens in URLs
- Implement rate limiting on client side

### 5. Data Validation
- Validate date formats (YYYY-MM-DD)
- Check required fields before submission
- Handle timezone differences appropriately
- Validate email and phone formats

---

## Troubleshooting

### Common Issues

**"Token is missing"**
- Ensure Authorization header is included in request
- Token format should be: `Bearer <your_token>`

**"Invalid or expired token"**
- Token may have expired (24-hour limit)
- Call `/api/auth/refresh-token` to get new token
- Check token isn't corrupted

**"Content-Type must be application/json"**
- For POST requests, include header: `Content-Type: application/json`
- Request body must be valid JSON

**Pagination returns empty results**
- Check if page number exceeds total pages
- Ensure search/filter parameters are correct
- Verify user has access to requested data

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-01 | Initial API release with auth, employee, attendance, leave, payroll endpoints |

---

## Support

For issues or questions regarding the API:
1. Check the troubleshooting section above
2. Review example implementations
3. Check server logs for detailed error messages
4. Contact the development team with error details and logs

---

## Changelog

### Planned Features (v1.1)
- [ ] Overtime management endpoints
- [ ] Appraisal endpoints
- [ ] Document management endpoints
- [ ] Bulk operations support
- [ ] Advanced filtering and sorting
- [ ] Export functionality (CSV/Excel)
- [ ] Webhook support for real-time updates