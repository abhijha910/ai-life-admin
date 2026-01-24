# 🤖 AI Life Admin Assistant

<div align="center">

**An intelligent AI-powered system that automatically organizes your entire life by reading emails, scanning documents, extracting tasks, predicting schedules, and generating personalized daily action plans.**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

</div>

---

## ✨ What is AI Life Admin?

AI Life Admin is a **production-ready, full-stack AI system** that acts as your personal life assistant. It intelligently processes your emails and documents, automatically extracts actionable tasks, predicts your schedule patterns, and generates optimized daily plans to help you stay organized and productive.

### 🎯 Core Capabilities

- **📧 Smart Email Processing**: Automatically syncs and analyzes emails from Gmail, Outlook, and IMAP accounts
- **📄 Intelligent Document Scanning**: OCR-powered document processing with automatic classification
- **✅ Automatic Task Extraction**: AI extracts tasks, deadlines, and priorities from your emails and documents
- **📅 Daily Plan Generation**: AI creates personalized, prioritized daily action plans
- **🔔 Smart Reminders**: Intelligent reminder system with context-aware notifications
- **🧠 Habit Pattern Prediction**: Learns your patterns and predicts future tasks and schedules
- **🔒 Privacy-First**: Self-hosted AI using Ollama - your data stays private

---

## 🚀 Key Features

### Email Management
- **Multi-Provider Support**: Connect Gmail, Outlook, or any IMAP email account
- **Automatic Sync**: Background workers continuously sync your emails
- **Smart Classification**: AI categorizes emails by importance, type, and actionability
- **Task Extraction**: Automatically identifies tasks, deadlines, and action items from emails

### Document Intelligence
- **OCR Processing**: Extract text from PDFs, images, and scanned documents
- **Document Classification**: AI automatically categorizes documents (bills, contracts, receipts, etc.)
- **Content Extraction**: Extracts dates, amounts, parties, and key information
- **Secure Storage**: Documents stored securely with encrypted access

### Task Management
- **Auto-Generated Tasks**: Tasks automatically created from emails and documents
- **Priority Scoring**: AI calculates task priority based on deadlines, importance, and context
- **Smart Scheduling**: Tasks intelligently scheduled based on your patterns
- **Progress Tracking**: Track completion and analyze productivity patterns

### Daily Planning
- **AI-Generated Plans**: Personalized daily action plans generated each morning
- **Priority Optimization**: Tasks ordered by importance and deadlines
- **Time Estimation**: AI estimates time needed for each task
- **Adaptive Planning**: Plans adjust based on your actual completion patterns

### Intelligent Reminders
- **Context-Aware**: Reminders consider your schedule and priorities
- **Multi-Channel**: Notifications via web, email, and future mobile app support
- **Smart Timing**: AI determines optimal reminder timing

---

## 🏗️ System Architecture

```
┌─────────────────┐
│   React Frontend │  (TypeScript, Tailwind CSS)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  NGINX Gateway  │  (Reverse Proxy, Load Balancing)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Backend │  (Python, Async, REST API)
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌──────┐  ┌─────────┐ ┌──────────┐
│Postgres│ │Redis │  │Ollama  │ │   S3     │
│   DB   │ │Cache │  │   AI   │ │  Storage │
└────────┘ └──────┘  └─────────┘ └──────────┘
    │         │
    └────┬────┘
         ▼
┌─────────────────┐
│ Celery Workers  │  (Background Processing)
└─────────────────┘
```

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast Python web framework
- **PostgreSQL** - Robust relational database
- **Redis** - Caching and message queue
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations
- **Celery** - Asynchronous task processing
- **Pydantic** - Data validation

### AI & Machine Learning
- **Ollama** - Self-hosted LLM (Llama 3, Mistral, etc.)
- **spaCy** - Natural language processing
- **Tesseract OCR** - Document text extraction
- **PyPDF2/pdfplumber** - PDF processing
- **Custom NLP** - Task extraction and classification

### Frontend
- **React 18** - Modern UI framework
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool
- **React Router** - Client-side routing
- **Zustand** - State management
- **Tailwind CSS** - Utility-first styling
- **React Query** - Data fetching and caching

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **NGINX** - Reverse proxy and load balancing
- **AWS S3** - Document storage
- **GitHub Actions** - CI/CD (ready for setup)

---

## 📱 How to Use

### 1. **Sign Up & Login**
Create your account and log in to access your personalized dashboard.

### 2. **Connect Email Accounts**
- Go to Settings → Email Accounts
- Connect Gmail, Outlook, or IMAP accounts
- Emails automatically sync in the background
- AI processes emails and extracts tasks

### 3. **Upload Documents**
- Navigate to Documents page
- Upload PDFs, images, or scanned documents
- AI automatically extracts text and classifies documents
- Tasks and reminders created from document content

### 4. **View Your Daily Plan**
- Dashboard shows your AI-generated daily plan
- Tasks prioritized by importance and deadlines
- Mark tasks as complete as you finish them
- Plan updates throughout the day

### 5. **Manage Tasks**
- View all tasks in the Task List
- Filter by status, priority, or date
- Edit, complete, or delete tasks
- See tasks extracted from emails and documents

### 6. **Set Reminders**
- Create reminders for important tasks
- AI suggests optimal reminder timing
- Receive notifications via web interface

---

## 🎨 User Interface

