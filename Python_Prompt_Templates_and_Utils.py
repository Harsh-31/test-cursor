# app/utils/prompt_templates.py

PROMPT_TEMPLATES = {
    "RESPONSE_ANALYSIS": """
You are an expert technical interviewer evaluating a candidate's response. 

Interview Context:
- Job Role: {job_role}
- Question Asked: {question}
- Candidate Response: {response}
- Skills Already Assessed: {skills_assessed}

Analyze this response and provide a detailed evaluation in JSON format:

{{
    "technical_score": <0-10 score for technical accuracy and depth>,
    "communication_score": <0-10 score for clarity and articulation>,
    "confidence": <0-10 score for candidate's confidence level>,
    "key_strengths": [<list of 2-3 specific strengths demonstrated>],
    "areas_for_improvement": [<list of 2-3 specific areas to improve>],
    "follow_up_needed": <true/false if clarification is needed>,
    "overall_assessment": "<2-3 sentence summary of the response quality>",
    "keywords_mentioned": [<relevant technical keywords candidate used>],
    "depth_of_knowledge": "<surface/intermediate/deep assessment of knowledge level>",
    "problem_solving_approach": "<description of how they approached the problem if applicable>"
}}

Be fair but thorough in your evaluation. Consider both technical accuracy and communication skills.
""",

    "QUESTION_GENERATION": """
You are an expert interviewer conducting a {job_role} interview.

Current Interview State:
- Interview Stage: {stage}
- Previous Response Quality: {response_quality}
- Skills Already Assessed: {assessed_skills}
- Skills Still to Assess: {remaining_skills}

Generate the next most appropriate interview question. The question should:
1. Match the candidate's demonstrated skill level
2. Explore areas not yet fully assessed
3. Be clear, specific, and fair
4. Have appropriate difficulty progression
5. Allow for meaningful evaluation

Return your response in JSON format:

{{
    "question": "<the complete question text>",
    "type": "<technical|behavioral|situational|problem_solving|system_design>",
    "difficulty": "<easy|medium|hard>",
    "expected_duration": <time in seconds (60-300)>,
    "skills_being_assessed": [<list of skills this question evaluates>],
    "evaluation_criteria": [<key points to look for in the response>],
    "follow_up_hints": [<optional hints if candidate struggles>]
}}

Make the question engaging and relevant to real-world scenarios in the {job_role} role.
""",

    "INTERVIEW_REPORT": """
Generate a comprehensive interview evaluation report for this candidate.

Interview Summary:
- Candidate: {candidate_name}
- Position: {job_role}
- Duration: {duration}
- Questions Asked: {question_count}

Detailed Response Analysis:
{responses_summary}

Create a thorough evaluation report in JSON format:

{{
    "overall_score": <0-10 overall interview performance>,
    "technical_score": <0-10 technical competency score>,
    "communication_score": <0-10 communication effectiveness score>,
    "problem_solving_score": <0-10 problem-solving ability>,
    "cultural_fit_score": <0-10 based on responses and approach>,
    
    "strengths": [<list of 3-5 key strengths with specific examples>],
    "weaknesses": [<list of 2-4 areas for improvement with specifics>],
    "recommendation": "<hire|strong_hire|maybe|no_hire>",
    "confidence_level": "<high|medium|low confidence in recommendation>",
    
    "detailed_feedback": {{
        "technical_competency": "<detailed assessment of technical skills>",
        "communication_skills": "<assessment of how well they explained concepts>",
        "problem_solving_approach": "<how they approached challenges>",
        "learning_attitude": "<willingness to learn and adapt>",
        "experience_level": "<junior|mid|senior assessment>"
    }},
    
    "skills_assessment": {{
        <for each skill assessed>
        "skill_name": {{
            "score": <0-10>,
            "evidence": "<specific examples from responses>",
            "notes": "<additional observations>"
        }}
    }},
    
    "interview_quality": {{
        "response_depth": "<surface|good|excellent>",
        "consistency": "<how consistent were responses>",
        "engagement": "<candidate's engagement level>",
        "questions_asked": "<quality of questions candidate asked>"
    }},
    
    "next_steps": [<recommended follow-up actions>],
    "additional_notes": "<any other relevant observations>"
}}

Be objective, specific, and provide actionable feedback.
""",

    "FOLLOW_UP_QUESTION": """
The candidate just answered: "{original_question}"
Their response was: "{candidate_response}"

Context: {context}
Needs Clarification: {needs_clarification}

Generate an appropriate follow-up question in JSON format:

{{
    "question": "<follow-up question text>",
    "type": "follow_up",
    "purpose": "<clarification|deeper_dive|example_request|alternative_approach>",
    "expected_duration": <30-120 seconds>,
    "skills_being_assessed": [<same as original or related skills>]
}}
""",

    "INTERVIEW_OPENING": """
You are starting an interview for a {job_role} position.

Candidate Background:
- Name: {candidate_name}
- Experience Level: {experience_level}
- Key Skills: {skills}

Generate a warm, professional opening question that:
1. Makes the candidate comfortable
2. Allows them to introduce themselves naturally
3. Gives insight into their background
4. Sets a positive tone for the interview

Return in JSON format:

{{
    "question": "<opening question text>",
    "type": "introduction",
    "expected_duration": 90,
    "skills_being_assessed": ["communication", "self_presentation"],
    "tone": "warm_and_welcoming"
}}
"""
}

