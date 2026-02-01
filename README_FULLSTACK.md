# LinkedIn MCP Full-Stack Application

A complete full-stack application with Next.js frontend, FastAPI backend, and Clerk authentication for interacting with LinkedIn via the MCP server.

## Architecture

- **Frontend**: Next.js 14 with TypeScript, Tailwind CSS, and Clerk authentication
- **Backend**: FastAPI with Clerk JWT verification
- **MCP Client**: Python client library for LinkedIn MCP Server

## Prerequisites

1. **LinkedIn MCP Server Setup**:
   ```bash
   # Install uv if needed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Create LinkedIn session (one-time)
   uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --get-session
   ```

2. **Clerk Account**: Sign up at [clerk.com](https://clerk.com) and get your API keys

## Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment and install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Clerk keys
   ```

4. **Run the backend**:
   ```bash
   python main.py
   # Or with uvicorn:
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

The backend will be available at `http://localhost:8000`

## Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   # Or
   yarn install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env.local
   # Edit .env.local and add your Clerk keys and API URL
   ```

4. **Run the frontend**:
   ```bash
   npm run dev
   # Or
   yarn dev
   ```

The frontend will be available at `http://localhost:3000`

## Environment Variables

### Backend (.env)

```env
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
CLERK_JWKS_URL=https://api.clerk.com/.well-known/jwks.json
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
MCP_SERVER_COMMAND=uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Features

### 1. Person Profile
- Get detailed LinkedIn person profiles
- View work experience, education, skills, and more

### 2. Company Profile
- Retrieve company information
- View company details, employees, locations

### 3. Company Posts
- Get recent posts from company LinkedIn feeds
- Configurable post limit

### 4. Job Search
- Search for jobs with keywords and location
- **NEW**: Time filter (past hour, 24 hours, week, month)
- Configurable result limit

### 5. Job Details
- Get detailed information about specific job postings
- View full job descriptions and requirements

## API Endpoints

All endpoints require Clerk authentication via Bearer token.

- `POST /api/person-profile` - Get person profile
- `POST /api/company-profile` - Get company profile
- `POST /api/company-posts` - Get company posts
- `POST /api/job-search` - Search for jobs
- `POST /api/job-details` - Get job details
- `GET /api/tools` - List available tools
- `GET /health` - Health check

## Job Search Time Filter

The job search now supports a `time_posted` parameter with the following options:

- `1h` - Past hour
- `24h` - Past 24 hours
- `7d` - Past week
- `30d` - Past month

Example request:
```json
{
  "keywords": "Python Developer",
  "location": "San Francisco",
  "limit": 10,
  "time_posted": "24h"
}
```

## Development

### Backend Development

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm run dev
```

## Troubleshooting

### Backend Issues

1. **MCP Server Connection Failed**:
   - Make sure the LinkedIn MCP server is installed
   - Verify session exists: `~/.linkedin-mcp/session.json`
   - Run `--get-session` again if needed

2. **Clerk Authentication Errors**:
   - Verify your Clerk keys are correct
   - Check that the JWT token is being sent from frontend

### Frontend Issues

1. **API Connection Errors**:
   - Verify `NEXT_PUBLIC_API_URL` is correct
   - Check that backend is running
   - Verify CORS settings in backend

2. **Clerk Authentication**:
   - Verify `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` is set
   - Check Clerk dashboard for correct configuration

## Production Deployment

### Backend

1. Use a production ASGI server like Gunicorn with Uvicorn workers
2. Set up proper environment variables
3. Configure CORS for your production domain
4. Use HTTPS

### Frontend

1. Build the Next.js app: `npm run build`
2. Deploy to Vercel, Netlify, or your preferred platform
3. Set environment variables in your hosting platform
4. Update `NEXT_PUBLIC_API_URL` to your production backend URL

## License

Apache 2.0
