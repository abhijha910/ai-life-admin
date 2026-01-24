# Testing Guide - AI Life Admin Assistant

## Quick Start

The backend server should now be running! Here's how to test it:

### 1. Check Server Status

Open your browser and visit:
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/health
- **Root**: http://localhost:8000/

### 2. Test API Endpoints

#### Using the Interactive API Docs (Recommended)

1. Open http://localhost:8000/api/docs in your browser
2. You'll see all available endpoints
3. Click "Try it out" on any endpoint to test it
4. Fill in the required parameters and click "Execute"

#### Test User Registration

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#",
    "full_name": "Test User"
  }'
```

#### Test User Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#"
  }'
```

This will return an access token that you can use for authenticated requests.

#### Test Authenticated Endpoint

```bash
# Replace YOUR_TOKEN with the access_token from login
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Test Frontend (Optional)

To run the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173 in your browser.

### 4. Common Endpoints to Test

1. **Health Check**: `GET /api/health`
2. **Register**: `POST /api/v1/auth/register`
3. **Login**: `POST /api/v1/auth/login`
4. **Get Current User**: `GET /api/v1/auth/me` (requires auth)
5. **List Tasks**: `GET /api/v1/tasks` (requires auth)
6. **Get Today's Plan**: `GET /api/v1/plans/today` (requires auth)

### 5. Troubleshooting

#### Server Not Starting?

- Check if port 8000 is already in use
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check the console for error messages

#### Database Connection Errors?

- The app will work for basic endpoints without a database
- For full functionality, you need PostgreSQL running
- You can use Docker: `docker compose up -d postgres redis`

#### Redis Connection Errors?

- Redis is optional for basic functionality
- Rate limiting might not work without Redis
- You can use Docker: `docker compose up -d redis`

### 6. Next Steps

1. Set up PostgreSQL and Redis (if not using Docker)
2. Run database migrations: `alembic upgrade head`
3. Configure email OAuth credentials (optional)
4. Set up Ollama for AI features (optional)

## Notes

- The server is running in the background
- To stop it, find the process and terminate it, or restart your terminal
- Check the console output for any errors
- The API docs at `/api/docs` are the best way to explore and test endpoints
