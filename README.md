# AI Life Admin Assistant

A complete production-ready AI system that automatically organizes users' entire lives by reading emails, scanning documents, extracting tasks, predicting schedules, and generating daily action plans.

## Features

- **Multi-Email Provider Support**: Gmail API, Microsoft Graph (Outlook), and IMAP
- **Document Processing**: OCR with Tesseract, document classification with AI
- **AI-Powered Task Extraction**: Automatically extracts tasks from emails and documents
- **Daily Plan Generation**: AI-generated prioritized daily schedules
- **Intelligent Reminders**: Smart reminder system with notifications
- **Self-Hosted AI**: Uses Ollama for privacy and cost control
- **Real-time Updates**: WebSocket support for live notifications

## Architecture

```
Frontend (React) → API Gateway (NGINX) → FastAPI Backend → PostgreSQL + Redis
                                                              ↓
                                                         AI Engine (Ollama)
                                                              ↓
                                                         Celery Workers
```

## Tech Stack

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL 15+
- Redis 7+
- Celery for async tasks
- SQLAlchemy ORM
- Alembic for migrations

### AI/ML
- Ollama (self-hosted LLM)
- spaCy for NLP
- Tesseract OCR
- PyPDF2/pdfplumber for PDF processing

### Frontend
- React 18 with TypeScript
- Vite
- React Router
- Zustand for state management
- React Query for data fetching
- Tailwind CSS

### Infrastructure
- Docker & Docker Compose
- NGINX reverse proxy
- AWS S3 for document storage

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- PostgreSQL 15+ (if not using Docker)
- Redis 7+ (if not using Docker)
- Ollama installed and running (for AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-life-admin
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your configuration
   ```

3. **Start Ollama and pull model**
   ```bash
   ollama serve
   ollama pull llama3:8b
   ```

4. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

5. **Run database migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

6. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Celery Workers

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Emails
- `POST /api/v1/emails/connect` - Connect email account
- `GET /api/v1/emails/accounts` - List connected accounts
- `POST /api/v1/emails/sync` - Sync emails
- `GET /api/v1/emails` - List emails
- `GET /api/v1/emails/{id}` - Get email details

### Documents
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents` - List documents
- `GET /api/v1/documents/{id}` - Get document details
- `POST /api/v1/documents/{id}/process` - Process document
- `DELETE /api/v1/documents/{id}` - Delete document

### Tasks
- `GET /api/v1/tasks` - List tasks
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks/{id}` - Get task details
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `POST /api/v1/tasks/{id}/complete` - Complete task
- `GET /api/v1/tasks/predict` - Get predicted tasks

### Daily Plans
- `GET /api/v1/plans/today` - Get today's plan
- `GET /api/v1/plans/{date}` - Get plan for date
- `POST /api/v1/plans/regenerate` - Regenerate plan

### Notifications
- `GET /api/v1/notifications` - List notifications
- `PUT /api/v1/notifications/{id}/read` - Mark as read
- `DELETE /api/v1/notifications/{id}` - Delete notification

### Settings
- `GET /api/v1/settings` - Get settings
- `PUT /api/v1/settings` - Update settings

## Database Schema

See `backend/alembic/versions/` for migration files. Key tables:
- `users` - User accounts
- `email_accounts` - Connected email providers
- `email_items` - Synced emails
- `documents` - Uploaded documents
- `tasks` - Extracted and manual tasks
- `reminders` - Scheduled reminders
- `notifications` - User notifications
- `user_settings` - User preferences

## AI Configuration

The system uses Ollama for AI processing. Configure in `.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2000
```

## Security

- JWT authentication with refresh tokens
- Encrypted storage of email OAuth tokens
- Rate limiting on API endpoints
- Input validation and sanitization
- S3 presigned URLs for document access
- CORS configuration
- Security headers via NGINX

## Deployment

### AWS Deployment

1. **EC2 Setup**
   - Launch EC2 instances for application servers
   - Configure security groups
   - Set up Application Load Balancer

2. **RDS Setup**
   - Create PostgreSQL RDS instance
   - Configure security groups
   - Update DATABASE_URL

3. **S3 Setup**
   - Create S3 bucket for documents
   - Configure IAM roles
   - Update S3_BUCKET_NAME

4. **ElastiCache**
   - Create Redis cluster
   - Update REDIS_URL

5. **Deploy**
   ```bash
   docker build -t ai-life-admin-backend ./backend
   docker build -t ai-life-admin-frontend ./frontend
   # Push to ECR and deploy
   ```

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## License

MIT

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Support

For issues and questions, please open an issue on GitHub.
