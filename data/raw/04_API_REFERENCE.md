# Hotel Booking System – API Reference

---

## Document Information

> **Version:** 2.0  
> **Updated:** October 27, 2025  
> **Author:** KnowRA API Team  
> **Tags:** api, rest-api, endpoints, integration, documentation, openapi  
> **Status:** Active  

---

## Table of Contents

1. [API Overview](#1-api-overview)
2. [Authentication & Authorization API](#2-authentication--authorization-api)
3. [Hotel Search API](#3-hotel-search-api)
4. [Room Management API](#4-room-management-api)
5. [Booking API](#5-booking-api)
6. [Payment API](#6-payment-api)
7. [Guest Management API](#7-guest-management-api)
8. [Review & Rating API](#8-review--rating-api)
9. [Loyalty Program API](#9-loyalty-program-api)
10. [Admin API](#10-admin-api)
11. [Integration API](#11-integration-api)
12. [Notification API](#12-notification-api)
13. [API Rate Limiting](#13-api-rate-limiting)
14. [API Versioning](#14-api-versioning)
15. [Testing & Sandbox](#15-testing--sandbox)
16. [Appendices](#appendices)

---

## 1. API Overview

### 1.1 Base URLs

| Environment | Base URL | Purpose |
|-------------|----------|---------|
| **Production** | `https://api.hotelbooking.com/v2` | Live production environment |
| **Staging** | `https://api-staging.hotelbooking.com/v2` | Pre-production testing |
| **Development** | `https://api-dev.hotelbooking.com/v2` | Development environment |
| **Sandbox** | `https://api-sandbox.hotelbooking.com/v2` | Integration testing |

### 1.2 Authentication

The API uses **Bearer Token Authentication** with JWT tokens issued by Azure Active Directory B2C.

**Authentication Flow:**
```http
POST /auth/login HTTP/1.1
Host: api.hotelbooking.com
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "def50200e3e02d...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "read write"
}
```

**Using the Token:**
```http
GET /hotels/search HTTP/1.1
Host: api.hotelbooking.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 1.3 Common Headers

| Header | Required | Description | Example |
|--------|----------|-------------|---------|
| `Authorization` | Yes* | Bearer token for authenticated requests | `Bearer eyJhbGciOiJSUzI1NiI...` |
| `Content-Type` | Yes | MIME type of request body | `application/json` |
| `Accept` | No | Preferred response format | `application/json` |
| `X-Request-ID` | No | Unique request identifier for tracking | `550e8400-e29b-41d4-a716-446655440000` |
| `X-API-Version` | No | API version override | `2.0` |
| `Accept-Language` | No | Preferred language for responses | `en-US, fr-FR` |
| `X-Currency` | No | Preferred currency for pricing | `USD, EUR, GBP` |

*Required for authenticated endpoints

### 1.4 Response Formats

**Standard Success Response:**
```json
{
  "success": true,
  "data": {
    // Response data object
  },
  "meta": {
    "timestamp": "2025-10-27T14:30:00Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "version": "2.0"
  }
}
```

**Paginated Response:**
```json
{
  "success": true,
  "data": [
    // Array of items
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 15,
    "total_items": 300,
    "has_next": true,
    "has_previous": false
  },
  "meta": {
    "timestamp": "2025-10-27T14:30:00Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### 1.5 Error Handling

**Error Response Format:**
```json
{
  "success": false,
  "error": {
    "code": "BOOKING_NOT_FOUND",
    "message": "The requested booking could not be found",
    "details": "Booking with ID 'b123e4567-e89b-12d3-a456-426614174000' does not exist",
    "field": "booking_id",
    "help_url": "https://docs.api.hotelbooking.com/errors/booking-not-found"
  },
  "meta": {
    "timestamp": "2025-10-27T14:30:00Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**HTTP Status Codes:**
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (duplicate, constraint violation)
- `422 Unprocessable Entity` - Validation errors
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

## 2. Authentication & Authorization API

### 2.1 User Registration

**Endpoint:** `POST /auth/register`

**Description:** Register a new user account.

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1-555-123-4567",
  "date_of_birth": "1990-05-15",
  "preferred_language": "en",
  "preferred_currency": "USD",
  "marketing_consent": true
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "john.doe@example.com",
    "email_verified": false,
    "verification_email_sent": true
  },
  "meta": {
    "timestamp": "2025-10-27T14:30:00Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Validation Rules:**
- Email must be valid and unique
- Password must be 8+ characters with uppercase, lowercase, number, and special character
- Phone number must be valid international format
- Date of birth must be 18+ years ago

### 2.2 User Login

**Endpoint:** `POST /auth/login`

**Description:** Authenticate user and receive access tokens.

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePassword123!",
  "remember_me": true
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "def50200e3e02d...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "john.doe@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "roles": ["guest"],
      "email_verified": true
    }
  }
}
```

### 2.3 Token Refresh

**Endpoint:** `POST /auth/refresh`

**Description:** Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "def50200e3e02d..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

### 2.4 Logout

**Endpoint:** `POST /auth/logout`

**Description:** Invalidate current session and tokens.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "Successfully logged out"
  }
}
```

### 2.5 Password Reset

**Endpoint:** `POST /auth/password/reset`

**Description:** Initiate password reset process.

**Request Body:**
```json
{
  "email": "john.doe@example.com"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "Password reset email sent if account exists",
    "reset_token_expires": "2025-10-27T15:30:00Z"
  }
}
```

---

## 3. Hotel Search API

### 3.1 Search Hotels

**Endpoint:** `GET /hotels/search`

**Description:** Search for hotels based on location, dates, and filters.

**Query Parameters:**
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `location` | string | Yes | City, address, or landmark | `New York, NY` |
| `check_in` | date | Yes | Check-in date (ISO 8601) | `2025-11-15` |
| `check_out` | date | Yes | Check-out date (ISO 8601) | `2025-11-18` |
| `adults` | integer | Yes | Number of adult guests | `2` |
| `children` | integer | No | Number of child guests | `1` |
| `rooms` | integer | No | Number of rooms (default: 1) | `1` |
| `min_price` | decimal | No | Minimum price per night | `100.00` |
| `max_price` | decimal | No | Maximum price per night | `500.00` |
| `star_rating` | array | No | Hotel star ratings | `[4,5]` |
| `amenities` | array | No | Required amenities | `["wifi","pool","gym"]` |
| `distance` | integer | No | Max distance from location (km) | `10` |
| `sort_by` | string | No | Sort criteria | `price_asc`, `rating_desc`, `distance_asc` |
| `page` | integer | No | Page number (default: 1) | `1` |
| `per_page` | integer | No | Items per page (default: 20, max: 100) | `20` |

**Example Request:**
```http
GET /hotels/search?location=New%20York,%20NY&check_in=2025-11-15&check_out=2025-11-18&adults=2&star_rating[]=4&star_rating[]=5&amenities[]=wifi&amenities[]=pool&sort_by=price_asc HTTP/1.1
Host: api.hotelbooking.com
Authorization: Bearer eyJhbGciOiJSUzI1NiI...
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "hotel_id": "h123e4567-e89b-12d3-a456-426614174000",
      "name": "Grand Plaza Hotel New York",
      "description": "Luxury hotel in the heart of Manhattan",
      "star_rating": 4,
      "address": {
        "street": "123 Broadway",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA"
      },
      "location": {
        "latitude": 40.7128,
        "longitude": -74.0060
      },
      "distance_km": 2.5,
      "amenities": ["wifi", "pool", "gym", "spa", "restaurant"],
      "images": [
        {
          "url": "https://cdn.hotelbooking.com/hotels/h123/main.jpg",
          "type": "main",
          "alt": "Hotel exterior view"
        }
      ],
      "availability": {
        "available": true,
        "rooms_available": 5,
        "rate": {
          "amount": 299.00,
          "currency": "USD",
          "per_night": true,
          "taxes_included": false,
          "total_amount": 897.00,
          "total_nights": 3
        }
      },
      "ratings": {
        "overall": 4.2,
        "cleanliness": 4.5,
        "location": 4.8,
        "service": 4.0,
        "value": 3.9,
        "total_reviews": 1542
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 15,
    "total_items": 287,
    "has_next": true,
    "has_previous": false
  },
  "filters_applied": {
    "location": "New York, NY",
    "check_in": "2025-11-15",
    "check_out": "2025-11-18",
    "adults": 2,
    "star_rating": [4, 5],
    "amenities": ["wifi", "pool"]
  }
}
```

### 3.2 Get Hotel Details

**Endpoint:** `GET /hotels/{hotel_id}`

**Description:** Get detailed information about a specific hotel.

**Path Parameters:**
- `hotel_id` (string, required) - Unique hotel identifier

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "hotel_id": "h123e4567-e89b-12d3-a456-426614174000",
    "name": "Grand Plaza Hotel New York",
    "description": "Experience luxury and comfort in the heart of Manhattan. Our hotel offers world-class amenities and exceptional service.",
    "star_rating": 4,
    "address": {
      "street": "123 Broadway",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "USA"
    },
    "contact": {
      "phone": "+1-212-555-0123",
      "email": "info@grandplazany.com",
      "website": "https://www.grandplazany.com"
    },
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    },
    "amenities": [
      {
        "code": "wifi",
        "name": "Free WiFi",
        "category": "connectivity"
      },
      {
        "code": "pool",
        "name": "Indoor Pool",
        "category": "recreation"
      }
    ],
    "images": [
      {
        "url": "https://cdn.hotelbooking.com/hotels/h123/main.jpg",
        "type": "main",
        "alt": "Hotel exterior view",
        "width": 1200,
        "height": 800
      }
    ],
    "policies": {
      "check_in_time": "15:00",
      "check_out_time": "11:00",
      "cancellation_policy": "Free cancellation up to 24 hours before check-in",
      "pet_policy": "Pets not allowed",
      "child_policy": "Children under 12 stay free with parents"
    },
    "ratings": {
      "overall": 4.2,
      "cleanliness": 4.5,
      "location": 4.8,
      "service": 4.0,
      "value": 3.9,
      "total_reviews": 1542
    }
  }
}
```

### 3.3 Get Hotel Amenities

**Endpoint:** `GET /hotels/amenities`

**Description:** Get list of all available hotel amenities with categories.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "code": "connectivity",
        "name": "Connectivity",
        "amenities": [
          {
            "code": "wifi",
            "name": "Free WiFi",
            "description": "Complimentary wireless internet access"
          },
          {
            "code": "business_center",
            "name": "Business Center",
            "description": "24/7 business center with computers and printers"
          }
        ]
      },
      {
        "code": "recreation",
        "name": "Recreation",
        "amenities": [
          {
            "code": "pool",
            "name": "Swimming Pool",
            "description": "Indoor or outdoor swimming pool"
          },
          {
            "code": "gym",
            "name": "Fitness Center",
            "description": "Fully equipped fitness center"
          }
        ]
      }
    ]
  }
}
```

### 3.4 Search Filters

**Endpoint:** `GET /hotels/filters`

**Description:** Get available search filters and their options.

**Query Parameters:**
- `location` (string, optional) - Filter options specific to location

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "price_range": {
      "min": 50,
      "max": 2000,
      "currency": "USD"
    },
    "star_ratings": [1, 2, 3, 4, 5],
    "amenities": [
      {
        "code": "wifi",
        "name": "Free WiFi",
        "category": "connectivity",
        "available_count": 1247
      }
    ],
    "hotel_chains": [
      {
        "code": "marriott",
        "name": "Marriott Hotels",
        "hotel_count": 45
      }
    ],
    "neighborhoods": [
      {
        "code": "manhattan",
        "name": "Manhattan",
        "hotel_count": 156
      }
    ]
  }
}
```

### 3.5 Hotel Availability

**Endpoint:** `GET /hotels/{hotel_id}/availability`

**Description:** Check room availability and rates for specific dates.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `check_in` | date | Yes | Check-in date |
| `check_out` | date | Yes | Check-out date |
| `adults` | integer | Yes | Number of adults |
| `children` | integer | No | Number of children |
| `rooms` | integer | No | Number of rooms |

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "hotel_id": "h123e4567-e89b-12d3-a456-426614174000",
    "available": true,
    "check_in": "2025-11-15",
    "check_out": "2025-11-18",
    "room_types": [
      {
        "room_type_id": "rt123e4567-e89b-12d3-a456-426614174000",
        "name": "Standard Double Room",
        "description": "Comfortable room with city view",
        "max_occupancy": 2,
        "bed_configuration": "1 King Bed",
        "room_size": 35,
        "amenities": ["wifi", "tv", "minibar"],
        "available_rooms": 3,
        "rate_plans": [
          {
            "rate_plan_id": "rp123e4567-e89b-12d3-a456-426614174000",
            "name": "Best Available Rate",
            "description": "Our best rate with free cancellation",
            "cancellation_policy": "Free cancellation until 24 hours before check-in",
            "breakfast_included": false,
            "refundable": true,
            "rate": {
              "amount": 299.00,
              "currency": "USD",
              "per_night": true,
              "taxes": 35.88,
              "fees": 25.00,
              "total_amount": 1077.64,
              "total_nights": 3
            }
          }
        ]
      }
    ]
  }
}
```

---

## 4. Room Management API

### 4.1 Get Available Rooms

**Endpoint:** `GET /rooms/available`

**Description:** Get available rooms across multiple hotels for specific criteria.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `location` | string | Yes | Search location |
| `check_in` | date | Yes | Check-in date |
| `check_out` | date | Yes | Check-out date |
| `adults` | integer | Yes | Number of adults |
| `children` | integer | No | Number of children |
| `room_type` | string | No | Specific room type filter |

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "room_id": "r123e4567-e89b-12d3-a456-426614174000",
      "hotel_id": "h123e4567-e89b-12d3-a456-426614174000",
      "hotel_name": "Grand Plaza Hotel New York",
      "room_type": "Deluxe King Room",
      "max_occupancy": 2,
      "bed_configuration": "1 King Bed",
      "room_size": 42,
      "floor": "12-18",
      "view": "City View",
      "amenities": [
        "wifi", "tv", "minibar", "safe", "balcony"
      ],
      "rate": {
        "amount": 349.00,
        "currency": "USD",
        "per_night": true,
        "total_amount": 1047.00,
        "total_nights": 3
      },
      "available_count": 2
    }
  ],
  "meta": {
    "total_available": 156,
    "search_criteria": {
      "location": "New York, NY",
      "check_in": "2025-11-15",
      "check_out": "2025-11-18",
      "adults": 2
    }
  }
}
```

### 4.2 Get Room Details

**Endpoint:** `GET /rooms/{room_id}`

**Description:** Get detailed information about a specific room.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "room_id": "r123e4567-e89b-12d3-a456-426614174000",
    "hotel_id": "h123e4567-e89b-12d3-a456-426614174000",
    "room_number": "1205",
    "room_type": "Deluxe King Room",
    "description": "Spacious room with panoramic city views and modern amenities",
    "max_occupancy": 2,
    "max_adults": 2,
    "max_children": 1,
    "bed_configuration": "1 King Bed",
    "room_size": 42,
    "size_unit": "sqm",
    "floor": 12,
    "view": "City View",
    "smoking_allowed": false,
    "amenities": [
      {
        "code": "wifi",
        "name": "Free WiFi",
        "description": "High-speed wireless internet"
      },
      {
        "code": "balcony",
        "name": "Private Balcony",
        "description": "Private balcony with city views"
      }
    ],
    "images": [
      {
        "url": "https://cdn.hotelbooking.com/rooms/r123/main.jpg",
        "type": "main",
        "alt": "Deluxe King Room overview"
      }
    ],
    "accessibility": {
      "wheelchair_accessible": true,
      "hearing_accessible": false,
      "visual_accessible": false
    }
  }
}
```

### 4.3 Check Room Availability

**Endpoint:** `POST /rooms/check-availability`

**Description:** Check availability for multiple rooms in a single request.

**Request Body:**
```json
{
  "requests": [
    {
      "room_id": "r123e4567-e89b-12d3-a456-426614174000",
      "check_in": "2025-11-15",
      "check_out": "2025-11-18",
      "adults": 2,
      "children": 0
    },
    {
      "room_id": "r456e7890-e89b-12d3-a456-426614174000",
      "check_in": "2025-11-15",
      "check_out": "2025-11-18",
      "adults": 2,
      "children": 1
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "room_id": "r123e4567-e89b-12d3-a456-426614174000",
      "available": true,
      "available_count": 3,
      "rate": {
        "amount": 349.00,
        "currency": "USD",
        "total_amount": 1047.00
      }
    },
    {
      "room_id": "r456e7890-e89b-12d3-a456-426614174000",
      "available": false,
      "reason": "No availability for selected dates"
    }
  ]
}
```

### 4.4 Get Room Types

**Endpoint:** `GET /hotels/{hotel_id}/room-types`

**Description:** Get all room types available at a specific hotel.

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "room_type_id": "rt123e4567-e89b-12d3-a456-426614174000",
      "name": "Standard Double Room",
      "description": "Comfortable room perfect for couples",
      "max_occupancy": 2,
      "bed_configurations": ["1 Queen Bed", "2 Twin Beds"],
      "room_size": 28,
      "size_unit": "sqm",
      "amenities": ["wifi", "tv", "safe"],
      "base_rate": {
        "amount": 199.00,
        "currency": "USD"
      },
      "images": [
        {
          "url": "https://cdn.hotelbooking.com/room-types/rt123/main.jpg",
          "alt": "Standard Double Room"
        }
      ]
    }
  ]
}
```

### 4.5 Get Rate Plans

**Endpoint:** `GET /rooms/{room_id}/rate-plans`

**Description:** Get available rate plans for a specific room.

**Query Parameters:**
- `check_in` (date, required) - Check-in date
- `check_out` (date, required) - Check-out date

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "rate_plan_id": "rp123e4567-e89b-12d3-a456-426614174000",
      "name": "Best Available Rate",
      "description": "Our most flexible rate with free cancellation",
      "rate_type": "BAR",
      "cancellation_policy": "Free cancellation until 18:00 day before arrival",
      "prepayment_required": false,
      "breakfast_included": false,
      "refundable": true,
      "rate": {
        "base_amount": 299.00,
        "taxes": 35.88,
        "fees": 25.00,
        "total_amount": 359.88,
        "currency": "USD",
        "per_night": true
      },
      "restrictions": {
        "minimum_stay": 1,
        "maximum_stay": 30,
        "advance_booking_required": 0
      }
    },
    {
      "rate_plan_id": "rp456e7890-e89b-12d3-a456-426614174000",
      "name": "Advance Purchase",
      "description": "Save 15% with advance booking - Non-refundable",
      "rate_type": "PROMOTIONAL",
      "cancellation_policy": "Non-refundable",
      "prepayment_required": true,
      "breakfast_included": true,
      "refundable": false,
      "rate": {
        "base_amount": 254.15,
        "taxes": 30.50,
        "fees": 25.00,
        "total_amount": 309.65,
        "currency": "USD",
        "per_night": true
      },
      "restrictions": {
        "minimum_stay": 2,
        "maximum_stay": 14,
        "advance_booking_required": 14
      }
    }
  ]
}
```

---

## 5. Booking API

### 5.1 Create Booking

**Endpoint:** `POST /bookings`

**Description:** Create a new hotel booking.

**Request Body:**
```json
{
  "hotel_id": "h123e4567-e89b-12d3-a456-426614174000",
  "room_id": "r123e4567-e89b-12d3-a456-426614174000",
  "rate_plan_id": "rp123e4567-e89b-12d3-a456-426614174000",
  "check_in": "2025-11-15",
  "check_out": "2025-11-18",
  "guests": {
    "adults": 2,
    "children": 0
  },
  "rooms": 1,
  "guest_details": {
    "primary_guest": {
      "title": "Mr",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "phone": "+1-555-123-4567"
    },
    "additional_guests": [
      {
        "title": "Mrs",
        "first_name": "Jane",
        "last_name": "Doe"
      }
    ]
  },
  "special_requests": "Late check-in after 10 PM. High floor room preferred.",
  "billing_address": {
    "street": "123 Main St",
    "city": "Boston",
    "state": "MA",
    "postal_code": "02101",
    "country": "USA"
  },
  "payment_method": "credit_card",
  "hold_booking": false
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "booking_id": "b123e4567-e89b-12d3-a456-426614174000",
    "booking_reference": "HBS-2025-001234",
    "status": "confirmed",
    "hotel": {
      "hotel_id": "h123e4567-e89b-12d3-a456-426614174000",
      "name": "Grand Plaza Hotel New York",
      "address": "123 Broadway, New York, NY 10001"
    },
    "room": {
      "room_id": "r123e4567-e89b-12d3-a456-426614174000",
      "room_type": "Deluxe King Room",
      "bed_configuration": "1 King Bed"
    },
    "stay_details": {
      "check_in": "2025-11-15",
      "check_out": "2025-11-18",
      "nights": 3,
      "guests": {
        "adults": 2,
        "children": 0
      },
      "rooms": 1
    },
    "pricing": {
      "base_amount": 897.00,
      "taxes": 107.64,
      "fees": 75.00,
      "total_amount": 1079.64,
      "currency": "USD"
    },
    "cancellation": {
      "cancellable": true,
      "deadline": "2025-11-14T18:00:00Z",
      "penalty": 0.00
    },
    "created_at": "2025-10-27T14:30:00Z",
    "confirmation_sent": true
  }
}
```

### 5.2 Get Booking Details

**Endpoint:** `GET /bookings/{booking_id}`

**Description:** Get detailed information about a specific booking.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "booking_id": "b123e4567-e89b-12d3-a456-426614174000",
    "booking_reference": "HBS-2025-001234",
    "status": "confirmed",
    "hotel": {
      "hotel_id": "h123e4567-e89b-12d3-a456-426614174000",
      "name": "Grand Plaza Hotel New York",
      "address": {
        "street": "123 Broadway",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA"
      },
      "contact": {
        "phone": "+1-212-555-0123",
        "email": "reservations@grandplazany.com"
      }
    },
    "room": {
      "room_id": "r123e4567-e89b-12d3-a456-426614174000",
      "room_type": "Deluxe King Room",
      "bed_configuration": "1 King Bed",
      "amenities": ["wifi", "tv", "minibar", "safe", "balcony"]
    },
    "stay_details": {
      "check_in": "2025-11-15",
      "check_out": "2025-11-18",
      "nights": 3,
      "guests": {
        "adults": 2,
        "children": 0
      },
      "rooms": 1
    },
    "guest_details": {
      "primary_guest": {
        "title": "Mr",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-123-4567"
      }
    },
    "pricing": {
      "rate_plan": "Best Available Rate",
      "base_amount": 897.00,
      "taxes": 107.64,
      "fees": 75.00,
      "total_amount": 1079.64,
      "currency": "USD",
      "breakdown": [
        {
          "date": "2025-11-15",
          "amount": 299.00,
          "taxes": 35.88,
          "fees": 25.00
        },
        {
          "date": "2025-11-16",
          "amount": 299.00,
          "taxes": 35.88,
          "fees": 25.00
        },
        {
          "date": "2025-11-17",
          "amount": 299.00,
          "taxes": 35.88,
          "fees": 25.00
        }
      ]
    },
    "payment": {
      "status": "paid",
      "method": "credit_card",
      "amount_paid": 1079.64,
      "payment_date": "2025-10-27T14:30:00Z"
    },
    "cancellation": {
      "cancellable": true,
      "deadline": "2025-11-14T18:00:00Z",
      "penalty": 0.00,
      "policy": "Free cancellation until 18:00 day before arrival"
    },
    "special_requests": "Late check-in after 10 PM. High floor room preferred.",
    "created_at": "2025-10-27T14:30:00Z",
    "updated_at": "2025-10-27T14:30:00Z"
  }
}
```

### 5.3 Update Booking

**Endpoint:** `PUT /bookings/{booking_id}`

**Description:** Update an existing booking (dates, guests, special requests).

**Request Body:**
```json
{
  "check_out": "2025-11-19",
  "special_requests": "Late check-in after 10 PM. High floor room preferred. Extra towels needed.",
  "guest_details": {
    "primary_guest": {
      "phone": "+1-555-123-9999"
    }
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "booking_id": "b123e4567-e89b-12d3-a456-426614174000",
    "booking_reference": "HBS-2025-001234",
    "status": "confirmed",
    "changes": [
      {
        "field": "check_out",
        "old_value": "2025-11-18",
        "new_value": "2025-11-19"
      },
      {
        "field": "special_requests",
        "old_value": "Late check-in after 10 PM. High floor room preferred.",
        "new_value": "Late check-in after 10 PM. High floor room preferred. Extra towels needed."
      }
    ],
    "pricing_changes": {
      "old_total": 1079.64,
      "new_total": 1439.52,
      "difference": 359.88,
      "additional_payment_required": true
    },
    "updated_at": "2025-10-27T15:45:00Z"
  }
}
```

### 5.4 Cancel Booking

**Endpoint:** `DELETE /bookings/{booking_id}`

**Description:** Cancel an existing booking.

**Request Body:**
```json
{
  "reason": "Change of travel plans",
  "requested_by": "guest"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "booking_id": "b123e4567-e89b-12d3-a456-426614174000",
    "booking_reference": "HBS-2025-001234",
    "status": "cancelled",
    "cancellation": {
      "cancelled_at": "2025-10-27T16:00:00Z",
      "reason": "Change of travel plans",
      "cancelled_by": "guest",
      "penalty_amount": 0.00,
      "refund_amount": 1079.64,
      "refund_method": "original_payment_method",
      "refund_timeline": "5-7 business days"
    }
  }
}
```

### 5.5 Get Booking History

**Endpoint:** `GET /bookings`

**Description:** Get booking history for the authenticated user.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by booking status |
| `from_date` | date | Bookings from this date |
| `to_date` | date | Bookings until this date |
| `page` | integer | Page number |
| `per_page` | integer | Items per page |

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "booking_id": "b123e4567-e89b-12d3-a456-426614174000",
      "booking_reference": "HBS-2025-001234",
      "status": "confirmed",
      "hotel_name": "Grand Plaza Hotel New York",
      "check_in": "2025-11-15",
      "check_out": "2025-11-18",
      "nights": 3,
      "total_amount": 1079.64,
      "currency": "USD",
      "created_at": "2025-10-27T14:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 3,
    "total_items": 45
  }
}
```

### 5.6 Confirm Booking

**Endpoint:** `POST /bookings/{booking_id}/confirm`

**Description:** Confirm a pending booking (for bookings that require manual confirmation).

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "booking_id": "b123e4567-e89b-12d3-a456-426614174000",
    "status": "confirmed",
    "confirmed_at": "2025-10-27T16:30:00Z",
    "confirmation_number": "CNF-HBS-2025-001234"
  }
}
```