The application features a modern, responsive design with:
- **Clean Dashboard**: Overview of your day, tasks, and upcoming items
- **Email Inbox**: Unified inbox for all connected email accounts
- **Document Scanner**: Easy document upload and processing
- **Task Management**: Intuitive task list with filtering and sorting
- **Daily Planner**: Visual timeline of your day
- **Settings**: Configure email accounts, preferences, and AI settings

---

## 🔐 Security & Privacy

- **JWT Authentication**: Secure token-based authentication
- **Encrypted Storage**: Email OAuth tokens encrypted at rest
- **Self-Hosted AI**: Your data never leaves your infrastructure
- **Rate Limiting**: API protection against abuse
- **Input Validation**: Comprehensive input sanitization
- **Secure Headers**: Security headers via NGINX
- **Audit Logging**: Track all important actions

---

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Create new account
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user profile

### Emails
- `POST /api/v1/emails/connect` - Connect email account
- `GET /api/v1/emails/accounts` - List connected accounts
- `POST /api/v1/emails/sync` - Manually trigger email sync
- `GET /api/v1/emails` - List emails with filtering
- `GET /api/v1/emails/{id}` - Get email details

### Documents
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents` - List documents
- `GET /api/v1/documents/{id}` - Get document details
- `POST /api/v1/documents/{id}/process` - Process document with AI
- `DELETE /api/v1/documents/{id}` - Delete document

### Tasks
- `GET /api/v1/tasks` - List tasks with filtering
- `POST /api/v1/tasks` - Create manual task
- `GET /api/v1/tasks/{id}` - Get task details
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `POST /api/v1/tasks/{id}/complete` - Mark task as complete
- `GET /api/v1/tasks/predict` - Get AI-predicted tasks

### Daily Plans
- `GET /api/v1/plans/today` - Get today's plan
- `GET /api/v1/plans/{date}` - Get plan for specific date
- `POST /api/v1/plans/regenerate` - Regenerate plan with AI

### Reminders
- `GET /api/v1/reminders` - List reminders
- `POST /api/v1/reminders` - Create reminder
- `PUT /api/v1/reminders/{id}` - Update reminder
- `DELETE /api/v1/reminders/{id}` - Delete reminder

### Notifications
- `GET /api/v1/notifications` - List notifications
- `PUT /api/v1/notifications/{id}/read` - Mark as read
- `DELETE /api/v1/notifications/{id}` - Delete notification

### Settings
- `GET /api/v1/settings` - Get user settings
- `PUT /api/v1/settings` - Update settings

**Full API Documentation**: Available at `/api/docs` when backend is running (Swagger UI)

---

## 🧠 AI Engine Components

### NLP Extractor
- Extracts entities (dates, amounts, people, locations)
- Identifies action items and tasks
- Classifies email/document types
- Determines sentiment and urgency

### Document Classifier
- Categorizes documents (bills, contracts, receipts, etc.)
- Extracts key information
- Identifies important dates and amounts

### OCR Pipeline
- Text extraction from images and PDFs
- Multi-language support
- Handles scanned documents and photos

### Task Generator
- Creates tasks from emails and documents
- Infers deadlines and priorities
- Links related tasks together

### Priority Scorer
- Calculates task priority based on:
  - Deadlines and due dates
  - Email/document importance
  - User patterns and history
  - Context and relationships

### Plan Generator
- Generates optimized daily schedules
- Considers task priorities and deadlines
- Estimates time requirements
- Adapts to user patterns

### Habit Predictor
- Learns user behavior patterns
- Predicts recurring tasks
- Suggests optimal scheduling
- Identifies productivity patterns

---

## 📦 Project Structure

```
ai-life-admin/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── ai_engine/      # AI processing modules
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── workers/        # Celery background workers
│   │   └── utils/          # Utilities
│   ├── alembic/            # Database migrations
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/          # Page components
│   │   ├── services/       # API client
│   │   └── store/          # State management
│   └── package.json        # Node dependencies
├── nginx/                  # NGINX configuration
├── docker-compose.yml      # Docker orchestration
└── README.md              # This file
```

---

## 🚀 Getting Started

### Prerequisites
- Docker Desktop (for database)
- Python 3.11+ (for backend)
- Node.js 18+ (for frontend)
- Ollama (for AI features)

### Quick Start

1. **Start Database**
   ```powershell
   .\start_database.ps1
   ```

2. **Start Backend**
   ```powershell
   .\start_backend.ps1
   ```

3. **Start Frontend**
   ```powershell
   .\start_frontend.ps1
   ```

4. **Access Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs

### Setup AI (Ollama)

1. Install Ollama from https://ollama.ai
2. Start Ollama: `ollama serve`
3. Pull model: `ollama pull llama3:8b`
4. Configure in backend `.env`:
   ```
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3:8b
   ```

---

## 📈 Future Enhancements

- [ ] Mobile app (React Native)
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Voice commands and voice-to-task
- [ ] Advanced analytics and insights
- [ ] Team collaboration features
- [ ] Third-party integrations (Slack, Trello, etc.)
- [ ] Multi-language support
- [ ] Advanced AI models and fine-tuning

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

---

## 💬 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

<div align="center">

**Built with ❤️ using FastAPI, React, and AI**

[Report Bug](https://github.com/abhijha910/ai-life-admin/issues) · [Request Feature](https://github.com/abhijha910/ai-life-admin/issues) · [Documentation](#-getting-started)

</div>
