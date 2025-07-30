# AI Interviewer - System Flow Diagrams

## 1. Complete Interview Flow Diagram

```mermaid
graph TD
    A[Candidate Accesses Interview Link] --> B[Authentication & Validation]
    B --> C[Create Interview Session]
    C --> D[Initialize WebRTC Connection]
    D --> E[Display Interview Interface]
    E --> F[AI Introduction & First Question]
    
    F --> G[Candidate Speaks Response]
    G --> H[Audio Capture & Streaming]
    H --> I[Speech-to-Text Processing]
    I --> J[Response Analysis & Evaluation]
    J --> K[Generate Next Question]
    K --> L[Text-to-Speech Conversion]
    L --> M[Play AI Response]
    
    M --> N{Interview Complete?}
    N -->|No| G
    N -->|Yes| O[Generate Interview Report]
    O --> P[Store Results]
    P --> Q[Send Report to Stakeholders]
    Q --> R[End Session]
    
    style A fill:#e1f5fe
    style F fill:#f3e5f5
    style O fill:#e8f5e8
    style R fill:#ffebee
```

## 2. Detailed Real-time Communication Flow

```mermaid
sequenceDiagram
    participant C as Candidate Browser
    participant WS as WebSocket Server
    participant AS as Audio Service
    participant STT as Speech-to-Text
    participant NLP as NLP Engine
    participant QG as Question Generator
    participant TTS as Text-to-Speech
    participant DB as Database
    
    Note over C,DB: Interview Initialization
    C->>WS: Connect with session token
    WS->>DB: Validate session
    DB-->>WS: Session details
    WS-->>C: Connection established
    
    Note over C,DB: First Question
    WS->>QG: Generate opening question
    QG->>DB: Get candidate profile
    DB-->>QG: Profile data
    QG-->>WS: Opening question
    WS->>TTS: Convert to speech
    TTS-->>WS: Audio data
    WS-->>C: Play opening question
    
    Note over C,DB: Response Processing Loop
    loop For each response
        C->>WS: Audio chunk (real-time)
        WS->>AS: Buffer audio data
        AS->>STT: Process audio
        STT-->>AS: Transcription
        AS-->>WS: Transcribed text
        
        WS->>NLP: Analyze response
        NLP-->>WS: Analysis results
        WS->>DB: Store response & analysis
        
        WS->>QG: Generate next question
        QG->>DB: Get interview context
        DB-->>QG: Context data
        QG-->>WS: Next question
        
        WS->>TTS: Convert to speech
        TTS-->>WS: Audio response
        WS-->>C: Play AI question
    end
    
    Note over C,DB: Interview Completion
    WS->>DB: Generate final report
    DB-->>WS: Interview report
    WS-->>C: Interview completed
```

## 3. Audio Processing Pipeline

```mermaid
graph LR
    A[Microphone Input] --> B[Audio Capture API]
    B --> C[Audio Preprocessing]
    C --> D[Noise Reduction]
    D --> E[Audio Chunking]
    E --> F[WebSocket Streaming]
    
    F --> G[Server Audio Buffer]
    G --> H[Audio Enhancement]
    H --> I[Speech Detection]
    I --> J{Speech Detected?}
    
    J -->|Yes| K[Speech-to-Text API]
    J -->|No| L[Continue Buffering]
    L --> G
    
    K --> M[Transcription Result]
    M --> N[Confidence Check]
    N --> O{Confidence > Threshold?}
    
    O -->|Yes| P[Process Transcription]
    O -->|No| Q[Request Repeat/Clarification]
    
    P --> R[NLP Analysis]
    Q --> S[Generate Clarification Question]
    S --> T[Text-to-Speech]
    T --> U[Audio Response]
    
    style A fill:#e3f2fd
    style K fill:#fff3e0
    style R fill:#e8f5e8
```

## 4. Question Generation Strategy

```mermaid
graph TD
    A[Interview Context] --> B[Candidate Profile Analysis]
    B --> C[Previous Response Evaluation]
    C --> D[Skill Gap Identification]
    D --> E[Question Type Selection]
    
    E --> F{Question Type}
    F -->|Technical| G[Technical Question Bank]
    F -->|Behavioral| H[Behavioral Question Bank]
    F -->|Situational| I[Situational Question Bank]
    F -->|Follow-up| J[Dynamic Follow-up Generator]
    
    G --> K[Difficulty Adaptation]
    H --> K
    I --> K
    J --> K
    
    K --> L[Question Customization]
    L --> M[Context Integration]
    M --> N[Final Question Generation]
    
    N --> O[Question Validation]
    O --> P{Valid Question?}
    P -->|Yes| Q[Return Question]
    P -->|No| E
    
    style A fill:#e1f5fe
    style N fill:#f3e5f5
    style Q fill:#e8f5e8
```

## 5. Error Handling & Recovery Flow

