# College AI Assistant - Detailed Project Report

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [What We Are Building](#what-we-are-building)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [Data Storage](#data-storage)
6. [Core Features](#core-features)
7. [AI/ML Implementation](#aiml-implementation)
8. [Database Schema](#database-schema)
9. [API Endpoints](#api-endpoints)
10. [Frontend Implementation](#frontend-implementation)

---

## 🎯 Project Overview

**College AI Assistant** is an intelligent, AI-powered academic information system designed to help students and faculty members access course notes, view academic results, and retrieve syllabus information through natural language conversations. The system uses advanced AI/ML technologies to understand user queries and provide accurate, context-aware responses.

---

## 🏗️ What We Are Building

### Core Functionalities:

1. **Intelligent Chat Interface**
   - Natural language query processing
   - Multi-agent routing system
   - Context-aware responses
   - Real-time conversation

2. **Notes Management System**
   - PDF document upload and processing
   - Semantic search across uploaded notes
   - Document chunking and vectorization
   - PDF download functionality

3. **Results Management System**
   - Student result PDF upload and parsing
   - Automatic result extraction from PDFs
   - Student result queries by enrollment number
   - Semester-wise result organization
   - CGPA/SGPA calculation

4. **Syllabus Management System**
   - Syllabus PDF upload and extraction
   - Structured syllabus data storage (JSON format)
   - Course information retrieval
   - Unit-wise syllabus display
   - Textbook and reference management

5. **Admin Panel**
   - Notes upload interface
   - Results upload interface
   - Syllabus upload interface
   - Manual data entry options

---

## 🛠️ Technology Stack

### Backend Technologies:

#### **Framework & Runtime:**
- **FastAPI** (v0.104.1) - Modern, fast web framework for building APIs
- **Python 3.13** - Programming language
- **Uvicorn** (v0.24.0) - ASGI server for FastAPI

#### **AI/ML Technologies:**
- **Groq API** (v0.11.0+) - LLM provider
  - Model: `llama-3.3-70b-versatile`
  - Used for: Natural language understanding, response generation
- **ChromaDB** (v1.3.5+) - Vector database
  - Used for: Semantic search, document embeddings storage
  - Persistence: Local file system (`./data/chroma_db`)

#### **Database Technologies:**
- **PostgreSQL** - Relational database
  - Used for: Structured data storage (results, notes metadata, syllabus)
  - Connection: `psycopg[binary]` (v3.2.0+)
  - ORM: SQLAlchemy (v2.0.35+)

#### **Document Processing:**
- **PyPDF2** (v3.0.1) - PDF text extraction
- **pdfplumber** - Advanced PDF parsing (for syllabus extraction)
- **python-multipart** (v0.0.6) - File upload handling

#### **Configuration & Environment:**
- **python-dotenv** (v1.0.0) - Environment variable management
- **pydantic** (v2.5.0+) - Data validation and settings
- **pydantic-settings** (v2.1.0) - Settings management

### Frontend Technologies:

#### **Framework & Library:**
- **Next.js** (v16.0.3) - React framework
- **React** (v19.2.0) - UI library
- **React DOM** (v19.2.0) - React rendering

#### **Styling:**
- **Tailwind CSS** (v4) - Utility-first CSS framework
- **PostCSS** - CSS processing

#### **UI Components:**
- **lucide-react** (v0.554.0) - Icon library
- **react-icons** (v5.5.0) - Additional icons

#### **Development Tools:**
- **ESLint** - Code linting
- **Babel React Compiler** - React optimization

---

## 🏛️ System Architecture

### Architecture Pattern: **Multi-Agent System with Layered Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Chat UI    │  │  Admin Panel │  │  API Client  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Router Agent                              │  │
│  │  (Routes queries to appropriate specialized agent)    │  │
│  └──────────────────────────────────────────────────────┘  │
│           │              │              │                   │
│           ▼              ▼              ▼                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ Notes Agent  │ │Results Agent │ │Syllabus Agent│       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
           │              │              │
           ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  PostgreSQL  │  │  ChromaDB    │  │  LLM Service │     │
│  │  (Structured)│  │  (Vectors)   │  │  (Groq API)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Agent-Based Architecture:

1. **Router Agent** (`router_agent.py`)
   - Analyzes user queries
   - Routes to appropriate specialized agent
   - Handles ambiguous queries with clarification

2. **Notes Agent** (`notes_agent.py`)
   - Processes notes-related queries
   - Performs semantic search using ChromaDB
   - Retrieves relevant PDF documents
   - Generates AI-powered responses

3. **Results Agent** (`results_agent.py`)
   - Handles student result queries
   - Searches PostgreSQL for student data
   - Calculates CGPA/SGPA
   - Formats result displays

4. **Syllabus Agent** (`syllabus_agent.py`)
   - Processes syllabus-related queries
   - Searches syllabus database
   - Formats structured syllabus data
   - Displays units, objectives, outcomes, textbooks, references

---

## 💾 Data Storage

### 1. PostgreSQL Database (Structured Data)

**Location:** Cloud-hosted PostgreSQL (configured via environment variables)

**Connection:**
- Uses `psycopg` for direct database connections
- SQLAlchemy ORM for model definitions
- Connection pooling (pool_size=5, max_overflow=10)

**Tables:**

#### **a) `student_results` Table**
Stores student academic results extracted from PDFs or manually entered.

**Schema:**
```sql
- id (Integer, Primary Key)
- student_id (String, Indexed) - Enrollment number
- student_name (String)
- programme (String) - e.g., B.Tech
- branch (String) - e.g., Computer Science and Engineering
- institute (String) - Institute name
- subject (String) - Course/subject name
- marks (Float) - Total marks obtained
- grade (String) - Grade (A+, A, B+, B, C, D, F)
- semester (String) - Semester identifier
- paper_id (String) - Paper ID like "027302"
- internal_marks (Float) - Internal assessment marks
- external_marks (Float) - External assessment marks
- credits (Integer) - Credit hours for the subject
```

**Storage Location:** PostgreSQL database server

#### **b) `notes_metadata` Table**
Stores metadata about uploaded PDF notes.

**Schema:**
```sql
- id (Integer, Primary Key)
- file_id (String, Unique, Indexed) - UUID identifier
- filename (String) - Original filename
- stored_filename (String) - UUID-based filename on disk
- subject (String) - Subject name
- topic (String) - Topic name
- file_size (Integer) - Size in bytes
- file_path (String) - Path to stored file
- chunk_count (Integer) - Number of text chunks created
- upload_date (DateTime) - Upload timestamp
```

**Storage Location:** PostgreSQL database server

#### **c) `syllabus` Table**
Stores course syllabus information.

**Schema:**
```sql
- id (Integer, Primary Key)
- course_code (String, Unique, Indexed) - e.g., "CIE-306T"
- course_name (String) - Full course name
- department (String) - Department name
- semester (String) - Semester number
- credits (Integer) - Credit hours
- syllabus_content (Text) - JSON-formatted syllabus data
```

**Syllabus Content JSON Structure:**
```json
{
  "course_name": "Advanced Java Programming",
  "course_code": "CIE-306T",
  "credits": {
    "L": 3,
    "P": 0,
    "C": 3
  },
  "semester": "6",
  "department": "CSE",
  "paper_codes": ["CIE-306T"],
  "objectives": [
    "Objective 1...",
    "Objective 2...",
    "Objective 3...",
    "Objective 4..."
  ],
  "outcomes": [
    {"co": "CO 1", "description": "..."},
    {"co": "CO 2", "description": "..."},
    {"co": "CO 3", "description": "..."},
    {"co": "CO 4", "description": "..."}
  ],
  "syllabus": {
    "UNIT-I": {"topics": [...]},
    "UNIT-II": {"topics": [...]},
    "UNIT-III": {"topics": [...]},
    "UNIT-IV": {"topics": [...]}
  },
  "textbooks": [
    {"number": 1, "author": "...", "title": "...", "publisher": "..."}
  ],
  "references": [
    {"number": 1, "author": "...", "title": "...", "publisher": "..."}
  ]
}
```

**Storage Location:** PostgreSQL database server

### 2. ChromaDB (Vector Database)

**Location:** Local file system
- **Path:** `./data/chroma_db/`
- **Type:** Persistent ChromaDB instance
- **Collection Name:** `notes_collection`

**Purpose:**
- Stores document embeddings for semantic search
- Enables similarity-based document retrieval
- Uses cosine similarity for matching

**Data Stored:**
- Document chunks (text segments from PDFs)
- Embeddings (vector representations)
- Metadata (file_id, subject, topic, chunk_index)
- Document IDs (unique identifiers)

**Storage Format:**
- Binary files: `data_level0.bin`, `header.bin`, `index_metadata.pickle`, etc.
- SQLite database: `chroma.sqlite3`

### 3. File Storage (PDF Documents)

**Location:** Local file system
- **Path:** `./data/uploads/`
- **Format:** PDF files stored with UUID-based filenames
- **Naming:** `{uuid}.pdf` (e.g., `272c3dd6-8b3c-4354-a67e-62e4f1b89df4.pdf`)

**Purpose:**
- Stores uploaded PDF notes
- Enables PDF download functionality
- Maintains original documents for reference

**File Management:**
- Files are stored permanently
- UUID-based naming prevents conflicts
- Original filenames stored in database metadata

### 4. Redis Cache (Optional)

**Status:** Configured but currently disabled (`use_redis: False`)

**Purpose (if enabled):**
- Cache frequently accessed data
- Improve response times
- Reduce database load

**Storage Location:** Redis server (when enabled)

---

## 🎨 Core Features

### 1. Natural Language Chat Interface

**Implementation:**
- Users type queries in natural language
- Router Agent analyzes and routes to appropriate agent
- Specialized agents process queries and generate responses
- LLM (Groq) generates context-aware answers

**Example Queries:**
- "What are my results for semester 5?"
- "Find notes on Machine Learning"
- "Show syllabus for Advanced Java Programming"
- "What's my CGPA?"

### 2. Notes Search & Retrieval

**Process:**
1. User uploads PDF notes via admin panel
2. System extracts text from PDF
3. Text is chunked into smaller segments
4. Chunks are embedded using ChromaDB's default embedding function
5. Embeddings stored in ChromaDB with metadata
6. User queries trigger semantic search
7. Relevant chunks retrieved and passed to LLM
8. LLM generates response based on retrieved context

**Features:**
- Semantic search (understands meaning, not just keywords)
- PDF download functionality
- Source citation in responses

### 3. Results Management

**Process:**
1. Admin uploads result PDF or enters manually
2. System extracts student data from PDF
3. Data parsed and stored in PostgreSQL
4. Students query results using enrollment number
5. System retrieves and formats results
6. Calculates CGPA/SGPA automatically

**Features:**
- Automatic PDF parsing
- Semester-wise organization
- Grade point calculation
- Multiple result formats (table, summary)

### 4. Syllabus Management

**Process:**
1. Admin uploads syllabus PDF
2. System extracts structured data using `pdfplumber`
3. Data parsed into JSON format
4. Stored in PostgreSQL with JSON structure
5. Users query by course name or code
6. System formats and displays syllabus information

**Features:**
- Structured data extraction (objectives, outcomes, units, textbooks, references)
- Course code and name search
- Semester and department filtering
- Clean formatting with markdown

---

## 🤖 AI/ML Implementation

### 1. Large Language Model (LLM)

**Provider:** Groq API
**Model:** `llama-3.3-70b-versatile`
**Purpose:**
- Natural language understanding
- Response generation
- Context-aware answers
- Query interpretation

**Configuration:**
- Temperature: 0.7 (balanced creativity/accuracy)
- Max Tokens: 1024 (default)
- System Prompt: "You are a helpful college assistant..."

### 2. Vector Embeddings

**Provider:** ChromaDB Default Embedding Function
**Purpose:**
- Convert text chunks to vector representations
- Enable semantic similarity search
- Find relevant documents based on meaning

**Process:**
1. Text chunks created from PDFs
2. Chunks embedded into vectors
3. Vectors stored in ChromaDB
4. Query embedded and compared
5. Most similar chunks retrieved

### 3. Semantic Search

**Technology:** ChromaDB Query System
**Method:** Cosine Similarity
**Purpose:**
- Find documents similar in meaning to query
- Not just keyword matching
- Understands context and intent

---

## 📊 Database Schema Details

### Student Results Table
```python
class StudentResult(Base):
    __tablename__ = "student_results"
    
    id: Integer (Primary Key)
    student_id: String (Indexed) - Enrollment number
    student_name: String
    programme: String
    branch: String
    institute: String
    subject: String
    marks: Float
    grade: String
    semester: String
    paper_id: String
    internal_marks: Float
    external_marks: Float
    credits: Integer
```

### Notes Metadata Table
```python
class NotesMetadata(Base):
    __tablename__ = "notes_metadata"
    
    id: Integer (Primary Key)
    file_id: String (Unique, Indexed) - UUID
    filename: String
    stored_filename: String
    subject: String
    topic: String
    file_size: Integer
    file_path: String
    chunk_count: Integer
    upload_date: DateTime
```

### Syllabus Table
```python
class Syllabus(Base):
    __tablename__ = "syllabus"
    
    id: Integer (Primary Key)
    course_code: String (Unique, Indexed)
    course_name: String
    department: String
    semester: String
    credits: Integer
    syllabus_content: Text (JSON format)
```

---

## 🔌 API Endpoints

### Chat Endpoints
- `POST /api/chat` - Send chat message, get AI response

### Notes Endpoints
- `POST /api/notes/upload` - Upload PDF notes
- `POST /api/notes/search` - Search notes
- `GET /api/notes/download/{file_id}` - Download PDF

### Results Endpoints
- `POST /api/results/upload` - Upload results PDF
- `POST /api/results/add` - Add result manually
- `GET /api/results/{student_id}` - Get student results

### Syllabus Endpoints
- `POST /api/syllabus/upload` - Upload syllabus PDF
- `POST /api/syllabus` - Add syllabus manually
- `GET /api/syllabus/search` - Search syllabus
- `GET /api/syllabus/course/{course_code}` - Get by course code
- `GET /api/syllabus/semester/{semester}` - Get by semester
- `GET /api/syllabus/department/{department}` - Get by department

### Health Endpoints
- `GET /health` - Health check
- `GET /` - API status

---

## 🎨 Frontend Implementation

### Pages

1. **Main Chat Page** (`/`)
   - Chat interface
   - Message history
   - File upload integration
   - PDF download links
   - Result tables display

2. **Admin Panel** (`/admin`)
   - Notes upload tab
   - Results upload tab
   - Syllabus upload tab
   - Manual data entry forms

### Components

1. **ChatInterface** - Main chat UI
2. **MessageList** - Message display
3. **InputBox** - Message input
4. **NotesUpload** - Notes upload form

### State Management
- React Hooks (`useState`, `useEffect`)
- Local component state
- API service layer (`api.js`)

### Styling
- Tailwind CSS utility classes
- Responsive design
- Modern gradient UI
- Icon integration (Lucide React)

---

## 🔄 Data Flow

### Notes Upload Flow:
```
User Uploads PDF → FastAPI Receives → Extract Text → 
Chunk Text → Generate Embeddings → Store in ChromaDB → 
Store Metadata in PostgreSQL → Store PDF File → Return Success
```

### Notes Query Flow:
```
User Query → Router Agent → Notes Agent → 
Embed Query → Search ChromaDB → Retrieve Relevant Chunks → 
Pass to LLM with Context → Generate Response → Return to User
```

### Results Query Flow:
```
User Query → Router Agent → Results Agent → 
Extract Enrollment Number → Query PostgreSQL → 
Calculate CGPA/SGPA → Format Results → Return to User
```

### Syllabus Query Flow:
```
User Query → Router Agent → Syllabus Agent → 
Search PostgreSQL by Course Name/Code → 
Parse JSON Content → Format Response → Return to User
```

---

## 🔐 Configuration

### Environment Variables (`.env`)

**Required:**
- `GROQ_API_KEY` - Groq API key for LLM
- `DATABASE_URL` - PostgreSQL connection string
- `POSTGRES_HOST` - PostgreSQL host
- `POSTGRES_PORT` - PostgreSQL port (default: 5432)
- `POSTGRES_DB` - Database name
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_CONNECTION_STRING` - Alternative connection string

**Optional:**
- `CHROMA_PERSIST_DIR` - ChromaDB storage path (default: `./data/chroma_db`)
- `USE_REDIS` - Enable Redis caching (default: `False`)
- `ENVIRONMENT` - Environment mode (default: `development`)
- `DEBUG` - Debug mode (default: `True`)

---

## 📁 Project Structure

```
assestant/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agents (router, notes, results, syllabus)
│   │   ├── api/
│   │   │   └── routes/      # API route handlers
│   │   ├── database/        # Database connections and helpers
│   │   ├── models/          # Database models and schemas
│   │   ├── services/        # Business logic (LLM, embeddings, document processing)
│   │   ├── utils/           # Utility functions
│   │   ├── config.py        # Configuration settings
│   │   └── main.py          # FastAPI application entry point
│   ├── data/
│   │   ├── chroma_db/       # ChromaDB vector database files
│   │   ├── notes/           # Notes storage (if needed)
│   │   └── uploads/         # Uploaded PDF files
│   ├── scripts/
│   │   └── extract_syllabus_from_pdf.py  # Syllabus extraction script
│   ├── create_*_table.py   # Database table creation scripts
│   ├── delete_all_*.py      # Utility scripts for data management
│   └── requirements.txt     # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── admin/       # Admin panel page
    │   │   ├── page.js      # Main chat page
    │   │   ├── layout.js    # App layout
    │   │   └── globals.css  # Global styles
    │   ├── components/      # React components
    │   └── lib/
    │       └── api.js       # API client
    ├── public/              # Static assets
    └── package.json         # Node.js dependencies
```

---

## 🚀 Deployment Considerations

### Backend:
- FastAPI with Uvicorn server
- PostgreSQL database (cloud-hosted)
- ChromaDB (local file system or cloud)
- Environment variables for configuration

### Frontend:
- Next.js production build
- Static asset optimization
- API URL configuration via environment variables

### Data Storage Locations:
1. **PostgreSQL:** Cloud database server
2. **ChromaDB:** Local file system (`./data/chroma_db/`)
3. **PDF Files:** Local file system (`./data/uploads/`)

---

## 📈 Future Enhancements

1. **Redis Caching:** Enable Redis for improved performance
2. **User Authentication:** Add user login/registration
3. **Multi-semester Support:** Enhanced result tracking
4. **Advanced Search:** Full-text search capabilities
5. **Analytics:** Usage tracking and analytics
6. **Mobile App:** React Native mobile application
7. **Cloud Storage:** Move PDFs to cloud storage (S3, etc.)
8. **Real-time Updates:** WebSocket support for real-time features

---

## 🎓 Conclusion

The **College AI Assistant** is a comprehensive, AI-powered academic information system that leverages modern technologies to provide intelligent, context-aware assistance to students and faculty. With its multi-agent architecture, semantic search capabilities, and structured data management, it offers a seamless experience for accessing notes, results, and syllabus information through natural language interactions.

**Key Strengths:**
- ✅ Multi-agent system for specialized query handling
- ✅ Semantic search for intelligent document retrieval
- ✅ Structured data storage with JSON support
- ✅ Modern, responsive UI
- ✅ Comprehensive admin panel
- ✅ Scalable architecture

**Technologies Used:**
- FastAPI, Next.js, React
- PostgreSQL, ChromaDB
- Groq LLM (llama-3.3-70b-versatile)
- PyPDF2, pdfplumber
- Tailwind CSS

---

*Report Generated: 2025*
*Project: College AI Assistant*
*Version: 1.0*