# app/utils/audio_utils.py
import base64
import io
import wave
import numpy as np
from pydub import AudioSegment
from typing import Tuple, Optional


def encode_audio_to_base64(audio_data: bytes) -> str:
    """Encode audio bytes to base64 string."""
    return base64.b64encode(audio_data).decode('utf-8')


def decode_audio_from_base64(base64_audio: str) -> bytes:
    """Decode base64 string to audio bytes."""
    return base64.b64decode(base64_audio)


def convert_audio_format(audio_data: bytes, target_format: str = "wav") -> bytes:
    """Convert audio to target format."""
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_data))
        output_buffer = io.BytesIO()
        audio.export(output_buffer, format=target_format)
        return output_buffer.getvalue()
    except Exception as e:
        print(f"Audio conversion failed: {e}")
        return audio_data


def get_audio_duration(audio_data: bytes) -> float:
    """Get audio duration in seconds."""
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_data))
        return len(audio) / 1000.0  # Convert milliseconds to seconds
    except:
        return 0.0


def normalize_audio_volume(audio_data: bytes) -> bytes:
    """Normalize audio volume."""
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_data))
        normalized_audio = audio.normalize()
        output_buffer = io.BytesIO()
        normalized_audio.export(output_buffer, format="wav")
        return output_buffer.getvalue()
    except Exception as e:
        print(f"Audio normalization failed: {e}")
        return audio_data


def detect_silence(audio_data: bytes, silence_threshold: int = -40) -> Tuple[bool, float]:
    """Detect if audio contains significant speech or is mostly silence."""
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_data))
        
        # Calculate average dBFS (decibels relative to full scale)
        avg_dbfs = audio.dBFS
        
        # Check if audio is above silence threshold
        has_speech = avg_dbfs > silence_threshold
        
        return has_speech, avg_dbfs
    except:
        return True, 0.0  # Assume has speech if detection fails


def chunk_audio(audio_data: bytes, chunk_duration: int = 5000) -> list:
    """Split audio into chunks of specified duration (milliseconds)."""
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_data))
        chunks = []
        
        for i in range(0, len(audio), chunk_duration):
            chunk = audio[i:i + chunk_duration]
            chunk_buffer = io.BytesIO()
            chunk.export(chunk_buffer, format="wav")
            chunks.append(chunk_buffer.getvalue())
        
        return chunks
    except Exception as e:
        print(f"Audio chunking failed: {e}")
        return [audio_data]


# app/utils/helpers.py
import re
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import hashlib
import secrets


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return secrets.token_urlsafe(32)


def sanitize_text(text: str) -> str:
    """Sanitize text input to prevent injection attacks."""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\'\&]', '', text)
    
    # Limit length
    return sanitized[:1000]