---

## 6. Payment API

### 6.1 Process Payment

**Endpoint:** `POST /payments`

**Description:** Process payment for a booking.

**Request Body:**
```json
{
  "booking_id": "b123e4567-e89b-12d3-a456-426614174000",
  "payment_method": "credit_card",
  "amount": 1079.64,
  "currency": "USD",
  "card_details": {
    "card_token": "tok_1234567890abcdef",
    "cardholder_name": "John Doe",
    "billing_address": {
      "street": "123 Main St",
      "city": "Boston",
      "state": "MA",
      "postal_code": "02101",
      "country": "USA"
    }
  },
  "save_payment_method": false
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "payment_id": "pay_123e4567-e89b-12d3-a456-426614174000",
    "transaction_id": "txn_987654321",
    "status": "completed",
    "amount": 1079.64,
    "currency": "USD",
    "payment_method": "credit_card",
    "card_info": {
      "last4": "4242",
      "brand": "visa",
      "exp_month": 12,
      "exp_year": 2026
    },
    "processed_at": "2025-10-27T14:30:00Z",
    "receipt_url": "https://receipts.hotelbooking.com/pay_123e4567"
  }
}
```

### 6.2 Get Payment Methods

**Endpoint:** `GET /payments/methods`

**Description:** Get available payment methods for the user.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "saved_methods": [
      {
        "payment_method_id": "pm_123456789",
        "type": "credit_card",
        "card": {
          "last4": "4242",
          "brand": "visa",
          "exp_month": 12,
          "exp_year": 2026
        },
        "billing_address": {
          "street": "123 Main St",
          "city": "Boston",
          "state": "MA",
          "postal_code": "02101",
          "country": "USA"
        },
        "is_default": true
      }
    ],
    "available_methods": [
      {
        "type": "credit_card",
        "name": "Credit/Debit Card",
        "supported_brands": ["visa", "mastercard", "amex", "discover"],
        "processing_fee": 0.029
      },
      {
        "type": "paypal",
        "name": "PayPal",
        "processing_fee": 0.034
      },
      {
        "type": "bank_transfer",
        "name": "Bank Transfer",
        "processing_fee": 0.00,
        "processing_time": "1-3 business days"
      }
    ]
  }
}
```

### 6.3 Verify Payment

**Endpoint:** `GET /payments/{payment_id}`

**Description:** Get payment status and details.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "payment_id": "pay_123e4567-e89b-12d3-a456-426614174000",
    "booking_id": "b123e4567-e89b-12d3-a456-426614174000",
    "transaction_id": "txn_987654321",
    "status": "completed",
    "amount": 1079.64,
    "currency": "USD",
    "payment_method": "credit_card",
    "gateway": "stripe",
    "gateway_response": {
      "status": "succeeded",
      "authorization_code": "12345A"
    },
    "processed_at": "2025-10-27T14:30:00Z",
    "fees": {
      "processing_fee": 31.31,
      "gateway_fee": 2.16
    }
  }
}
```

