# 🚀 Quick Start Guide

## Prerequisites

1. **Python 3.8+** installed
2. **Node.js 18+** and npm/yarn installed
3. **Clerk Account** - Sign up at [clerk.com](https://clerk.com)
4. **LinkedIn MCP Server** - Will be installed automatically

## Step-by-Step Setup

### 1. Set Up LinkedIn MCP Server (One-Time)

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create LinkedIn session
uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --get-session
```

This will open a browser window. Log in to LinkedIn and complete any 2FA/captcha. The session will be saved automatically.

### 2. Set Up Clerk Authentication

1. Go to [clerk.com](https://clerk.com) and create an account
2. Create a new application
3. Copy your **Publishable Key** and **Secret Key**
4. Note your **JWKS URL** (usually `https://api.clerk.com/.well-known/jwks.json`)

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy env.example .env  # Windows
# or
cp env.example .env    # Mac/Linux

# Edit .env and add your Clerk keys:
# CLERK_PUBLISHABLE_KEY=pk_test_...
# CLERK_SECRET_KEY=sk_test_...
```

### 4. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
# or
yarn install

# Create .env.local file
copy env.example .env.local  # Windows
# or
cp env.example .env.local    # Mac/Linux

# Edit .env.local and add:
# NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
# CLERK_SECRET_KEY=sk_test_...
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

Backend will run on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# or
yarn dev
```

Frontend will run on `http://localhost:3000`

### 6. Access the Application

1. Open `http://localhost:3000` in your browser
2. Sign in with Clerk (you'll be redirected to Clerk's sign-in page)
3. Once signed in, you can use all the LinkedIn MCP features!

## Features

✅ **Person Profile** - Get detailed LinkedIn profiles  
✅ **Company Profile** - Retrieve company information  
✅ **Company Posts** - View recent company posts  
✅ **Job Search** - Search jobs with filters including **time posted** (1h, 24h, 7d, 30d)  
✅ **Job Details** - Get detailed job information  

## Troubleshooting

### Backend won't start
- Make sure you have a LinkedIn session: `~/.linkedin-mcp/session.json`
- If missing, run: `uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --get-session`

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Check CORS settings in backend `.env`

### Clerk authentication errors
- Verify your Clerk keys are correct
- Make sure you're using the correct environment (test vs production keys)
- Check Clerk dashboard for any configuration issues

## Next Steps

- Read [README_FULLSTACK.md](README_FULLSTACK.md) for detailed documentation
- Check out the API endpoints in `backend/main.py`
- Explore the frontend components in `frontend/app/components/`

## Need Help?

- Check the [LinkedIn MCP Server documentation](https://github.com/stickerdaniel/linkedin-mcp-server)
- Review [Clerk documentation](https://clerk.com/docs)
- Check the troubleshooting section in [README_FULLSTACK.md](README_FULLSTACK.md)
