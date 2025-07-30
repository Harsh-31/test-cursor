# AI Interviewer - Complete API & WebSocket Endpoints Specification

## 📋 Overview

This document lists all the endpoints that need to be developed by the **Backend & AI Team** for the AI Interviewer system.

## 🔗 REST API Endpoints

### 1. Authentication & User Management

#### `POST /api/v1/auth/login`
**Purpose**: User authentication  
**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
**Response**:
```json
{
  "access_token": "jwt_token_here",
  "refresh_token": "refresh_token_here",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "role": "interviewer|candidate|admin"
  }
}
```

#### `POST /api/v1/auth/refresh`
**Purpose**: Refresh JWT token  
**Request**:
```json
{
  "refresh_token": "refresh_token_here"
}
```

#### `POST /api/v1/auth/logout`
**Purpose**: User logout  
**Headers**: `Authorization: Bearer <token>`

---

### 2. Candidate Management

#### `POST /api/v1/candidates`
**Purpose**: Create new candidate profile  
**Request**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "resume_url": "https://storage.com/resume.pdf",
  "skills": ["Python", "React", "SQL"],
  "experience_years": 3,
  "job_role": "software_engineer"
}
```
**Response**:
```json
{
  "id": "candidate_uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### `GET /api/v1/candidates/{candidate_id}`
**Purpose**: Get candidate details  
**Response**:
```json
{
  "id": "candidate_uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "skills": ["Python", "React", "SQL"],
  "experience_years": 3,
  "resume_url": "https://storage.com/resume.pdf",
  "interview_history": [
    {
      "session_id": "session_uuid",
      "date": "2024-01-15T10:30:00Z",
      "status": "completed",
      "overall_score": 8.5
    }
  ]
}
```

#### `PUT /api/v1/candidates/{candidate_id}`
**Purpose**: Update candidate profile  

#### `GET /api/v1/candidates`
**Purpose**: List all candidates (with pagination)  
**Query Parameters**: `page`, `limit`, `search`, `job_role`

---

### 3. Interview Session Management

#### `POST /api/v1/interviews`
**Purpose**: Create new interview session  
**Request**:
```json
{
  "candidate_id": "candidate_uuid",
  "job_role": "software_engineer",
  "interviewer_id": "interviewer_uuid",
  "scheduled_time": "2024-01-15T14:00:00Z",
  "duration_minutes": 45,
  "interview_type": "technical|behavioral|mixed"
}
```
**Response**:
```json
{
  "session_id": "session_uuid",
  "candidate_id": "candidate_uuid",
  "job_role": "software_engineer",
  "status": "scheduled",
  "websocket_url": "ws://localhost:8000/ws/session_uuid",
  "interview_link": "https://app.com/interview/session_uuid",
  "scheduled_time": "2024-01-15T14:00:00Z"
}
```

#### `GET /api/v1/interviews/{session_id}`
**Purpose**: Get interview session details  
**Response**:
```json
{
  "session_id": "session_uuid",
  "candidate": {
    "id": "candidate_uuid",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "job_role": "software_engineer",
  "status": "in_progress|completed|cancelled",
  "start_time": "2024-01-15T14:00:00Z",
  "end_time": "2024-01-15T14:45:00Z",
  "current_question_index": 5,
  "total_questions": 10,
  "overall_score": 8.5,
  "responses_count": 5
}
```

#### `PUT /api/v1/interviews/{session_id}`
**Purpose**: Update interview session  
**Request**:
```json
{
  "status": "completed|cancelled|paused",
  "end_time": "2024-01-15T14:45:00Z",
  "notes": "Interview completed successfully"
}
```

#### `GET /api/v1/interviews`
**Purpose**: List interview sessions  
**Query Parameters**: `status`, `candidate_id`, `date_from`, `date_to`, `page`, `limit`

#### `DELETE /api/v1/interviews/{session_id}`
**Purpose**: Cancel/delete interview session

---

### 4. Audio Processing

#### `POST /api/v1/audio/speech-to-text`
**Purpose**: Convert audio to text (fallback endpoint)  
**Request**: `multipart/form-data`
```
audio_file: <audio_file.wav>
session_id: "session_uuid"
```
**Response**:
```json
{
  "transcription": "This is the transcribed text",
  "confidence": 0.95,
  "duration": 15.5,
  "language": "en"
}
```

#### `POST /api/v1/audio/text-to-speech`
**Purpose**: Convert text to speech  
**Request**:
```json
{
  "text": "Hello, can you tell me about yourself?",
  "voice": "alloy|echo|fable|onyx|nova|shimmer",
  "speed": 1.0,
  "format": "mp3|wav"
}
```
**Response**: Audio file (binary) or base64 encoded audio

#### `POST /api/v1/audio/upload`
**Purpose**: Upload audio files for processing  
**Request**: `multipart/form-data`
**Response**:
```json
{
  "file_id": "file_uuid",
  "file_url": "https://storage.com/audio/file_uuid.wav",
  "duration": 15.5,
  "size_bytes": 245760
}
```

---

### 5. Question Management

#### `GET /api/v1/questions`
**Purpose**: Get available questions (for manual review/editing)  
**Query Parameters**: `job_role`, `type`, `difficulty`
**Response**:
```json
{
  "questions": [
    {
      "id": "question_uuid",
      "text": "Explain the difference between list and tuple in Python",
      "type": "technical",
      "difficulty": "medium",
      "job_role": "software_engineer",
      "skills_assessed": ["python", "data_structures"],
      "expected_duration": 120
    }
  ],
  "total": 150,
  "page": 1
}
```

#### `POST /api/v1/questions`
**Purpose**: Add custom question to database  
**Request**:
```json
{
  "text": "How would you optimize a slow database query?",
  "type": "technical",
  "difficulty": "hard",
  "job_role": "backend_developer",
  "skills_assessed": ["sql", "database_optimization"],
  "expected_duration": 180
}
```

---

### 6. Interview Reports & Analytics

#### `GET /api/v1/reports/{session_id}`
**Purpose**: Get detailed interview report  
**Response**:
```json
{
  "session_id": "session_uuid",
  "candidate": {
    "id": "candidate_uuid",
    "name": "John Doe"
  },
  "overall_score": 8.5,
  "technical_score": 9.0,
  "communication_score": 8.0,
  "problem_solving_score": 8.5,
  "strengths": [
    "Strong Python knowledge",
    "Good problem-solving approach",
    "Clear communication"
  ],
  "weaknesses": [
    "Could improve system design knowledge",
    "Needs more experience with databases"
  ],
  "recommendation": "hire",
  "confidence_level": "high",
  "detailed_feedback": {
    "technical_competency": "Candidate showed strong...",
    "communication_skills": "Clear and articulate...",
    "problem_solving_approach": "Systematic approach..."
  },
  "skills_assessment": {
    "python": {"score": 9, "evidence": "Wrote clean code..."},
    "algorithms": {"score": 7, "evidence": "Good understanding..."}
  },
  "responses": [
    {
      "question": "Tell me about yourself",
      "transcription": "I am a software engineer...",
      "technical_score": 8,
      "communication_score": 9,
      "duration": 45
    }
  ],
  "generated_at": "2024-01-15T15:00:00Z"
}
```

#### `GET /api/v1/reports`
**Purpose**: List all reports  
**Query Parameters**: `candidate_id`, `date_from`, `date_to`, `job_role`

#### `POST /api/v1/reports/{session_id}/regenerate`
**Purpose**: Regenerate interview report using latest AI model

#### `GET /api/v1/analytics/performance`
**Purpose**: Get performance analytics  
**Response**:
```json
{
  "total_interviews": 1250,
  "average_score": 7.2,
  "completion_rate": 0.89,
  "by_job_role": {
    "software_engineer": {"count": 450, "avg_score": 7.5},
    "data_scientist": {"count": 200, "avg_score": 7.8}
  },
  "trends": {
    "last_30_days": [
      {"date": "2024-01-01", "interviews": 15, "avg_score": 7.1},
      {"date": "2024-01-02", "interviews": 18, "avg_score": 7.3}
    ]
  }
}
```

#### `GET /api/v1/analytics/trends`
**Purpose**: Get hiring trends and insights

---

### 7. System Health & Monitoring

#### `GET /api/v1/health`
**Purpose**: Health check endpoint  
**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "openai_api": "healthy",
    "audio_services": "healthy"
  },
  "version": "1.0.0"
}
```

#### `GET /api/v1/metrics`
**Purpose**: System metrics for monitoring  
**Response**: Prometheus format metrics

---

## 🔌 WebSocket Endpoints

### Main WebSocket Connection

#### `WS /ws/{session_id}`
**Purpose**: Real-time interview communication  
**Authentication**: JWT token in query parameter or header

### WebSocket Message Types

#### 1. Connection Events

**Client → Server: Join Interview**
```json
{
  "type": "join_interview",
  "session_id": "session_uuid",
  "candidate_id": "candidate_uuid",
  "token": "jwt_token"
}
```

**Server → Client: Connection Confirmed**
```json
{
  "type": "connection_confirmed",
  "session_id": "session_uuid",
  "message": "Connected to AI Interviewer",
  "interview_status": "waiting|in_progress|completed"
}
```

#### 2. Interview Control

**Client → Server: Start Interview**
```json
{
  "type": "start_interview",
  "session_id": "session_uuid"
}
```

**Server → Client: Interview Started**
```json
{
  "type": "interview_started",
  "session_id": "session_uuid",
  "first_question": {
    "text": "Hello! Please tell me about yourself.",
    "type": "introduction",
    "expected_duration": 90,
    "audio_url": "data:audio/wav;base64,..."
  },
  "interview_context": {
    "total_expected_questions": 8,
    "estimated_duration": 30
  }
}
```

#### 3. Audio Processing

**Client → Server: Audio Chunk**
```json
{
  "type": "audio_chunk",
  "session_id": "session_uuid",
  "audio_data": "base64_encoded_audio",
  "sequence": 1,
  "is_final": false,
  "timestamp": "2024-01-15T10:30:15.123Z"
}
```

**Client → Server: Speech End**
```json
{
  "type": "speech_end",
  "session_id": "session_uuid",
  "sequence": 5
}
```

**Server → Client: Transcription Update**
```json
{
  "type": "transcription_update",
  "session_id": "session_uuid",
  "transcription": "I am a software engineer with 3 years...",
  "is_final": true,
  "confidence": 0.95
}
```

#### 4. AI Response Processing

**Server → Client: Processing Status**
```json
{
  "type": "processing_status",
  "session_id": "session_uuid",
  "status": "analyzing_response|generating_question|converting_to_speech",
  "message": "Analyzing your response..."
}
```

**Server → Client: AI Response Ready**
```json
{
  "type": "ai_response_ready",
  "session_id": "session_uuid",
  "response": {
    "analysis": {
      "technical_score": 8.5,
      "communication_score": 7.0,
      "key_strengths": ["Clear explanation", "Good examples"],
      "areas_for_improvement": ["Could add more detail"]
    },
    "next_question": {
      "text": "Can you explain the difference between REST and GraphQL?",
      "type": "technical",
      "expected_duration": 120,
      "skills_being_assessed": ["api_design", "web_development"]
    },
    "audio_data": "base64_encoded_audio",
    "question_number": 3,
    "total_questions": 8
  }
}
```

#### 5. Interview Progress

**Server → Client: Progress Update**
```json
{
  "type": "progress_update",
  "session_id": "session_uuid",
  "current_question": 4,
  "total_questions": 8,
  "elapsed_time": 15,
  "estimated_remaining": 15,
  "current_score": 7.8
}
```

#### 6. Interview Completion

**Client → Server: End Interview**
```json
{
  "type": "end_interview",
  "session_id": "session_uuid",
  "reason": "completed|candidate_request|technical_issue"
}
```

**Server → Client: Interview Completed**
```json
{
  "type": "interview_completed",
  "session_id": "session_uuid",
  "summary": {
    "total_questions": 8,
    "duration": 28,
    "overall_score": 8.2,
    "recommendation": "hire"
  },
  "report_url": "/api/v1/reports/session_uuid",
  "message": "Thank you for completing the interview!"
}
```

#### 7. Error Handling

**Server → Client: Error**
```json
{
  "type": "error",
  "session_id": "session_uuid",
  "error_code": "AUDIO_PROCESSING_FAILED|OPENAI_API_ERROR|SESSION_EXPIRED",
  "message": "There was an issue processing your audio. Please try again.",
  "recoverable": true,
  "retry_after": 5
}
```

#### 8. System Events

**Server → Client: System Notification**
```json
{
  "type": "system_notification",
  "session_id": "session_uuid",
  "level": "info|warning|error",
  "message": "Your connection quality is poor. Please check your internet.",
  "action_required": false
}
```

---

## 📊 Implementation Priority

### Phase 1 (Core Functionality)
1. ✅ Authentication endpoints
2. ✅ Interview session management
3. ✅ WebSocket connection and basic messaging
4. ✅ Audio processing endpoints
5. ✅ Basic report generation

### Phase 2 (Enhanced Features)
1. ✅ Advanced analytics
2. ✅ Question management
3. ✅ Performance monitoring
4. ✅ Error handling improvements

### Phase 3 (Production Ready)
1. ✅ Rate limiting
2. ✅ Comprehensive logging
3. ✅ Health checks
4. ✅ Metrics collection

---

## 🔒 Security Considerations

### Authentication
- JWT tokens for all API endpoints
- WebSocket authentication via token
- Role-based access control

### Rate Limiting
- API endpoints: 100 requests/minute per user
- WebSocket: Connection limits per session
- Audio upload: Size and duration limits

### Data Protection
- Audio data encryption in transit
- Temporary audio file cleanup
- PII data handling compliance

This comprehensive API specification covers all the endpoints your Backend & AI team needs to implement for the AI Interviewer system!