### 6.4 Refund Payment

**Endpoint:** `POST /payments/{payment_id}/refund`

**Description:** Process a refund for a payment.

**Request Body:**
```json
{
  "amount": 1079.64,
  "reason": "booking_cancelled",
  "description": "Full refund due to booking cancellation"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "refund_id": "ref_123e4567-e89b-12d3-a456-426614174000",
    "payment_id": "pay_123e4567-e89b-12d3-a456-426614174000",
    "amount": 1079.64,
    "currency": "USD",
    "status": "pending",
    "reason": "booking_cancelled",
    "expected_arrival": "2025-11-03",
    "processed_at": "2025-10-27T16:00:00Z"
  }
}
```

### 6.5 Get Payment History

**Endpoint:** `GET /payments`

**Description:** Get payment history for the authenticated user.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `booking_id` | string | Filter by specific booking |
| `status` | string | Filter by payment status |
| `from_date` | date | Payments from this date |
| `to_date` | date | Payments until this date |

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "payment_id": "pay_123e4567-e89b-12d3-a456-426614174000",
      "booking_reference": "HBS-2025-001234",
      "amount": 1079.64,
      "currency": "USD",
      "status": "completed",
      "payment_method": "credit_card",
      "processed_at": "2025-10-27T14:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_items": 15
  }
}
```

---

## 7. Guest Management API

### 7.1 Get Guest Profile

**Endpoint:** `GET /guests/{guest_id}`

**Description:** Get detailed guest profile information.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "guest_id": "g123e4567-e89b-12d3-a456-426614174000",
    "title": "Mr",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-123-4567",
    "date_of_birth": "1985-03-15",
    "nationality": "USA",
    "address": {
      "street": "123 Main St",
      "city": "Boston",
      "state": "MA",
      "postal_code": "02101",
      "country": "USA"
    },
    "preferences": {
      "room_type": "king",
      "floor_preference": "high",
      "smoking": false,
      "special_needs": ["vegetarian_meals", "late_checkin"]
    },
    "loyalty_program": {
      "member": true,
      "tier": "Gold",
      "member_since": "2023-05-10",
      "points_balance": 12450
    },
    "stay_statistics": {
      "total_bookings": 15,
      "total_nights": 42,
      "favorite_destinations": ["New York", "Los Angeles", "Miami"]
    },
    "created_at": "2023-05-10T09:15:00Z",
    "updated_at": "2025-10-27T14:30:00Z"
  }
}
```