def extract_keywords(text: str) -> List[str]:
    """Extract technical keywords from text."""
    # Common technical keywords (expand based on your needs)
    technical_keywords = {
        'python', 'javascript', 'java', 'react', 'node', 'sql', 'database',
        'api', 'rest', 'graphql', 'microservices', 'docker', 'kubernetes',
        'aws', 'azure', 'gcp', 'machine learning', 'ai', 'algorithm',
        'data structure', 'oop', 'functional programming', 'agile', 'scrum'
    }
    
    text_lower = text.lower()
    found_keywords = []
    
    for keyword in technical_keywords:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords


def calculate_response_score(
    technical_score: float,
    communication_score: float,
    confidence: float,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """Calculate weighted response score."""
    if weights is None:
        weights = {
            'technical': 0.5,
            'communication': 0.3,
            'confidence': 0.2
        }
    
    total_score = (
        technical_score * weights['technical'] +
        communication_score * weights['communication'] +
        confidence * weights['confidence']
    )
    
    return round(total_score, 2)


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable format."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def is_session_expired(created_at: datetime, max_duration_hours: int = 2) -> bool:
    """Check if a session has expired."""
    expiry_time = created_at + timedelta(hours=max_duration_hours)
    return datetime.utcnow() > expiry_time


def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for storage."""
    return hashlib.sha256(data.encode()).hexdigest()


def validate_job_role(job_role: str) -> bool:
    """Validate if job role is supported."""
    supported_roles = {
        'software_engineer', 'data_scientist', 'frontend_developer',
        'backend_developer', 'fullstack_developer', 'devops_engineer',
        'mobile_developer', 'ui_ux_designer', 'product_manager'
    }
    
    return job_role.lower().replace(' ', '_') in supported_roles


def parse_json_safely(json_string: str) -> Optional[Dict[str, Any]]:
    """Safely parse JSON string with error handling."""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return None


async def retry_async_operation(
    operation,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0
):
    """Retry an async operation with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            wait_time = delay * (backoff_factor ** attempt)
            print(f"Operation failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
            await asyncio.sleep(wait_time)


def create_error_response(error_message: str, error_code: str = "INTERNAL_ERROR") -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        "error": True,
        "error_code": error_code,
        "message": error_message,
        "timestamp": datetime.utcnow().isoformat()
    }


def log_interview_event(session_id: str, event_type: str, details: Dict[str, Any]):
    """Log interview events for debugging and analytics."""
    log_entry = {
        "session_id": session_id,
        "event_type": event_type,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # In production, you'd send this to your logging service
    print(f"INTERVIEW_LOG: {json.dumps(log_entry)}")


# app/schemas/interview.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    INTRODUCTION = "introduction"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"
    PROBLEM_SOLVING = "problem_solving"
    SYSTEM_DESIGN = "system_design"
    FOLLOW_UP = "follow_up"
    CLOSING = "closing"


class InterviewStatus(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class Question(BaseModel):
    text: str = Field(..., description="The question text")
    type: QuestionType = Field(..., description="Type of question")
    difficulty: str = Field(default="medium", description="Question difficulty")
    expected_duration: int = Field(default=120, description="Expected response time in seconds")
    skills_being_assessed: List[str] = Field(default=[], description="Skills this question evaluates")
    evaluation_criteria: Optional[List[str]] = Field(default=None, description="Key evaluation points")
    follow_up_hints: Optional[List[str]] = Field(default=None, description="Hints if candidate struggles")


class ResponseAnalysis(BaseModel):
    technical_score: float = Field(..., ge=0, le=10, description="Technical accuracy score")
    communication_score: float = Field(..., ge=0, le=10, description="Communication clarity score")
    confidence: float = Field(..., ge=0, le=10, description="Candidate confidence level")
    key_strengths: List[str] = Field(..., description="Identified strengths")
    areas_for_improvement: List[str] = Field(..., description="Areas needing improvement")
    follow_up_needed: bool = Field(..., description="Whether follow-up is needed")
    overall_assessment: str = Field(..., description="Overall response assessment")
    keywords_mentioned: Optional[List[str]] = Field(default=None, description="Technical keywords used")
    depth_of_knowledge: Optional[str] = Field(default=None, description="Knowledge depth assessment")
    problem_solving_approach: Optional[str] = Field(default=None, description="Problem-solving method")


class InterviewContext(BaseModel):
    job_role: str = Field(..., description="Position being interviewed for")
    candidate_id: str = Field(..., description="Candidate identifier")
    candidate_name: Optional[str] = Field(default=None, description="Candidate name")
    current_stage: str = Field(default="introduction", description="Current interview stage")
    current_question_index: int = Field(default=0, description="Current question number")
    assessed_skills: List[str] = Field(default=[], description="Skills already evaluated")
    remaining_skills: List[str] = Field(default=[], description="Skills yet to be assessed")
    current_question: Optional[Question] = Field(default=None, description="Current active question")
    session_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional session data")


class InterviewResponse(BaseModel):
    session_id: str = Field(..., description="Interview session ID")
    transcription: str = Field(..., description="Speech-to-text result")
    analysis: Optional[ResponseAnalysis] = Field(default=None, description="Response analysis")
    next_question: Optional[Question] = Field(default=None, description="Next question to ask")
    audio_data: Optional[bytes] = Field(default=None, description="TTS audio data")
    duration: Optional[float] = Field(default=None, description="Response duration in seconds")
    error: Optional[str] = Field(default=None, description="Error message if any")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class InterviewSession(BaseModel):
    id: str = Field(..., description="Session identifier")
    candidate_id: str = Field(..., description="Candidate identifier")
    job_role: str = Field(..., description="Job role")
    status: InterviewStatus = Field(default=InterviewStatus.WAITING, description="Session status")
    start_time: Optional[datetime] = Field(default=None, description="Interview start time")
    end_time: Optional[datetime] = Field(default=None, description="Interview end time")
    current_question: Optional[Question] = Field(default=None, description="Current question")
    responses: List[InterviewResponse] = Field(default=[], description="All responses")
    overall_score: Optional[float] = Field(default=None, description="Overall interview score")
    audio_data: Optional[bytes] = Field(default=None, description="Current audio data")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Session metadata")


class InterviewReport(BaseModel):
    session_id: str = Field(..., description="Interview session ID")
    candidate_id: str = Field(..., description="Candidate ID")
    overall_score: float = Field(..., ge=0, le=10, description="Overall interview score")
    technical_score: float = Field(..., ge=0, le=10, description="Technical competency score")
    communication_score: float = Field(..., ge=0, le=10, description="Communication score")
    problem_solving_score: float = Field(..., ge=0, le=10, description="Problem-solving score")
    cultural_fit_score: float = Field(..., ge=0, le=10, description="Cultural fit score")
    
    strengths: List[str] = Field(..., description="Key strengths identified")
    weaknesses: List[str] = Field(..., description="Areas for improvement")
    recommendation: str = Field(..., description="Hiring recommendation")
    confidence_level: str = Field(..., description="Confidence in recommendation")
    
    detailed_feedback: Dict[str, str] = Field(..., description="Detailed feedback by category")
    skills_assessment: Dict[str, Dict[str, Any]] = Field(..., description="Individual skill assessments")
    interview_quality: Dict[str, str] = Field(..., description="Interview quality metrics")
    
    next_steps: List[str] = Field(..., description="Recommended next steps")
    additional_notes: Optional[str] = Field(default=None, description="Additional observations")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation time")


# Example usage and testing
if __name__ == "__main__":
    # Test the schemas
    question = Question(
        text="Can you explain the difference between list and tuple in Python?",
        type=QuestionType.TECHNICAL,
        difficulty="medium",
        expected_duration=120,
        skills_being_assessed=["python", "data_structures"]
    )
    
    print("Question Schema Test:")
    print(question.json(indent=2))
    
    analysis = ResponseAnalysis(
        technical_score=8.5,
        communication_score=7.0,
        confidence=6.5,
        key_strengths=["Good understanding of immutability", "Clear examples"],
        areas_for_improvement=["Could explain performance implications"],
        follow_up_needed=False,
        overall_assessment="Solid understanding with room for deeper knowledge"
    )
    
    print("\nResponse Analysis Schema Test:")
    print(analysis.json(indent=2))