```mermaid
graph TD
    A[System Operation] --> B{Error Detected?}
    B -->|No| A
    B -->|Yes| C[Error Classification]
    
    C --> D{Error Type}
    D -->|Audio| E[Audio Error Handler]
    D -->|Network| F[Network Error Handler]
    D -->|AI Service| G[AI Service Error Handler]
    D -->|Database| H[Database Error Handler]
    
    E --> I[Switch Audio Source/Retry]
    F --> J[Reconnection Logic]
    G --> K[Fallback AI Service]
    H --> L[Database Failover]
    
    I --> M{Recovery Successful?}
    J --> M
    K --> M
    L --> M
    
    M -->|Yes| N[Log Recovery & Continue]
    M -->|No| O[Graceful Degradation]
    
    N --> A
    O --> P[Notify User & Admin]
    P --> Q[Save Session State]
    Q --> R[Schedule Retry/Reschedule]
    
    style B fill:#fff3e0
    style O fill:#ffebee
    style N fill:#e8f5e8
```

## 6. Session Management Lifecycle

```mermaid
stateDiagram-v2
    [*] --> SessionCreated: Create Session
    SessionCreated --> WaitingForCandidate: Initialize
    WaitingForCandidate --> InProgress: Candidate Joins
    
    InProgress --> AudioProcessing: Candidate Speaks
    AudioProcessing --> ResponseAnalysis: STT Complete
    ResponseAnalysis --> QuestionGeneration: Analysis Complete
    QuestionGeneration --> AIResponse: Question Ready
    AIResponse --> InProgress: AI Speaks
    
    InProgress --> Paused: Connection Issues
    Paused --> InProgress: Connection Restored
    Paused --> Terminated: Timeout/Failure
    
    InProgress --> Completed: Interview Finished
    Completed --> ReportGeneration: Generate Report
    ReportGeneration --> Archived: Report Complete
    
    InProgress --> Cancelled: User/Admin Cancel
    Cancelled --> Archived: Cleanup Complete
    
    Terminated --> Archived: Error Handling Complete
    Archived --> [*]
```

## 7. Data Flow Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[React Frontend]
        B[WebRTC Client]
        C[Audio Components]
    end
    
    subgraph "API Gateway"
        D[Load Balancer]
        E[Authentication]
        F[Rate Limiting]
    end
    
    subgraph "Service Layer"
        G[Interview Service]
        H[Audio Service]
        I[Session Manager]
        J[User Service]
    end
    
    subgraph "AI/ML Layer"
        K[Speech Services]
        L[NLP Engine]
        M[Question Generator]
        N[Response Analyzer]
    end
    
    subgraph "Data Layer"
        O[(PostgreSQL)]
        P[(Redis Cache)]
        Q[File Storage]
    end
    
    A --> D
    B --> D
    C --> D
    
    D --> G
    D --> H
    D --> I
    D --> J
    
    G --> K
    G --> L
    H --> K
    I --> P
    
    L --> M
    L --> N
    M --> O
    N --> O
    
    G --> O
    H --> Q
    I --> O
    J --> O
    
    style A fill:#e3f2fd
    style K fill:#fff3e0
    style O fill:#e8f5e8
```

## 8. Microservices Communication Pattern

```mermaid
graph LR
    subgraph "Frontend"
        A[React App]
    end
    
    subgraph "API Gateway"
        B[Kong/Nginx]
    end
    
    subgraph "Core Services"
        C[Interview Service]
        D[Audio Service]
        E[Session Service]
        F[User Service]
    end
    
    subgraph "AI Services"
        G[STT Service]
        H[TTS Service]
        I[NLP Service]
        J[Question Service]
    end
    
    subgraph "Infrastructure"
        K[Message Queue]
        L[Event Bus]
        M[Service Discovery]
    end
    
    A -.->|HTTPS/WSS| B
    B -.->|HTTP/gRPC| C
    B -.->|HTTP/gRPC| D
    B -.->|HTTP/gRPC| E
    B -.->|HTTP/gRPC| F
    
    C -.->|Async| K
    D -.->|Async| K
    
    K -.->|Events| G
    K -.->|Events| H
    K -.->|Events| I
    K -.->|Events| J
    
    C <-.->|Service Mesh| L
    D <-.->|Service Mesh| L
    E <-.->|Service Mesh| L
    F <-.->|Service Mesh| L
    
    L <-.->|Discovery| M
```

## 9. Real-time Performance Monitoring

```mermaid
graph TD
    A[System Metrics Collection] --> B[Performance Dashboard]
    
    subgraph "Metrics Sources"
        C[Audio Latency]
        D[STT Processing Time]
        E[NLP Response Time]
        F[TTS Generation Time]
        G[WebRTC Quality]
        H[Database Performance]
    end
    
    C --> A
    D --> A
    E --> A
    F --> A
    G --> A
    H --> A
    
    B --> I[Alert System]
    I --> J{Threshold Exceeded?}
    J -->|Yes| K[Send Notifications]
    J -->|No| L[Continue Monitoring]
    
    K --> M[Auto-scaling Trigger]
    M --> N[Resource Adjustment]
    N --> L
    
    B --> O[Analytics Engine]
    O --> P[Performance Reports]
    P --> Q[Optimization Recommendations]
    
    style A fill:#e1f5fe
    style I fill:#fff3e0
    style Q fill:#e8f5e8
```

This comprehensive set of flow diagrams provides a detailed view of how the AI Interviewer system operates at different levels, from high-level user interactions to low-level technical processes. Each diagram focuses on specific aspects of the system to ensure clarity and maintainability.