### 7.2 Update Guest Profile

**Endpoint:** `PUT /guests/{guest_id}`

**Description:** Update guest profile information.

**Request Body:**
```json
{
  "phone": "+1-555-987-6543",
  "address": {
    "street": "456 Oak Avenue",
    "city": "Cambridge",
    "state": "MA",
    "postal_code": "02139",
    "country": "USA"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "guest_id": "g123e4567-e89b-12d3-a456-426614174000",
    "updated_fields": ["phone", "address"],
    "updated_at": "2025-10-27T15:45:00Z"
  }
}
```

### 7.3 Get Guest Preferences

**Endpoint:** `GET /guests/{guest_id}/preferences`

**Description:** Get guest preferences and special requirements.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "room_preferences": {
      "room_type": "king",
      "bed_type": "king",
      "floor_preference": "high",
      "smoking": false,
      "connecting_rooms": false
    },
    "accessibility": {
      "wheelchair_accessible": false,
      "hearing_accessible": false,
      "visual_accessible": false
    },
    "amenities": [
      "wifi", "minibar", "balcony", "gym_access"
    ],
    "special_requests": [
      "vegetarian_meals",
      "late_checkin",
      "extra_towels"
    ],
    "communication": {
      "language": "English",
      "contact_method": "email",
      "marketing_emails": true,
      "booking_reminders": true
    }
  }
}
```

### 7.4 Update Guest Preferences

**Endpoint:** `PUT /guests/{guest_id}/preferences`

**Description:** Update guest preferences and special requirements.

**Request Body:**
```json
{
  "room_preferences": {
    "room_type": "suite",
    "floor_preference": "high",
    "smoking": false
  },
  "special_requests": [
    "vegetarian_meals",
    "late_checkin",
    "gym_access",
    "room_service"
  ],
  "communication": {
    "marketing_emails": false,
    "booking_reminders": true
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "updated_categories": ["room_preferences", "special_requests", "communication"],
    "updated_at": "2025-10-27T16:00:00Z"
  }
}
```

### 7.5 Get Guest Bookings

**Endpoint:** `GET /guests/{guest_id}/bookings`

**Description:** Get all bookings for a specific guest.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by booking status |
| `from_date` | date | Bookings from this date |
| `to_date` | date | Bookings until this date |

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "booking_id": "b123e4567-e89b-12d3-a456-426614174000",
      "booking_reference": "HBS-2025-001234",
      "status": "confirmed",
      "hotel_name": "Grand Plaza Hotel New York",
      "check_in": "2025-11-15",
      "check_out": "2025-11-18",
      "total_amount": 1079.64,
      "currency": "USD",
      "created_at": "2025-10-27T14:30:00Z"
    }
  ],
  "summary": {
    "total_bookings": 15,
    "upcoming_bookings": 2,
    "completed_bookings": 12,
    "cancelled_bookings": 1
  }
}
```

