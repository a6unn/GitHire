# GitHire - Quick Start Guide

## 🚀 Get Up and Running in 5 Minutes

### Current Status
✅ **Backend**: Complete (5/5 modules, 293 tests passing)
✅ **Frontend**: Complete (6/6 phases, 98 tests passing)
🎯 **Ready to test!**

---

## Step 1: Start the Backend API

Open a terminal and run:

```bash
# Navigate to project root
cd /Users/arunkumar/ClaudeCode-Projects/juicebox

# Start the FastAPI backend
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ Backend will be running at: **http://localhost:8000**

---

## Step 2: Start the Frontend App

Open a **NEW terminal** (keep the backend running) and run:

```bash
# Navigate to frontend directory
cd /Users/arunkumar/ClaudeCode-Projects/juicebox/frontend

# Start the Vite dev server
npm run dev
```

**Expected output:**
```
  VITE v7.1.9  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

✅ Frontend will be running at: **http://localhost:5173**

---

## Step 3: Test the Application

### 3.1 Open the App
Open your browser and go to: **http://localhost:5173**

### 3.2 Register a New Account
1. Click "Sign up" or go to **http://localhost:5173/register**
2. Enter your email and password (any valid email format)
3. Click "Create Account"
4. You'll be automatically logged in

### 3.3 Run Your First Pipeline
1. On the Dashboard, you'll see the pipeline execution form
2. Enter a job description, for example:

```
Looking for a Senior Python Developer with 5+ years of experience.
Must have strong skills in FastAPI, SQLAlchemy, and Docker.
Experience with GitHub Actions and CI/CD is a plus.
Remote position, preferably in US/Europe timezone.
```

3. Click "Run Pipeline"
4. Watch the progress bar as it:
   - ✅ Parses the job description
   - ✅ Searches GitHub for candidates
   - ✅ Ranks candidates by fit
   - ✅ Generates personalized outreach messages

5. See the results with:
   - Top 10 ranked candidates
   - Skill match scores
   - Personalized outreach messages
   - Links to GitHub profiles

### 3.4 View Your Projects
1. Click "Projects" in the navigation
2. See all your past pipeline runs
3. Filter by status (completed/failed)
4. Search by job description text
5. Click any project to view details
6. Export results as JSON
7. Delete old projects

---

## Quick Test Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can register a new account
- [ ] Can log in
- [ ] Can run a pipeline with a job description
- [ ] Pipeline completes successfully
- [ ] Can see candidate results with scores
- [ ] Can view outreach messages
- [ ] Can navigate to Projects page
- [ ] Can view project details
- [ ] Can export project results
- [ ] Can delete a project
- [ ] Can log out

---

## Verification Commands

### Check Backend Health
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","modules":["jd_parser","github_sourcer","ranking_engine","outreach_generator","api"]}
```

### Check API Docs
Open in browser: **http://localhost:8000/docs**

---

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is already in use
lsof -i :8000

# If it is, kill the process
kill -9 <PID>

# Or use a different port
uvicorn src.api.main:app --reload --port 8001
```

### Frontend won't start
```bash
# Check if port 5173 is already in use
lsof -i :5173

# If dependencies are missing
cd frontend
npm install

# Clear cache and restart
rm -rf node_modules/.vite
npm run dev
```

### Pipeline fails with API errors
Check that your API keys are set in `.env`:
```bash
cat /Users/arunkumar/ClaudeCode-Projects/juicebox/.env
# Should show:
# OPENAI_API_KEY=sk-...
# GITHUB_TOKEN=github_pat_...
```

### Frontend can't connect to backend
Make sure:
1. Backend is running on port 8000
2. Frontend `.env` has: `VITE_API_BASE_URL=/api`
3. Vite proxy is configured (it is by default)

---

## What's Next?

### Explore Features
- Try different job descriptions (Frontend, Backend, DevOps roles)
- Compare candidate rankings
- Test formal vs casual outreach tone (coming soon)
- Export and analyze results

### API Testing
Use the interactive Swagger UI:
- **http://localhost:8000/docs**
- Test all endpoints directly from browser
- See request/response schemas

### Run Tests
```bash
# Backend tests (293 tests)
cd /Users/arunkumar/ClaudeCode-Projects/juicebox
pytest

# Frontend tests (98 tests)
cd /Users/arunkumar/ClaudeCode-Projects/juicebox/frontend
npm test
```

---

## System Requirements Met

✅ **Backend**:
- Python 3.9+ (you have 3.9.6)
- All dependencies installed
- Database ready (SQLite)
- API keys configured

✅ **Frontend**:
- Node.js 18+ (you have 18.20.8)
- All dependencies installed
- Vite configured
- Environment variables set

---

## Support

If you encounter issues:
1. Check this guide first
2. Look at logs in the terminal
3. Check the main README.md for detailed docs
4. Verify API keys are valid

**Have fun testing GitHire!** 🎉
