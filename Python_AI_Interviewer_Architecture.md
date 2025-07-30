# AI Interviewer - Python Architecture & Implementation

## 1. Python Technology Stack

### 1.1 Core Framework & Libraries

```python
# requirements.txt
fastapi==0.104.1              # Modern async web framework
uvicorn[standard]==0.24.0     # ASGI server
websockets==12.0              # WebSocket support
python-socketio==5.10.0       # Socket.IO for real-time communication

# AI & Audio Processing
openai==1.3.5                 # OpenAI API client
whisper==1.1.10               # Local Whisper (fallback)
pydub==0.25.1                 # Audio processing
speechrecognition==3.10.0     # Additional STT options

# Database & Caching
sqlalchemy==2.0.23            # ORM
alembic==1.12.1               # Database migrations
asyncpg==0.29.0               # Async PostgreSQL driver
redis==5.0.1                  # Redis client
aioredis==2.0.1               # Async Redis client

# Authentication & Security
python-jose[cryptography]==3.3.0  # JWT handling
passlib[bcrypt]==1.7.4            # Password hashing
python-multipart==0.0.6           # Form data handling

# Utilities
pydantic==2.5.0               # Data validation
python-dotenv==1.0.0          # Environment variables
celery==5.3.4                 # Background tasks
httpx==0.25.2                 # Async HTTP client
```

## 2. Project Structure

```
ai_interviewer/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration settings
│   ├── dependencies.py            # Dependency injection
│   │
│   ├── api/                       # API routes
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── interviews.py      # Interview endpoints
│   │   │   ├── audio.py           # Audio processing endpoints
│   │   │   ├── candidates.py      # Candidate management
│   │   │   └── reports.py         # Report generation
│   │   └── websocket.py           # WebSocket handlers
│   │
│   ├── core/                      # Core business logic
│   │   ├── __init__.py
│   │   ├── interview_service.py   # Main interview logic
│   │   ├── openai_service.py      # OpenAI integration
│   │   ├── audio_service.py       # Audio processing
│   │   ├── session_manager.py     # Session management
│   │   └── auth.py                # Authentication logic
│   │
│   ├── models/                    # Database models
│   │   ├── __init__.py
│   │   ├── candidate.py
│   │   ├── interview.py
│   │   ├── question.py
│   │   └── response.py
│   │
│   ├── schemas/                   # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── candidate.py
│   │   ├── interview.py
│   │   ├── question.py
│   │   └── response.py
│   │
│   ├── database/                  # Database configuration
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── migrations/
│   │
│   ├── utils/                     # Utility functions
│   │   ├── __init__.py
│   │   ├── audio_utils.py
│   │   ├── prompt_templates.py
│   │   └── helpers.py
│   │
│   └── tests/                     # Test files
│       ├── __init__.py
│       ├── test_interview.py
│       ├── test_audio.py
│       └── test_openai.py
│
├── frontend/                      # React frontend (if needed)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 3. Core Implementation

### 3.1 FastAPI Application Setup

```python
# app/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.api.v1 import interviews, audio, candidates, reports
from app.api.websocket import WebSocketManager
from app.database.connection import create_tables
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="AI Interviewer API",
    description="Real-time AI-powered interview system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(interviews.router, prefix="/api/v1/interviews", tags=["interviews"])
app.include_router(audio.router, prefix="/api/v1/audio", tags=["audio"])
app.include_router(candidates.router, prefix="/api/v1/candidates", tags=["candidates"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])

# WebSocket manager
websocket_manager = WebSocketManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket_manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_json()
            await websocket_manager.handle_message(session_id, data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(session_id)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )
```

### 3.2 Configuration Management

```python
# app/config.py
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Interviewer"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/ai_interviewer"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    
    # Audio Services
    WHISPER_MODEL: str = "base"  # base, small, medium, large
    TTS_SERVICE: str = "elevenlabs"  # elevenlabs, azure, google
    ELEVENLABS_API_KEY: str = ""
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"


