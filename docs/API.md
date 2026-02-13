# API Documentation

Complete API reference for Dunkin Demand Intelligence

---

## Base URL

- **Development:** `http://localhost:5000`
- **Production:** `https://api.dunkindemand.com`

---

## Authentication Endpoints

### POST /auth/signup
Register a new user account.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response (201):**
```json
{
  "status": "success",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-02-13T10:30:00"
  }
}
```

**Error (400):**
```json
{
  "status": "error",
  "message": "Email already registered"
}
```

---

### POST /auth/login
Authenticate user with email and password.

**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "status": "success",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-02-13T10:30:00"
  }
}
```

**Error (401):**
```json
{
  "status": "error",
  "message": "Incorrect email or password"
}
```

---

### POST /auth/forgot-password
Request a password reset email.

**Request:**
```json
{
  "email": "john@example.com"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "If email exists, reset link will be sent"
}
```

**Notes:**
- Always returns success for security (doesn't reveal if email exists)
- Email is sent with password reset link
- Token expires in 1 hour

---

### POST /auth/validate-reset-token
Validate a password reset token before allowing password change.

**Request:**
```json
{
  "token": "abc123xyz..."
}
```

**Response (200):**
```json
{
  "status": "success",
  "user_id": 1,
  "email": "john@example.com",
  "name": "John Doe"
}
```

**Error (400):**
```json
{
  "status": "error",
  "message": "Invalid or expired token"
}
```

---

### POST /auth/reset-password
Reset user password using valid reset token.

**Request:**
```json
{
  "token": "abc123xyz...",
  "password": "NewPassword123!"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Password reset successfully"
}
```

**Error (400):**
```json
{
  "status": "error",
  "message": "Invalid or already-used token"
}
```

**Requirements:**
- Password must be 8+ characters
- Token must not be expired (1 hour max)
- Token must not have been used before

---

## Dashboard Endpoints

### GET /dashboard
Get dashboard statistics and KPIs.

**Headers:**
```
Authorization: Bearer session_token
```

**Response (200):**
```json
{
  "status": "success",
  "total_sales": 4521.50,
  "forecast_accuracy": 91.2,
  "daily_products_sold": 348,
  "waste_percentage": 3.2,
  "top_products": [
    {
      "name": "Glazed Donut",
      "quantity": 450,
      "revenue": 1350.00
    },
    {
      "name": "Boston Kreme",
      "quantity": 320,
      "revenue": 1120.00
    }
  ]
}
```

---

## Forecast Endpoints

### GET /forecast
Get sales forecast for specified number of days.

**Query Parameters:**
- `days` (optional): Number of days to forecast (default: 30)

**Headers:**
```
Authorization: Bearer session_token
```

**Response (200):**
```json
{
  "status": "success",
  "forecast": [
    {
      "date": "2026-02-14",
      "predicted_sales": 4800,
      "confidence": 0.92,
      "lower_bound": 4320,
      "upper_bound": 5280
    },
    {
      "date": "2026-02-15",
      "predicted_sales": 5120,
      "confidence": 0.89,
      "lower_bound": 4556,
      "upper_bound": 5684
    }
  ]
}
```

---

### POST /daily-production-plan
Get optimized production plan based on forecast.

**Request:**
```json
{
  "date": "2026-02-14"
}
```

**Response (200):**
```json
{
  "status": "success",
  "recommended_production": {
    "glazed_donuts": 480,
    "boston_kreme": 320,
    "jelly_donuts": 240,
    "old_fashioned": 180
  },
  "estimated_waste": 15,
  "confidence": 0.92
}
```

---

### GET /forecast/accuracy
Get forecast accuracy metrics.

**Query Parameters:**
- `period` (optional): "week", "month", "year" (default: "month")

**Response (200):**
```json
{
  "status": "success",
  "accuracy_rate": 91.2,
  "mean_absolute_error": 45.3,
  "predictions_total": 120,
  "predictions_accurate": 109
}
```

---

## Daily Data Endpoints

### POST /daily-sales
Record daily sales for a product.

**Request:**
```json
{
  "date": "2026-02-13",
  "product_name": "Glazed Donut",
  "quantity_sold": 450,
  "revenue": 1350.00
}
```

**Response (201):**
```json
{
  "status": "success",
  "id": 1,
  "message": "Sale recorded successfully"
}
```

---

### GET /daily-sales
Get sales history.

**Query Parameters:**
- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD
- `product_name` (optional): Filter by product

**Response (200):**
```json
{
  "status": "success",
  "sales": [
    {
      "date": "2026-02-13",
      "product_name": "Glazed Donut",
      "quantity_sold": 450,
      "revenue": 1350.00
    }
  ]
}
```

---

### POST /daily-waste
Record product waste/throwaway.

**Request:**
```json
{
  "date": "2026-02-13",
  "product_name": "Boston Kreme",
  "quantity_wasted": 15,
  "reason": "End of day"
}
```

**Response (201):**
```json
{
  "status": "success",
  "id": 1,
  "message": "Waste recorded successfully"
}
```

---

### GET /daily-waste
Get waste history and analytics.

**Query Parameters:**
- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD

**Response (200):**
```json
{
  "status": "success",
  "waste_data": [
    {
      "date": "2026-02-13",
      "product_name": "Boston Kreme",
      "quantity_wasted": 15,
      "reason": "End of day"
    }
  ],
  "total_waste": 45,
  "waste_percentage": 3.2
}
```

---

## Export Endpoints

### GET /export/excel
Export sales and forecast data to Excel.

**Query Parameters:**
- `start_date` (required): YYYY-MM-DD
- `end_date` (required): YYYY-MM-DD
- `include` (optional): Comma-separated list of "sales","forecast","waste"

**Response:** Binary Excel file (application/vnd.ms-excel)

---

## Error Handling

All endpoints return JSON with error details.

### Common Error Codes

**400 Bad Request**
```json
{
  "status": "error",
  "message": "Invalid input format"
}
```

**401 Unauthorized**
```json
{
  "status": "error",
  "message": "Authentication required"
}
```

**403 Forbidden**
```json
{
  "status": "error",
  "message": "Insufficient permissions"
}
```

**404 Not Found**
```json
{
  "status": "error",
  "message": "Resource not found"
}
```

**500 Internal Server Error**
```json
{
  "status": "error",
  "message": "Internal server error"
}
```

---

## Rate Limiting

- **Auth endpoints:** 5 requests per minute
- **Other endpoints:** 100 requests per minute
- **Response headers include:**
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

---

## Best Practices

1. **Always include error handling** - Check response status before processing data
2. **Use appropriate HTTP methods** - GET for retrieval, POST for creation
3. **Include timestamps** - All responses include ISO 8601 timestamps
4. **Pagination** - Use limit/offset for large datasets
5. **Caching** - Cache dashboard data for 5 minutes for better performance
6. **Security** - Always use HTTPS in production, never expose tokens

---

**Last Updated:** February 13, 2026