---

## 8. Review & Rating API

### 8.1 Submit Review

**Endpoint:** `POST /reviews`

**Description:** Submit a review for a completed stay.

**Request Body:**
```json
{
  "booking_id": "b123e4567-e89b-12d3-a456-426614174000",
  "hotel_id": "h123e4567-e89b-12d3-a456-426614174000",
  "overall_rating": 4.5,
  "ratings": {
    "cleanliness": 5.0,
    "service": 4.0,
    "value": 4.0,
    "location": 5.0,
    "amenities": 4.0
  },
  "title": "Excellent stay in the heart of the city",
  "comment": "The hotel exceeded our expectations. The room was spacious and clean, staff was very helpful, and the location was perfect for exploring the city.",
  "recommend": true,
  "stay_purpose": "leisure",
  "room_type": "Deluxe King Room",
  "traveled_with": "couple",
  "anonymous": false
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "review_id": "rev_123e4567-e89b-12d3-a456-426614174000",
    "status": "published",
    "helpful_votes": 0,
    "created_at": "2025-10-27T16:30:00Z"
  }
}
```

### 8.2 Get Hotel Reviews

**Endpoint:** `GET /hotels/{hotel_id}/reviews`

**Description:** Get reviews for a specific hotel.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `rating` | number | Filter by minimum rating |
| `sort` | string | Sort by date, rating, or helpfulness |
| `verified_only` | boolean | Show only verified reviews |
| `page` | integer | Page number |
| `per_page` | integer | Items per page |

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "review_id": "rev_123e4567-e89b-12d3-a456-426614174000",
      "guest_name": "John D.",
      "overall_rating": 4.5,
      "ratings": {
        "cleanliness": 5.0,
        "service": 4.0,
        "value": 4.0,
        "location": 5.0,
        "amenities": 4.0
      },
      "title": "Excellent stay in the heart of the city",
      "comment": "The hotel exceeded our expectations. The room was spacious and clean, staff was very helpful, and the location was perfect for exploring the city.",
      "recommend": true,
      "verified_stay": true,
      "stay_date": "2025-11-15",
      "helpful_votes": 12,
      "created_at": "2025-11-20T10:30:00Z"
    }
  ],
  "summary": {
    "total_reviews": 1247,
    "average_rating": 4.3,
    "rating_distribution": {
      "5": 534,
      "4": 423,
      "3": 201,
      "2": 67,
      "1": 22
    }
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 63
  }
}
```

### 8.3 Update Review

**Endpoint:** `PUT /reviews/{review_id}`

**Description:** Update an existing review (within 30 days of posting).

**Request Body:**
```json
{
  "overall_rating": 5.0,
  "title": "Outstanding experience - Updated review",
  "comment": "After reflecting on our stay, I wanted to update my review. The attention to detail and exceptional service truly made this an outstanding experience.",
  "ratings": {
    "cleanliness": 5.0,
    "service": 5.0,
    "value": 4.5,
    "location": 5.0,
    "amenities": 4.5
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "review_id": "rev_123e4567-e89b-12d3-a456-426614174000",
    "updated_at": "2025-10-27T16:45:00Z",
    "changes_made": ["overall_rating", "title", "comment", "ratings"]
  }
}
```

### 8.4 Delete Review

**Endpoint:** `DELETE /reviews/{review_id}`

**Description:** Delete a review (only by the reviewer within 30 days).

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "review_id": "rev_123e4567-e89b-12d3-a456-426614174000",
    "status": "deleted",
    "deleted_at": "2025-10-27T17:00:00Z"
  }
}
```

### 8.5 Get Review Statistics

**Endpoint:** `GET /reviews/statistics`

**Description:** Get aggregated review statistics for reporting.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `hotel_id` | string | Filter by specific hotel |
| `from_date` | date | Reviews from this date |
| `to_date` | date | Reviews until this date |

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "total_reviews": 15234,
    "average_rating": 4.2,
    "rating_distribution": {
      "5": 6234,
      "4": 5123,
      "3": 2345,
      "2": 987,
      "1": 545
    },
    "review_trends": {
      "monthly_growth": 12.5,
      "response_rate": 89.2,
      "average_response_time": "18 hours"
    },
    "top_mentioned_topics": [
      {
        "topic": "location",
        "mention_count": 8934,
        "sentiment": "positive"
      },
      {
        "topic": "cleanliness",
        "mention_count": 7654,
        "sentiment": "positive"
      }
    ]
  }
}
```

---

## 9. Loyalty Program API

### 9.1 Get Loyalty Points

**Endpoint:** `GET /loyalty/points`

**Description:** Get current loyalty points balance and details.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "member_id": "LM123456789",
    "points_balance": 12450,
    "tier": "Gold",
    "lifetime_points": 45230,
    "points_expiring": [
      {
        "points": 500,
        "expiry_date": "2025-12-31"
      }
    ],
    "earning_rate": {
      "base_rate": 10,
      "current_multiplier": 1.25,
      "effective_rate": 12.5
    }
  }
}
```

### 9.2 Redeem Points

**Endpoint:** `POST /loyalty/redeem`

**Description:** Redeem loyalty points for rewards.

