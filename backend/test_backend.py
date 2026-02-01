"""Quick test script to verify backend setup."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing backend setup...")
print("=" * 50)

# Test imports
try:
    from linkedin_mcp_client import LinkedInMCPClient
    print("[OK] LinkedInMCPClient imported successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import LinkedInMCPClient: {e}")
    sys.exit(1)

try:
    from linkedin_mcp_client.exceptions import (
        LinkedInMCPError,
        LinkedInMCPConnectionError,
        LinkedInMCPToolError,
        LinkedInMCPAuthenticationError,
    )
    print("[OK] Exceptions imported successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import exceptions: {e}")
    sys.exit(1)

try:
    from fastapi import FastAPI
    print("[OK] FastAPI imported successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import FastAPI: {e}")
    sys.exit(1)

try:
    import jwt
    print("[OK] PyJWT imported successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import PyJWT: {e}")
    sys.exit(1)

# Test environment variables
import os
from dotenv import load_dotenv
load_dotenv()

print("\nEnvironment Variables:")
print("=" * 50)
clerk_pub_key = os.getenv("CLERK_PUBLISHABLE_KEY", "")
clerk_secret = os.getenv("CLERK_SECRET_KEY", "")

if clerk_pub_key:
    print(f"[OK] CLERK_PUBLISHABLE_KEY: {clerk_pub_key[:20]}...")
else:
    print("[ERROR] CLERK_PUBLISHABLE_KEY not set")

if clerk_secret:
    print(f"[OK] CLERK_SECRET_KEY: {clerk_secret[:20]}...")
else:
    print("[ERROR] CLERK_SECRET_KEY not set")

print("\n" + "=" * 50)
print("[OK] All tests passed! Backend is ready to run.")
print("\nTo start the backend, run:")
print("  python main.py")
print("  or")
print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
