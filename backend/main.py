
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os

# Import our custom utilities
from mcp.client.stdio import stdio_client
from mcp import ClientSession
from linkedin_utils import (
    get_server_parameters, 
    search_jobs, 
    get_company_profile,
    get_company_posts,
    get_person_profile
)

app = FastAPI(title="LinkedIn Job Search API")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    keywords: List[str]
    location: str = "India"
    limit: int = 10
    time_posted: Optional[str] = None # e.g. "r86400"

class CompanyRequest(BaseModel):
    url: str

class CompanyPostsRequest(BaseModel):
    url: str
    limit: int = 10

class PersonRequest(BaseModel):
    url: str

class SessionRequest(BaseModel):
    li_at: str

@app.post("/api/session")
async def session_endpoint(request: SessionRequest):
    import tempfile
    try:
        cookie_path = os.path.join(tempfile.gettempdir(), "linkedin_cookie.txt")
        print(f"Setting session cookie in: {cookie_path}")
        with open(cookie_path, "w", encoding="utf-8") as f:
            f.write(request.li_at)
        return {"success": True, "message": "Session updated"}
    except Exception as e:
        print(f"Error saving session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    import tempfile
    cookie_path = os.path.join(tempfile.gettempdir(), "linkedin_cookie.txt")
    has_cookie = os.path.exists(cookie_path)
    return {"status": "ok", "has_session": has_cookie}

@app.post("/search")
async def search_endpoint(request: SearchRequest):
    print(f"Received search request: {request}")
    
    all_job_urls = []
    
    # Initialize session params
    server_params = get_server_parameters()

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Iterate through keywords
                for keyword in request.keywords:
                    print(f"Searching for: {keyword}...")
                    try:
                        urls = await search_jobs(
                            session, 
                            keyword, 
                            limit=request.limit, 
                            location=request.location,
                            time_posted=request.time_posted
                        )
                        if urls:
                            # Add to list (allowing duplicates as requested)
                            all_job_urls.extend(urls)
                    except Exception as exc:
                        print(f"Error searching for {keyword}: {exc}")
                        
                    # Small delay between keywords
                    await asyncio.sleep(1)
                    
        return {
            "status": "success",
            "count": len(all_job_urls),
            "jobs": all_job_urls
        }

    except Exception as e:
        print(f"Server error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/company-profile")
async def company_profile_endpoint(request: CompanyRequest):
    print(f"Received company profile request: {request}")
    server_params = get_server_parameters()
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                data = await get_company_profile(session, request.url)
        
        if data:
            if "error" in data:
                 return {"success": False, "error": data.get("message", data["error"])}
            return {"success": True, "data": data}
        else:
            # Return success False but not 500 if simply not found
            return {"success": False, "error": "Company not found or no data returned"}
            
    except Exception as e:
        print(f"Server error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/company-posts")
async def company_posts_endpoint(request: CompanyPostsRequest):
    print(f"Received company posts request: {request}")
    server_params = get_server_parameters()
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                data = await get_company_posts(session, request.url, request.limit)
        
        if data:
            if "error" in data:
                 return {"success": False, "error": data.get("message", data["error"])}
            return {"success": True, "data": data}
        return {"success": False, "error": "No posts found"}

    except Exception as e:
        print(f"Server error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/person-profile")
async def person_profile_endpoint(request: PersonRequest):
    print(f"Received person profile request: {request}")
    server_params = get_server_parameters()
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                data = await get_person_profile(session, request.url)
        
        if data:
            if "error" in data:
                 return {"success": False, "error": data.get("message", data["error"])}
            return {"success": True, "data": data}
        return {"success": False, "error": "Profile not found"}

    except Exception as e:
        print(f"Server error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