**Request Body:**
```json
{
  "redemption_type": "free_night",
  "points_to_redeem": 15000,
  "hotel_id": "h123e4567-e89b-12d3-a456-426614174000",
  "redemption_date": "2025-12-15"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "redemption_id": "red_123e4567-e89b-12d3-a456-426614174000",
    "points_redeemed": 15000,
    "reward_type": "free_night",
    "certificate_number": "FN-2025-123456",
    "expiry_date": "2026-10-27",
    "remaining_balance": 12450,
    "processed_at": "2025-10-27T16:45:00Z"
  }
}
```

### 9.3 Get Loyalty Tier

**Endpoint:** `GET /loyalty/tier`

**Description:** Get current loyalty tier information and benefits.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "current_tier": "Gold",
    "member_since": "2023-05-10",
    "tier_benefits": [
      "25% bonus points",
      "Room upgrades",
      "Late checkout",
      "Welcome amenity",
      "Priority customer support"
    ],
    "next_tier": "Platinum",
    "requirements": {
      "nights_needed": 32,
      "points_needed": 12550,
      "current_progress": {
        "nights": 18,
        "points": 12450
      }
    },
    "tier_expiry": "2025-12-31",
    "requalification_progress": {
      "nights_this_year": 18,
      "nights_required": 25,
      "progress_percentage": 72
    }
  }
}
```

### 9.4 Get Points History

**Endpoint:** `GET /loyalty/points/history`

**Description:** Get detailed points earning and redemption history.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `transaction_type` | string | Filter by earned/redeemed/expired |
| `from_date` | date | Transactions from this date |
| `to_date` | date | Transactions until this date |
| `page` | integer | Page number |

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "transaction_id": "txn_points_123456",
      "type": "earned",
      "points": 1047,
      "description": "Stay at Grand Plaza Hotel New York",
      "booking_reference": "HBS-2025-001234",
      "date": "2025-11-18",
      "base_points": 897,
      "bonus_points": 150,
      "bonus_reason": "Gold member 25% bonus"
    }
  ],
  "summary": {
    "total_earned": 18750,
    "total_redeemed": 6300,
    "current_balance": 12450
  }
}
```

### 9.5 Transfer Points

**Endpoint:** `POST /loyalty/transfer`

**Description:** Transfer points to another loyalty member.

**Request Body:**
```json
{
  "recipient_member_id": "LM987654321",
  "points_to_transfer": 1000,
  "message": "Happy Birthday! Enjoy your stay!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "transfer_id": "trans_123e4567-e89b-12d3-a456-426614174000",
    "points_transferred": 1000,
    "transfer_fee": 50,
    "net_points_deducted": 1050,
    "recipient": {
      "member_id": "LM987654321",
      "name": "Jane Smith"
    },
    "remaining_balance": 11400,
    "processed_at": "2025-10-27T17:15:00Z"
  }
}
```

---

## 10. Admin API

### 10.1 Hotel Management

**Endpoint:** `POST /admin/hotels`

**Description:** Add a new hotel to the system.

**Authorization:** Required - Admin role

**Request Body:**
```json
{
  "name": "Seaside Resort & Spa",
  "description": "Luxury beachfront resort with world-class amenities",
  "address": {
    "street": "456 Ocean Drive",
    "city": "Miami Beach",
    "state": "FL",
    "postal_code": "33139",
    "country": "USA"
  },
  "contact": {
    "phone": "+1-305-555-0199",
    "email": "reservations@seasideresort.com",
    "website": "https://www.seasideresort.com"
  },
  "coordinates": {
    "latitude": 25.7617,
    "longitude": -80.1918
  },
  "star_rating": 5,
  "amenities": [
    "pool", "spa", "fitness_center", "restaurant", 
    "bar", "beach_access", "valet_parking"
  ],
  "policies": {
    "check_in_time": "15:00",
    "check_out_time": "11:00",
    "cancellation_policy": "Free cancellation until 18:00 day before arrival",
    "pet_policy": "Pets allowed with additional fee"
  },
  "status": "active"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "hotel_id": "h789e0123-e89b-12d3-a456-426614174000",
    "status": "pending_verification",
    "created_at": "2025-10-27T17:00:00Z"
  }
}
```

### 10.2 Room Management

**Endpoint:** `POST /admin/hotels/{hotel_id}/rooms`

**Description:** Add rooms to a hotel.

**Authorization:** Required - Admin role

**Request Body:**
```json
{
  "room_type": "Deluxe Ocean View Suite",
  "room_numbers": ["1001", "1002", "1003"],
  "max_occupancy": 4,
  "bed_configuration": "1 King Bed + 1 Sofa Bed",
  "room_size": 65,
  "amenities": ["balcony", "ocean_view", "minibar", "safe"],
  "base_rate": 450.00
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "rooms_created": 3,
    "room_ids": [
      "r789e0123-e89b-12d3-a456-426614174001",
      "r789e0123-e89b-12d3-a456-426614174002", 
      "r789e0123-e89b-12d3-a456-426614174003"
    ]
  }
}
```

### 10.3 Booking Management

**Endpoint:** `GET /admin/bookings`

**Description:** Get all bookings with admin-level details.

**Authorization:** Required - Admin role

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by booking status |
| `hotel_id` | string | Filter by specific hotel |
| `from_date` | date | Bookings from this date |
| `to_date` | date | Bookings until this date |

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "booking_id": "b123e4567-e89b-12d3-a456-426614174000",
      "booking_reference": "HBS-2025-001234",
      "status": "confirmed",
      "guest": {
        "guest_id": "g123e4567-e89b-12d3-a456-426614174000",
        "name": "John Doe",
        "email": "john.doe@example.com"
      },
      "hotel": {
        "hotel_id": "h123e4567-e89b-12d3-a456-426614174000",
        "name": "Grand Plaza Hotel New York"
      },
      "financial": {
        "total_amount": 1079.64,
        "commission": 107.96,
        "net_amount": 971.68,
        "currency": "USD"
      },
      "created_at": "2025-10-27T14:30:00Z"
    }
  ],
  "summary": {
    "total_bookings": 15432,
    "total_revenue": 8567432.15
  }
}
```

### 10.4 User Management

**Endpoint:** `GET /admin/users`

**Description:** Get user accounts with admin privileges.

**Authorization:** Required - Admin role

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "user_id": "u123e4567-e89b-12d3-a456-426614174000",
      "email": "john.doe@example.com",
      "name": "John Doe",
      "status": "active",
      "role": "guest",
      "created_at": "2023-05-10T09:15:00Z",
      "last_login": "2025-10-27T12:30:00Z",
      "booking_count": 15,
      "total_spent": 15432.50
    }
  ]
}
```

### 10.5 Analytics & Reports

**Endpoint:** `POST /admin/reports/generate`

**Description:** Generate custom reports.

**Authorization:** Required - Admin role

**Request Body:**
```json
{
  "report_type": "occupancy",
  "date_range": {
    "from": "2025-10-01",
    "to": "2025-10-31"
  },
  "filters": {
    "hotel_ids": ["h123e4567-e89b-12d3-a456-426614174000"]
  },
  "format": "pdf"
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "data": {
    "report_id": "rpt_123e4567-e89b-12d3-a456-426614174000",
    "status": "generating",
    "estimated_completion": "2025-10-27T17:15:00Z"
  }
}
```

---

## 11. Integration API

### 11.1 OTA Integration

**Endpoint:** `POST /integration/ota/sync`

**Description:** Synchronize inventory and rates with OTA partners.

**Authorization:** Required - Integration role

**Request Body:**
```json
{
  "hotel_id": "h123e4567-e89b-12d3-a456-426614174000",
  "ota_partner": "booking.com",
  "sync_type": "rates_and_inventory",
  "date_range": {
    "from": "2025-11-01",
    "to": "2025-12-31"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "sync_id": "sync_123e4567-e89b-12d3-a456-426614174000",
    "status": "in_progress",
    "rooms_synced": 45,
    "rates_updated": 450,
    "started_at": "2025-10-27T17:30:00Z"
  }
}
```

### 11.2 Channel Manager

**Endpoint:** `PUT /integration/channels/rates`

**Description:** Update rates across all distribution channels.

**Authorization:** Required - Integration role