settings = Settings()
```

### 3.3 OpenAI Service Implementation

```python
# app/core/openai_service.py
from openai import AsyncOpenAI
from typing import List, Dict, Any
import json
import asyncio
from app.config import settings
from app.schemas.interview import InterviewContext, ResponseAnalysis, Question
from app.utils.prompt_templates import PROMPT_TEMPLATES


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def analyze_response(
        self,
        question: str,
        candidate_response: str,
        context: InterviewContext
    ) -> ResponseAnalysis:
        """Analyze candidate response and provide scoring."""
        
        prompt = PROMPT_TEMPLATES["RESPONSE_ANALYSIS"].format(
            question=question,
            response=candidate_response,
            job_role=context.job_role,
            skills_assessed=", ".join(context.assessed_skills)
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            analysis_data = json.loads(response.choices[0].message.content)
            return ResponseAnalysis(**analysis_data)
            
        except Exception as e:
            # Fallback analysis
            return ResponseAnalysis(
                technical_score=5.0,
                communication_score=5.0,
                confidence=5.0,
                key_strengths=["Response provided"],
                areas_for_improvement=["Analysis temporarily unavailable"],
                follow_up_needed=False,
                overall_assessment=f"Analysis error: {str(e)}"
            )
    
    async def generate_next_question(
        self,
        context: InterviewContext,
        previous_responses: List[Dict[str, Any]]
    ) -> Question:
        """Generate the next interview question based on context."""
        
        response_quality = self._assess_overall_quality(previous_responses)
        
        prompt = PROMPT_TEMPLATES["QUESTION_GENERATION"].format(
            job_role=context.job_role,
            stage=context.current_stage,
            response_quality=response_quality,
            assessed_skills=json.dumps(context.assessed_skills),
            remaining_skills=json.dumps(context.remaining_skills)
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert interviewer designing questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            question_data = json.loads(response.choices[0].message.content)
            return Question(**question_data)
            
        except Exception as e:
            # Fallback question
            return Question(
                text="Can you tell me about a challenging project you've worked on?",
                type="behavioral",
                expected_duration=120,
                skills_being_assessed=["problem-solving", "communication"]
            )
    
    async def generate_interview_report(
        self,
        candidate_name: str,
        job_role: str,
        responses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive interview report."""
        
        responses_summary = self._create_responses_summary(responses)
        
        prompt = PROMPT_TEMPLATES["INTERVIEW_REPORT"].format(
            candidate_name=candidate_name,
            job_role=job_role,
            duration=f"{len(responses) * 3} minutes",
            question_count=len(responses),
            responses_summary=responses_summary
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert interviewer generating reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {
                "error": f"Report generation failed: {str(e)}",
                "overall_score": 5.0,
                "recommendation": "manual_review_needed"
            }
    
    def _assess_overall_quality(self, responses: List[Dict[str, Any]]) -> str:
        """Assess overall quality of previous responses."""
        if not responses:
            return "no_previous_responses"
        
        avg_score = sum(r.get("technical_score", 5) for r in responses) / len(responses)
        
        if avg_score >= 8:
            return "excellent"
        elif avg_score >= 6:
            return "good"
        elif avg_score >= 4:
            return "average"
        else:
            return "needs_improvement"
    
    def _create_responses_summary(self, responses: List[Dict[str, Any]]) -> str:
        """Create a summary of all responses for report generation."""
        summary_parts = []
        for i, response in enumerate(responses, 1):
            summary_parts.append(
                f"Q{i}: {response.get('question', 'N/A')}\n"
                f"A{i}: {response.get('transcription', 'N/A')}\n"
                f"Score: {response.get('technical_score', 'N/A')}/10\n"
            )
        return "\n".join(summary_parts)
```

### 3.4 Audio Service Implementation

```python
# app/core/audio_service.py
import asyncio
import aiofiles
import whisper
from pydub import AudioSegment
from io import BytesIO
import httpx
from typing import Optional
from app.config import settings


class AudioService:
    def __init__(self):
        # Load Whisper model for local STT (fallback)
        self.whisper_model = whisper.load_model(settings.WHISPER_MODEL)
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech to text using OpenAI Whisper API (primary) or local Whisper (fallback)."""
        
        try:
            # Try OpenAI Whisper API first
            return await self._openai_whisper_stt(audio_data)
        except Exception as e:
            print(f"OpenAI Whisper failed: {e}, falling back to local Whisper")
            # Fallback to local Whisper
            return await self._local_whisper_stt(audio_data)
    
    async def _openai_whisper_stt(self, audio_data: bytes) -> str:
        """Use OpenAI Whisper API for speech-to-text."""
        
        # Save audio data to temporary file
        temp_file = f"/tmp/audio_{asyncio.current_task().get_name()}.wav"
        
        async with aiofiles.open(temp_file, "wb") as f:
            await f.write(audio_data)
        
        try:
            with open(temp_file, "rb") as audio_file:
                transcript = await self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            return transcript
        finally:
            # Clean up temp file
            try:
                os.remove(temp_file)
            except:
                pass
    
    async def _local_whisper_stt(self, audio_data: bytes) -> str:
        """Use local Whisper model for speech-to-text (fallback)."""
        
        # Convert audio data to format Whisper can process
        audio_segment = AudioSegment.from_file(BytesIO(audio_data))
        audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
        
        # Save to temporary file
        temp_file = f"/tmp/local_audio_{asyncio.current_task().get_name()}.wav"
        audio_segment.export(temp_file, format="wav")
        
        try:
            # Run Whisper in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.whisper_model.transcribe, 
                temp_file
            )
            return result["text"].strip()
        finally:
            try:
                os.remove(temp_file)
            except:
                pass
    
    async def text_to_speech(self, text: str, voice: str = "alloy") -> bytes:
        """Convert text to speech using OpenAI TTS or ElevenLabs."""
        
        if settings.TTS_SERVICE == "elevenlabs" and settings.ELEVENLABS_API_KEY:
            return await self._elevenlabs_tts(text)
        else:
            return await self._openai_tts(text, voice)
    
    async def _openai_tts(self, text: str, voice: str = "alloy") -> bytes:
        """Use OpenAI TTS for text-to-speech."""
        
        response = await self.openai_client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        return response.content
    
    async def _elevenlabs_tts(self, text: str) -> bytes:
        """Use ElevenLabs for text-to-speech."""
        
        url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"  # Default voice
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": settings.ELEVENLABS_API_KEY
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.content
    
    async def enhance_audio(self, audio_data: bytes) -> bytes:
        """Basic audio enhancement (noise reduction, normalization)."""
        
        try:
            audio = AudioSegment.from_file(BytesIO(audio_data))
            
            # Normalize audio
            audio = audio.normalize()
            
            # Apply basic noise reduction (simple high-pass filter)
            audio = audio.high_pass_filter(80)
            
            # Export enhanced audio
            output_buffer = BytesIO()
            audio.export(output_buffer, format="wav")
            return output_buffer.getvalue()
            
        except Exception as e:
            print(f"Audio enhancement failed: {e}")
            return audio_data  # Return original if enhancement fails
```

### 3.5 Interview Service (Main Logic)

```python
# app/core/interview_service.py
from typing import Dict, Any, Optional
import asyncio
import uuid
from datetime import datetime

from app.core.openai_service import OpenAIService
from app.core.audio_service import AudioService
from app.core.session_manager import SessionManager
from app.schemas.interview import InterviewSession, InterviewResponse, Question
from app.models.interview import Interview as InterviewModel
from app.database.connection import get_db


class InterviewService:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.audio_service = AudioService()
        self.session_manager = SessionManager()
    
    async def start_interview(
        self, 
        candidate_id: str, 
        job_role: str
    ) -> InterviewSession:
        """Start a new interview session."""
        
        session_id = str(uuid.uuid4())
        
        # Create session in database
        async with get_db() as db:
            interview = InterviewModel(
                id=session_id,
                candidate_id=candidate_id,
                job_role=job_role,
                status="in_progress",
                start_time=datetime.utcnow()
            )
            db.add(interview)
            await db.commit()
        
        # Initialize session in Redis
        await self.session_manager.create_session(session_id, {
            "candidate_id": candidate_id,
            "job_role": job_role,
            "current_question_index": 0,
            "assessed_skills": [],
            "remaining_skills": self._get_skills_for_role(job_role)
        })
        
        # Generate first question
        first_question = await self.openai_service.generate_next_question(
            context=await self.session_manager.get_context(session_id),
            previous_responses=[]
        )
        
        # Convert to speech
        audio_data = await self.audio_service.text_to_speech(first_question.text)
        
        return InterviewSession(
            id=session_id,
            candidate_id=candidate_id,
            job_role=job_role,
            status="in_progress",
            current_question=first_question,
            audio_data=audio_data
        )
    
    async def process_response(
        self, 
        session_id: str, 
        audio_data: bytes
    ) -> InterviewResponse:
        """Process candidate's audio response."""
        
        try:
            # 1. Convert speech to text
            transcription = await self.audio_service.speech_to_text(audio_data)
            
            # 2. Get session context
            context = await self.session_manager.get_context(session_id)
            current_question = context.current_question
            
            # 3. Analyze response using OpenAI
            analysis = await self.openai_service.analyze_response(
                question=current_question.text,
                candidate_response=transcription,
                context=context
            )
            
            # 4. Store response in database
            await self._store_response(session_id, current_question, transcription, analysis)
            
            # 5. Generate next question
            previous_responses = await self._get_previous_responses(session_id)
            next_question = await self.openai_service.generate_next_question(
                context=context,
                previous_responses=previous_responses
            )
            
            # 6. Convert next question to speech
            audio_response = await self.audio_service.text_to_speech(next_question.text)
            
            # 7. Update session
            await self.session_manager.update_session(session_id, {
                "current_question": next_question.dict(),
                "current_question_index": context.current_question_index + 1
            })
            
            return InterviewResponse(
                session_id=session_id,
                transcription=transcription,
                analysis=analysis,
                next_question=next_question,
                audio_data=audio_response
            )
            
        except Exception as e:
            # Error handling - return graceful fallback
            return InterviewResponse(
                session_id=session_id,
                transcription="Error processing response",
                analysis=None,
                next_question=Question(
                    text="I'm sorry, there was a technical issue. Could you please repeat your answer?",
                    type="clarification",
                    expected_duration=60,
                    skills_being_assessed=[]
                ),
                audio_data=await self.audio_service.text_to_speech(
                    "I'm sorry, there was a technical issue. Could you please repeat your answer?"
                ),
                error=str(e)
            )
    
    async def end_interview(self, session_id: str) -> Dict[str, Any]:
        """End interview and generate report."""
        
        # Get all responses
        responses = await self._get_previous_responses(session_id)
        context = await self.session_manager.get_context(session_id)
        
        # Generate final report using OpenAI
        report = await self.openai_service.generate_interview_report(
            candidate_name=context.candidate_name,
            job_role=context.job_role,
            responses=responses
        )
        
        # Update database
        async with get_db() as db:
            interview = await db.get(InterviewModel, session_id)
            interview.status = "completed"
            interview.end_time = datetime.utcnow()
            interview.overall_score = report.get("overall_score")
            await db.commit()
        
        # Clean up session
        await self.session_manager.cleanup_session(session_id)
        
        return report
    
    def _get_skills_for_role(self, job_role: str) -> list:
        """Get required skills for a job role."""
        
        skills_map = {
            "software_engineer": ["python", "algorithms", "system_design", "databases"],
            "data_scientist": ["python", "machine_learning", "statistics", "sql"],
            "frontend_developer": ["javascript", "react", "css", "html"],
            "backend_developer": ["python", "apis", "databases", "system_design"]
        }
        
        return skills_map.get(job_role.lower(), ["problem_solving", "communication"])
    
    async def _store_response(self, session_id: str, question: Question, transcription: str, analysis):
        """Store response in database."""
        # Implementation for storing response
        pass
    
    async def _get_previous_responses(self, session_id: str) -> list:
        """Get previous responses from database."""
        # Implementation for retrieving responses
        return []
```

### 3.6 WebSocket Manager

```python
# app/api/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
from app.core.interview_service import InterviewService


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.interview_service = InterviewService()
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a WebSocket for a session."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        
        # Send welcome message
        await self.send_message(session_id, {
            "type": "connected",
            "session_id": session_id,
            "message": "Connected to AI Interviewer"
        })
    
    def disconnect(self, session_id: str):
        """Disconnect a WebSocket."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, session_id: str, message: dict):
        """Send message to specific session."""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_json(message)
            except:
                self.disconnect(session_id)
    
    async def handle_message(self, session_id: str, data: dict):
        """Handle incoming WebSocket messages."""
        
        message_type = data.get("type")
        
        if message_type == "start_interview":
            await self._handle_start_interview(session_id, data)
        
        elif message_type == "audio_chunk":
            await self._handle_audio_chunk(session_id, data)
        
        elif message_type == "end_interview":
            await self._handle_end_interview(session_id, data)
    
    async def _handle_start_interview(self, session_id: str, data: dict):
        """Handle interview start."""
        try:
            candidate_id = data.get("candidate_id")
            job_role = data.get("job_role")
            
            session = await self.interview_service.start_interview(candidate_id, job_role)
            
            await self.send_message(session_id, {
                "type": "interview_started",
                "session": session.dict(),
                "first_question": session.current_question.dict()
            })
            
        except Exception as e:
            await self.send_message(session_id, {
                "type": "error",
                "message": f"Failed to start interview: {str(e)}"
            })
    
    async def _handle_audio_chunk(self, session_id: str, data: dict):
        """Handle audio processing."""
        try:
            # Get audio data (base64 encoded)
            audio_data = data.get("audio_data")
            
            # Process the response
            response = await self.interview_service.process_response(
                session_id, 
                audio_data
            )
            
            await self.send_message(session_id, {
                "type": "response_processed",
                "response": response.dict()
            })
            
        except Exception as e:
            await self.send_message(session_id, {
                "type": "error",
                "message": f"Failed to process audio: {str(e)}"
            })
    
    async def _handle_end_interview(self, session_id: str, data: dict):
        """Handle interview completion."""
        try:
            report = await self.interview_service.end_interview(session_id)
            
            await self.send_message(session_id, {
                "type": "interview_completed",
                "report": report
            })
            
        except Exception as e:
            await self.send_message(session_id, {
                "type": "error",
                "message": f"Failed to end interview: {str(e)}"
            })
```

## 4. Database Models with SQLAlchemy

```python
# app/models/interview.py
from sqlalchemy import Column, String, DateTime, Float, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()


class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), nullable=False)
    job_role = Column(String(255), nullable=False)
    status = Column(String(50), default="waiting")
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    current_question_index = Column(Integer, default=0)
    overall_score = Column(Float)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InterviewResponse(Base):
    __tablename__ = "interview_responses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    question_text = Column(Text, nullable=False)
    transcription = Column(Text)
    duration = Column(Integer)
    confidence = Column(Float)
    technical_score = Column(Float)
    communication_score = Column(Float)
    analysis_results = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
```

## 5. Running the Application

### 5.1 Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/ai_interviewer"
export SECRET_KEY="your-secret-key"

# Run database migrations
alembic upgrade head

# Start the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5.2 Docker Setup

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/ai_interviewer
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: ai_interviewer
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

This Python-based architecture provides a robust, scalable foundation for your AI Interviewer system using modern Python async patterns and frameworks!