# Quick Start Guide

## ✅ Servers Started!

Both backend and frontend servers should now be running in separate PowerShell windows.

### Access Points

- **Frontend Application**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/health

### What to Do Now

1. **Open the Frontend**
   - Go to http://localhost:5173 in your browser
   - You should see the login page

2. **Test the Backend API**
   - Go to http://localhost:8000/api/docs
   - This is an interactive API documentation where you can test all endpoints

3. **Create Your First Account**
   - On the frontend login page, click "Sign up"
   - Or use the API docs to register:
     - Go to `/api/v1/auth/register`
     - Click "Try it out"
     - Enter:
       ```json
       {
         "email": "test@example.com",
         "password": "Test123!@#",
         "full_name": "Test User"
       }
       ```
     - Click "Execute"

4. **Login**
   - Use the same credentials to login
   - You'll get an access token
   - Use this token in the "Authorize" button at the top of the API docs

### Server Windows

You should see two PowerShell windows:
- **Backend Window**: Shows uvicorn server logs
- **Frontend Window**: Shows Vite dev server logs

### To Stop Servers

Simply close the PowerShell windows, or press `Ctrl+C` in each window.

### Troubleshooting

#### Backend Not Starting?
- Check the backend PowerShell window for error messages
- Make sure port 8000 is not already in use
- Verify Python virtual environment is activated

#### Frontend Not Starting?
- Check the frontend PowerShell window for error messages
- Make sure port 5173 is not already in use
- Verify Node.js is installed: `node --version`

#### Database Errors?
- The app will work for basic testing without a database
- For full functionality, you need PostgreSQL
- You can use Docker: `docker compose up -d postgres redis`

### Next Steps

1. Explore the API documentation at http://localhost:8000/api/docs
2. Test creating a user and logging in
3. Try uploading a document (requires S3 setup for full functionality)
4. Connect an email account (requires OAuth setup)

### Need Help?

- Check `TESTING.md` for detailed testing instructions
- Check `README.md` for full documentation
- Review the API docs at http://localhost:8000/api/docs