**Request Body:**
```json
{
  "hotel_id": "h123e4567-e89b-12d3-a456-426614174000",
  "room_type_id": "rt123e4567-e89b-12d3-a456-426614174000",
  "rate_updates": [
    {
      "date": "2025-11-15",
      "base_rate": 320.00,
      "channels": ["direct", "booking.com", "expedia"]
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "update_id": "upd_123e4567-e89b-12d3-a456-426614174000",
    "channels_updated": 3,
    "rates_updated": 1,
    "status": "completed"
  }
}
```

### 11.3 Payment Gateway

**Endpoint:** `POST /integration/payments/webhook`

**Description:** Receive payment status updates from payment gateways.

**Request Body:**
```json
{
  "event_type": "payment.completed",
  "payment_id": "pay_123e4567-e89b-12d3-a456-426614174000",
  "transaction_id": "txn_987654321",
  "amount": 1079.64,
  "currency": "USD",
  "status": "succeeded",
  "gateway": "stripe",
  "timestamp": "2025-10-27T14:30:00Z"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "processed": true,
    "booking_updated": true
  }
}
```

### 11.4 Webhook Endpoints

**Endpoint:** `POST /webhooks/booking-created`

**Description:** Webhook for booking creation events.

**Request Headers:**
```
X-Webhook-Signature: sha256=abc123def456...
Content-Type: application/json
```

**Request Body:**
```json
{
  "event": "booking.created",
  "data": {
    "booking_id": "b123e4567-e89b-12d3-a456-426614174000",
    "booking_reference": "HBS-2025-001234",
    "hotel_id": "h123e4567-e89b-12d3-a456-426614174000",
    "guest_email": "john.doe@example.com",
    "total_amount": 1079.64,
    "check_in": "2025-11-15",
    "check_out": "2025-11-18"
  },
  "timestamp": "2025-10-27T14:30:00Z"
}
```

### 11.5 Third-Party Services

**Endpoint:** `GET /integration/services/status`

**Description:** Check status of integrated third-party services.

**Authorization:** Required - Integration role

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "services": [
      {
        "service": "stripe",
        "status": "healthy",
        "last_check": "2025-10-27T17:45:00Z",
        "response_time": 120
      },
      {
        "service": "booking.com_api",
        "status": "healthy",
        "last_check": "2025-10-27T17:45:00Z",
        "response_time": 250
      },
      {
        "service": "sendgrid",
        "status": "degraded",
        "last_check": "2025-10-27T17:45:00Z",
        "response_time": 1200
      }
    ]
  }
}
```

---

## 12. Notification API

### 12.1 Send Email Notification

**Endpoint:** `POST /notifications/email`

**Description:** Send email notifications to users.

**Authorization:** Required - Admin or System role

**Request Body:**
```json
{
  "to": "john.doe@example.com",
  "template": "booking_confirmation",
  "data": {
    "guest_name": "John Doe",
    "booking_reference": "HBS-2025-001234",
    "hotel_name": "Grand Plaza Hotel New York",
    "check_in": "2025-11-15",
    "check_out": "2025-11-18"
  },
  "priority": "high"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message_id": "msg_123e4567-e89b-12d3-a456-426614174000",
    "status": "sent",
    "sent_at": "2025-10-27T14:30:00Z"
  }
}
```

### 12.2 Send SMS Notification

**Endpoint:** `POST /notifications/sms`

**Description:** Send SMS notifications to users.

**Authorization:** Required - Admin or System role

**Request Body:**
```json
{
  "to": "+1-555-123-4567",
  "message": "Your booking HBS-2025-001234 is confirmed. Check-in: Nov 15, 2025 at Grand Plaza Hotel New York.",
  "booking_id": "b123e4567-e89b-12d3-a456-426614174000"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message_id": "sms_123e4567-e89b-12d3-a456-426614174000",
    "status": "sent",
    "sent_at": "2025-10-27T14:30:00Z",
    "cost": 0.05
  }
}
```

### 12.3 Push Notification

**Endpoint:** `POST /notifications/push`

**Description:** Send push notifications to mobile apps.

**Authorization:** Required - Admin or System role

**Request Body:**
```json
{
  "user_id": "u123e4567-e89b-12d3-a456-426614174000",
  "title": "Booking Confirmed",
  "body": "Your reservation at Grand Plaza Hotel New York is confirmed!",
  "data": {
    "booking_id": "b123e4567-e89b-12d3-a456-426614174000",
    "action": "view_booking"
  },
  "badge": 1
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "notification_id": "push_123e4567-e89b-12d3-a456-426614174000",
    "status": "sent",
    "devices_reached": 2,
    "sent_at": "2025-10-27T14:30:00Z"
  }
}
```

### 12.4 Get Notification Preferences

**Endpoint:** `GET /notifications/preferences`

**Description:** Get user notification preferences.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "email": {
      "booking_confirmations": true,
      "booking_reminders": true,
      "promotional": false,
      "newsletter": true
    },
    "sms": {
      "booking_confirmations": true,
      "booking_reminders": false,
      "promotional": false
    },
    "push": {
      "booking_updates": true,
      "promotional": false,
      "location_based": true
    }
  }
}
```

### 12.5 Update Notification Preferences

**Endpoint:** `PUT /notifications/preferences`

**Description:** Update user notification preferences.

**Request Body:**
```json
{
  "email": {
    "promotional": true,
    "newsletter": false
  },
  "sms": {
    "booking_reminders": true
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "updated_at": "2025-10-27T17:30:00Z",
    "preferences_updated": ["email.promotional", "email.newsletter", "sms.booking_reminders"]
  }
}
```

---

## 13. API Rate Limiting

### 13.1 Rate Limit Policies

The API implements rate limiting to ensure fair usage and system stability:

| User Type | Requests per Minute | Requests per Hour | Requests per Day |
|-----------|---------------------|-------------------|------------------|
| **Guest** | 100 | 1,000 | 10,000 |
| **Authenticated** | 200 | 5,000 | 50,000 |
| **Premium** | 500 | 10,000 | 100,000 |
| **Integration** | 1,000 | 20,000 | 200,000 |

**Rate Limit Windows:**
- Per minute: Rolling 60-second window
- Per hour: Rolling 3600-second window  
- Per day: Rolling 24-hour window

### 13.2 Rate Limit Headers

All API responses include rate limiting headers:

```http
X-RateLimit-Limit: 200
X-RateLimit-Remaining: 195
X-RateLimit-Reset: 1635724800
X-RateLimit-Window: 60
```

**Header Descriptions:**
- `X-RateLimit-Limit`: Maximum requests allowed in the time window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when the rate limit resets
- `X-RateLimit-Window`: Time window in seconds

### 13.3 Handling Rate Limits

When rate limits are exceeded, the API returns:

**Response (429 Too Many Requests):**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 45 seconds.",
    "details": {
      "limit": 200,
      "window": "60 seconds",
      "reset_at": "2025-10-27T17:45:00Z"
    }
  }
}
```

**Best Practices:**
- Implement exponential backoff
- Monitor rate limit headers
- Cache responses when possible
- Use webhooks for real-time updates instead of polling

---

## 14. API Versioning

### 14.1 Versioning Strategy

The API uses semantic versioning (SemVer) with the following format:

**Current Version:** `v1.2.3`

**Version Format:**
- **Major (v1)**: Breaking changes
- **Minor (v1.2)**: New features, backwards compatible
- **Patch (v1.2.3)**: Bug fixes, backwards compatible

**Version Specification:**
```http
# Header-based versioning (recommended)
API-Version: v1.2.3

# URL-based versioning (alternative)
GET /v1/hotels
```

### 14.2 Deprecation Policy

**Deprecation Timeline:**
1. **Announcement**: 6 months before deprecation
2. **Deprecation Warning**: 3 months before removal
3. **Sunset**: Feature/version removed

**Deprecation Headers:**
```http
Sunset: Wed, 27 Oct 2026 17:00:00 GMT
Deprecation: Wed, 27 Apr 2025 17:00:00 GMT
Link: <https://api.hotelbooking.com/v2/hotels>; rel="successor-version"
```

### 14.3 Migration Guide

**Migrating from v1.1 to v1.2:**

**Changes:**
- Added `guest_preferences` field to booking responses
- Enhanced error response format
- New loyalty program endpoints

**Breaking Changes (None in v1.2):**
- No breaking changes in this minor version

**New Features:**
```json
// New guest preferences in booking response
{
  "booking_id": "b123...",
  "guest_preferences": {
    "room_type": "king",
    "floor_preference": "high"
  }
}
```

---

## 15. Testing & Sandbox

### 15.1 Sandbox Environment

**Base URL:** `https://sandbox-api.hotelbooking.com`

