# API Reference

Complete API documentation for GitHire Backend.

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints except `/auth/register` and `/auth/login` require JWT authentication.

Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Response Format

### Success Response
```json
{
  "data": { ... },
  "status": "success"
}
```

### Error Response
```json
{
  "detail": "Error message",
  "type": "error_type",
  "errors": [ ... ]  // Optional validation errors
}
```

## Status Codes

- `200 OK` - Successful GET/PUT/DELETE request
- `201 Created` - Successful POST request
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## Authentication Endpoints

### Register User

Create a new user account.

**Endpoint**: `POST /auth/register`

**Authentication**: None

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Validation**:
- `email`: Valid email format
- `password`: Minimum 8 characters, maximum 100 characters

**Response** (`201 Created`):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": null,
  "created_at": "2025-10-10T12:00:00.000Z"
}
```

**Errors**:
- `400` - Email already registered

**Example**:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```

---

### Login

Authenticate and receive JWT token.

**Endpoint**: `POST /auth/login`

**Authentication**: None

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response** (`200 OK`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors**:
- `401` - Invalid email or password

**Example**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```

---

### Logout

Invalidate current session.

**Endpoint**: `POST /auth/logout`

**Authentication**: Required

**Request Body**: None

**Response** (`200 OK`):
```json
{
  "message": "Successfully logged out"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer <token>"
```

---

### Get Current User Profile

Get authenticated user's profile information.

**Endpoint**: `GET /auth/me`

**Authentication**: Required

**Response** (`200 OK`):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-10-10T12:00:00.000Z",
  "last_login": "2025-10-10T14:30:00.000Z"
}
```

**Example**:
```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer <token>"
```

---

### Update User Profile

Update user's profile information.

**Endpoint**: `PUT /auth/me`

**Authentication**: Required

**Request Body**:
```json
{
  "name": "John Doe"
}
```

**Validation**:
- `name`: Minimum 1 character, maximum 255 characters

**Response** (`200 OK`):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-10-10T12:00:00.000Z",
  "last_login": "2025-10-10T14:30:00.000Z"
}
```

**Example**:
```bash
curl -X PUT http://localhost:8000/auth/me \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe"}'
```

---

## Project Endpoints

### Create Project

Create a new recruitment project.

**Endpoint**: `POST /projects`

**Authentication**: Required

**Request Body**:
```json
{
  "name": "Senior Python Developer Search",
  "job_title": "Senior Python Developer",
  "job_description_text": "Looking for a Senior Python Developer with 5+ years of experience in FastAPI and SQLAlchemy. Must have strong experience with async/await patterns.",
  "location": "San Francisco, CA, USA"
}
```

**Validation**:
- `name`: 1-255 characters
- `job_title`: 1-255 characters
- `job_description_text`: 10-10000 characters
- `location`: Optional, max 500 characters

**Response** (`201 Created`):
```json
{
  "project_id": "660e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Senior Python Developer Search",
  "job_title": "Senior Python Developer",
  "status": "draft",
  "job_description_text": "Looking for a Senior Python Developer...",
  "location": "San Francisco, CA, USA",
  "candidate_count": 0,
  "avg_score": null,
  "created_at": "2025-10-10T12:00:00.000Z",
  "updated_at": "2025-10-10T12:00:00.000Z",
  "pipeline_start_time": null,
  "pipeline_end_time": null,
  "results_json": null
}
```

---

### List Projects

Get all projects for authenticated user.

**Endpoint**: `GET /projects`

**Authentication**: Required

**Query Parameters**:
- `limit`: Optional, default 50, max 100
- `offset`: Optional, default 0

**Response** (`200 OK`):
```json
{
  "projects": [
    {
      "project_id": "660e8400-e29b-41d4-a716-446655440000",
      "name": "Senior Python Developer Search",
      "job_title": "Senior Python Developer",
      "status": "ranked",
      "job_description_text": "Looking for a Senior Python Developer...",
      "candidate_count": 25,
      "avg_score": 72.5,
      "created_at": "2025-10-10T12:00:00.000Z",
      "updated_at": "2025-10-10T12:30:00.000Z",
      "pipeline_start_time": "2025-10-10T12:10:00.000Z",
      "pipeline_end_time": "2025-10-10T12:15:00.000Z"
    }
  ],
  "total": 1
}
```

**Example**:
```bash
curl "http://localhost:8000/projects?limit=10&offset=0" \
  -H "Authorization: Bearer <token>"
```

---

### Get Project Details

Get detailed information about a specific project.

**Endpoint**: `GET /projects/{project_id}`

**Authentication**: Required

**Response** (`200 OK`):
```json
{
  "project_id": "660e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Senior Python Developer Search",
  "job_title": "Senior Python Developer",
  "status": "ranked",
  "job_description_text": "Looking for a Senior Python Developer...",
  "location": "San Francisco, CA, USA",
  "candidate_count": 25,
  "avg_score": 72.5,
  "created_at": "2025-10-10T12:00:00.000Z",
  "updated_at": "2025-10-10T12:30:00.000Z",
  "pipeline_start_time": "2025-10-10T12:10:00.000Z",
  "pipeline_end_time": "2025-10-10T12:15:00.000Z",
  "results_json": {
    "candidates": [...],
    "ranked_candidates": [...],
    "metadata": {...}
  }
}
```

**Errors**:
- `404` - Project not found
- `403` - Not authorized to access this project

---

### Delete Project

Delete a project and all associated data.

**Endpoint**: `DELETE /projects/{project_id}`

**Authentication**: Required

**Response** (`200 OK`):
```json
{
  "message": "Project deleted successfully"
}
```

**Errors**:
- `404` - Project not found
- `403` - Not authorized to delete this project

---

## Multi-Stage Workflow Endpoints

### Source Candidates

Run candidate sourcing for a project (Module 002).

**Endpoint**: `POST /workflow/projects/{project_id}/source`

**Authentication**: Required

**Response** (`200 OK`):
```json
{
  "project_id": "660e8400-e29b-41d4-a716-446655440000",
  "status": "sourced",
  "candidates": [
    {
      "github_username": "johnsmith",
      "profile_url": "https://github.com/johnsmith",
      "bio": "Python developer interested in web frameworks",
      "location": "San Francisco, CA",
      "email": "john@example.com",
      "company": "Tech Corp",
      "public_repos": 45,
      "followers": 230,
      "following": 120,
      "created_at": "2018-01-15T00:00:00.000Z",
      "detected_skills": {
        "Python": {"confidence": 0.95, "signals": ["repos", "languages"]},
        "FastAPI": {"confidence": 0.85, "signals": ["repos", "readme"]}
      },
      "top_languages": ["Python", "JavaScript", "TypeScript"],
      "top_repositories": [...]
    }
  ],
  "candidate_count": 25
}
```

**Errors**:
- `404` - Project not found
- `400` - Project already sourced

---

### Rank Candidates

Run candidate ranking for a project (Module 003).

**Endpoint**: `POST /workflow/projects/{project_id}/rank`

**Authentication**: Required

**Response** (`200 OK`):
```json
{
  "project_id": "660e8400-e29b-41d4-a716-446655440000",
  "status": "ranked",
  "ranked_candidates": [
    {
      "github_username": "johnsmith",
      "rank": 1,
      "total_score": 85.5,
      "skill_match_score": 90.0,
      "experience_score": 82.0,
      "activity_score": 88.0,
      "domain_score": 82.0,
      "score_breakdown": {
        "skills_detail": {...},
        "experience_detail": {...},
        "activity_detail": {...},
        "domain_detail": {...}
      },
      ...candidate_fields...
    }
  ],
  "avg_score": 72.5
}
```

**Errors**:
- `404` - Project not found
- `400` - Project not sourced yet

---

### Shortlist Candidates

Mark selected candidates for shortlist.

**Endpoint**: `POST /workflow/projects/{project_id}/shortlist`

**Authentication**: Required

**Request Body**:
```json
{
  "candidate_usernames": ["johnsmith", "janedoe", "bobsmith"]
}
```

**Validation**:
- `candidate_usernames`: Array of at least 1 username

**Response** (`200 OK`):
```json
{
  "project_id": "660e8400-e29b-41d4-a716-446655440000",
  "status": "shortlisted",
  "shortlisted_count": 3
}
```

---

### Get Shortlisted Candidates

Get all shortlisted candidates for a project.

**Endpoint**: `GET /workflow/projects/{project_id}/shortlisted`

**Authentication**: Required

**Response** (`200 OK`):
```json
{
  "project_id": "660e8400-e29b-41d4-a716-446655440000",
  "shortlisted_candidates": [
    {
      "shortlist_id": "770e8400-e29b-41d4-a716-446655440000",
      "project_id": "660e8400-e29b-41d4-a716-446655440000",
      "github_username": "johnsmith",
      "candidate_data": {...},
      "enriched_data": {...},
      "enrichment_status": "completed",
      "enriched_at": "2025-10-10T12:20:00.000Z",
      "created_at": "2025-10-10T12:15:00.000Z"
    }
  ],
  "total": 3
}
```

---

### Toggle Shortlist

Add or remove a candidate from shortlist.

**Endpoint**: `POST /workflow/projects/{project_id}/candidates/{github_username}/toggle-shortlist`

**Authentication**: Required

**Response** (`200 OK`):
```json
{
  "project_id": "660e8400-e29b-41d4-a716-446655440000",
  "github_username": "johnsmith",
  "is_shortlisted": true,
  "shortlisted_count": 4
}
```

---

### Enrich Candidate

Fetch additional profile data for a shortlisted candidate.

**Endpoint**: `POST /workflow/projects/{project_id}/enrich/{github_username}`

**Authentication**: Required

**Response** (`200 OK`):
```json
{
  "shortlist_id": "770e8400-e29b-41d4-a716-446655440000",
  "github_username": "johnsmith",
  "enrichment_status": "completed",
  "enriched_data": {
    "additional_repos": [...],
    "recent_activity": [...],
    "contribution_stats": {...}
  },
  "enriched_at": "2025-10-10T12:20:00.000Z"
}
```

---

## Outreach Endpoints

### Generate Outreach

Generate personalized outreach messages for a candidate (Module 004).

**Endpoint**: `POST /outreach/{project_id}/{github_username}`

**Authentication**: Required

**Query Parameters**:
- `channels`: Optional, comma-separated list of channels (email,linkedin,twitter), defaults to all

**Response** (`200 OK`):
```json
{
  "project_id": "660e8400-e29b-41d4-a716-446655440000",
  "github_username": "johnsmith",
  "messages": [
    {
      "outreach_id": "880e8400-e29b-41d4-a716-446655440000",
      "project_id": "660e8400-e29b-41d4-a716-446655440000",
      "github_username": "johnsmith",
      "channel": "email",
      "subject_line": "Exciting Senior Python Opportunity at TechCorp",
      "message_text": "Hi John,\n\nI came across your impressive work on FastAPI-crud-generator...",
      "personalization_score": 87.5,
      "personalization_metadata": {
        "repos_mentioned": ["FastAPI-crud-generator"],
        "personalization_depth": "deep",
        "specific_contributions": true
      },
      "tokens_used": 450,
      "stage_breakdown": {
        "analysis": 150,
        "generation": 250,
        "validation": 50
      },
      "is_edited": false,
      "edited_message": null,
      "edited_at": null,
      "status": "draft",
      "sent_at": null,
      "generated_at": "2025-10-10T12:25:00.000Z"
    }
  ]
}
```

---

### Regenerate Outreach

Regenerate outreach message for a specific channel.

**Endpoint**: `POST /outreach/{project_id}/{github_username}/regenerate/{channel}`

**Authentication**: Required

**Response** (`200 OK`):
```json
{
  "project_id": "660e8400-e29b-41d4-a716-446655440000",
  "github_username": "johnsmith",
  "channel": "email",
  "message": {
    ...outreach_message_object...
  }
}
```

---

### Update Outreach Message

Edit an outreach message.

**Endpoint**: `PUT /outreach/{outreach_id}`

**Authentication**: Required

**Request Body**:
```json
{
  "message_text": "Hi John,\n\nEdited custom message..."
}
```

**Response** (`200 OK`):
```json
{
  "outreach_id": "880e8400-e29b-41d4-a716-446655440000",
  ...updated_message_object...,
  "is_edited": true,
  "edited_message": "Hi John,\n\nEdited custom message...",
  "edited_at": "2025-10-10T12:30:00.000Z"
}
```

---

### Mark Outreach as Sent

Mark an outreach message as sent.

**Endpoint**: `POST /outreach/{outreach_id}/send`

**Authentication**: Required

**Response** (`200 OK`):
```json
{
  "outreach_id": "880e8400-e29b-41d4-a716-446655440000",
  ...message_object...,
  "status": "sent",
  "sent_at": "2025-10-10T12:35:00.000Z"
}
```

---

### Generate Follow-up Sequences

Generate 3-part follow-up sequence for an outreach message.

**Endpoint**: `POST /outreach/{outreach_id}/followups`

**Authentication**: Required

**Response** (`200 OK`):
```json
{
  "outreach_message_id": "880e8400-e29b-41d4-a716-446655440000",
  "follow_ups": [
    {
      "followup_id": "990e8400-e29b-41d4-a716-446655440000",
      "outreach_message_id": "880e8400-e29b-41d4-a716-446655440000",
      "sequence_number": 1,
      "scheduled_days_after": 3,
      "message_text": "Hi John,\n\nJust following up on my previous email...",
      "angle": "reminder",
      "generated_at": "2025-10-10T12:25:00.000Z",
      "sent_at": null
    },
    {
      "sequence_number": 2,
      "scheduled_days_after": 7,
      "angle": "technical_challenge",
      ...
    },
    {
      "sequence_number": 3,
      "scheduled_days_after": 14,
      "angle": "soft_close",
      ...
    }
  ]
}
```

---

## Interactive API Documentation

Visit these URLs when the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

**Last Updated**: 2025-10-10