**Features:**
- Full API functionality with test data
- No real transactions or charges
- Rate limits: 10x higher than production
- Data reset: Every Sunday at 00:00 UTC

**Test Credentials:**
```json
{
  "client_id": "test_client_123",
  "client_secret": "test_secret_456",
  "api_key": "test_key_789"
}
```

### 15.2 Test Data

**Test Hotel IDs:**
- `h_test_001`: Grand Plaza Test Hotel
- `h_test_002`: Seaside Test Resort
- `h_test_003`: Mountain View Test Lodge

**Test Payment Methods:**
```json
{
  "success_card": {
    "number": "4242424242424242",
    "exp_month": 12,
    "exp_year": 2030,
    "cvc": "123"
  },
  "decline_card": {
    "number": "4000000000000002",
    "exp_month": 12,
    "exp_year": 2030,
    "cvc": "123"
  }
}
```

### 15.3 Postman Collection

**Collection URL:** 
`https://www.postman.com/hotelbooking-api/workspace/public/collection/hotel-booking-api`

**Environment Variables:**
```json
{
  "base_url": "{{base_url}}",
  "api_key": "{{api_key}}",
  "hotel_id": "{{test_hotel_id}}",
  "guest_id": "{{test_guest_id}}"
}
```

### 15.4 API Testing Tools

**Recommended Testing Tools:**
- **Postman**: API testing and documentation
- **Insomnia**: REST client for API testing
- **curl**: Command-line HTTP client
- **Newman**: Command-line Postman collection runner

**Example curl Request:**
```bash
curl -X GET "https://sandbox-api.hotelbooking.com/hotels/search" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "New York",
    "check_in": "2025-12-01",
    "check_out": "2025-12-03",
    "adults": 2
  }'
```

---

## Appendix

### A. Status Codes

| Status Code | Description | Usage |
|-------------|-------------|-------|
| **200** | OK | Successful GET, PUT, PATCH |
| **201** | Created | Successful POST |
| **204** | No Content | Successful DELETE |
| **400** | Bad Request | Invalid request data |
| **401** | Unauthorized | Missing or invalid authentication |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource not found |
| **409** | Conflict | Resource conflict (duplicate) |
| **422** | Unprocessable Entity | Validation errors |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Server Error | Server error |
| **502** | Bad Gateway | Upstream service error |
| **503** | Service Unavailable | Temporary service unavailable |

### B. Error Codes Reference

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_API_KEY` | 401 | API key is missing or invalid |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required permissions |
| `HOTEL_NOT_FOUND` | 404 | Specified hotel does not exist |
| `ROOM_NOT_AVAILABLE` | 409 | Room not available for selected dates |
| `INVALID_DATE_RANGE` | 422 | Check-in date must be before check-out |
| `PAYMENT_FAILED` | 422 | Payment processing failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `BOOKING_NOT_CANCELLABLE` | 409 | Booking cannot be cancelled |
| `INVALID_GUEST_COUNT` | 422 | Guest count exceeds room capacity |

### C. Data Models & Schemas

**Hotel Schema:**
```json
{
  "hotel_id": "string (UUID)",
  "name": "string (max 255)",
  "description": "string (max 2000)",
  "star_rating": "integer (1-5)",
  "address": {
    "street": "string (max 255)",
    "city": "string (max 100)",
    "state": "string (max 100)",
    "postal_code": "string (max 20)",
    "country": "string (ISO 3166-1 alpha-3)"
  },
  "coordinates": {
    "latitude": "number (-90 to 90)",
    "longitude": "number (-180 to 180)"
  },
  "amenities": "array of strings",
  "images": "array of image objects",
  "policies": "policy object",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

**Booking Schema:**
```json
{
  "booking_id": "string (UUID)",
  "booking_reference": "string (HBS-YYYY-NNNNNN)",
  "status": "enum [pending, confirmed, cancelled, completed]",
  "hotel_id": "string (UUID)",
  "room_id": "string (UUID)",
  "guest_id": "string (UUID)",
  "check_in": "string (YYYY-MM-DD)",
  "check_out": "string (YYYY-MM-DD)",
  "guests": {
    "adults": "integer (min 1, max 10)",
    "children": "integer (min 0, max 8)"
  },
  "total_amount": "number (decimal, 2 places)",
  "currency": "string (ISO 4217)",
  "payment_status": "enum [pending, paid, refunded]",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

### D. API Changelog

**Version 1.2.3** (2025-10-27)
- Added guest preferences to booking responses
- Enhanced error messages with more detailed descriptions
- Fixed loyalty points calculation for international bookings

**Version 1.2.2** (2025-10-15)
- Added new amenity codes for accessibility features
- Improved rate limiting for high-volume integrations
- Bug fix: Resolved timezone issues in booking confirmations

**Version 1.2.1** (2025-10-01)
- Added support for group bookings (5+ rooms)
- Enhanced search filters for business travelers
- Performance improvements for hotel search API

**Version 1.2.0** (2025-09-15)
- **New Features:**
  - Loyalty program API endpoints
  - Guest preference management
  - Enhanced review system with sentiment analysis
- **Improvements:**
  - Faster response times for search APIs
  - Better error handling for payment failures

### E. Code Examples

**JavaScript/Node.js Example:**
```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'https://api.hotelbooking.com',
  headers: {
    'Authorization': `Bearer ${process.env.API_KEY}`,
    'Content-Type': 'application/json'
  }
});

// Search for hotels
async function searchHotels(params) {
  try {
    const response = await api.post('/hotels/search', params);
    return response.data;
  } catch (error) {
    console.error('Search failed:', error.response.data);
    throw error;
  }
}

// Create a booking
async function createBooking(bookingData) {
  try {
    const response = await api.post('/bookings', bookingData);
    return response.data;
  } catch (error) {
    console.error('Booking failed:', error.response.data);
    throw error;
  }
}
```

**Python Example:**
```python
import requests
import os

class HotelBookingAPI:
    def __init__(self):
        self.base_url = "https://api.hotelbooking.com"
        self.headers = {
            "Authorization": f"Bearer {os.environ['API_KEY']}",
            "Content-Type": "application/json"
        }
    
    def search_hotels(self, search_params):
        response = requests.post(
            f"{self.base_url}/hotels/search",
            json=search_params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_booking(self, booking_data):
        response = requests.post(
            f"{self.base_url}/bookings",
            json=booking_data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Usage
api = HotelBookingAPI()
hotels = api.search_hotels({
    "location": "New York",
    "check_in": "2025-12-01",
    "check_out": "2025-12-03",
    "adults": 2
})
```

**PHP Example:**
```php
<?php
class HotelBookingAPI {
    private $baseUrl = 'https://api.hotelbooking.com';
    private $apiKey;
    
    public function __construct($apiKey) {
        $this->apiKey = $apiKey;
    }
    
    public function searchHotels($params) {
        $curl = curl_init();
        
        curl_setopt_array($curl, [
            CURLOPT_URL => $this->baseUrl . '/hotels/search',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($params),
            CURLOPT_HTTPHEADER => [
                'Authorization: Bearer ' . $this->apiKey,
                'Content-Type: application/json'
            ]
        ]);
        
        $response = curl_exec($curl);
        curl_close($curl);
        
        return json_decode($response, true);
    }
}

// Usage
$api = new HotelBookingAPI(getenv('API_KEY'));
$hotels = $api->searchHotels([
    'location' => 'New York',
    'check_in' => '2025-12-01',
    'check_out' => '2025-12-03',
    'adults' => 2
]);
?>
```

---

**End of API Reference Documentation**

For additional support or questions, please contact:
- **Technical Support**: api-support@hotelbooking.com
- **Documentation**: docs@hotelbooking.com
- **Business Inquiries**: partnerships@hotelbooking.com

**Last Updated:** October 27, 2025  
**API Version:** v1.2.3
