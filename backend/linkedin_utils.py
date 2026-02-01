
import os
import json
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters

load_dotenv()

def get_server_parameters():
    # Use local MCP server
    import os
    import tempfile
    
    local_mcp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "linkedin_mcp_server_local")
    
    env = os.environ.copy()
    
    # Check for BYO-Cookie from main.py API (supports Render/Vercel ephemeral session)
    cookie_path = os.path.join(tempfile.gettempdir(), "linkedin_cookie.txt")
    if os.path.exists(cookie_path):
        try:
            with open(cookie_path, "r", encoding="utf-8") as f:
                cookie = f.read().strip()
                if cookie:
                    env["LINKEDIN_COOKIE"] = cookie
                    # print(f"DEBUG: Injected LINKEDIN_COOKIE from {cookie_path}")
        except Exception as e:
            print(f"Error reading cookie file: {e}")

    return StdioServerParameters(
        command="python",
        args=["-m", "linkedin_mcp_server.cli_main", "--transport", "stdio"],
        env=env
    )

async def search_jobs(session: ClientSession, keyword: str, limit: int = 10, location: str = "India", time_posted: str = None):
    import asyncio
    from json import JSONDecoder
    
    arguments = {
        "keywords": keyword,
        "location": location,
        "limit": limit
    }
    # User confirmed time_posted is supported by their version/code.
    # BUT verified via debug script that the running uvx version REJECTS it.
    # Must keep it disabled until server is updated or run locally.
    # if time_posted:
    #    arguments["time_posted"] = time_posted
    
    decoder = JSONDecoder()

    def safe_parse_json(text):
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            if "Extra data" in str(e):
                try:
                    obj, _ = decoder.raw_decode(text)
                    return obj
                except:
                    pass
            # print(f"DEBUG: JSON parse failed for text: {text[:100]}...")
            return None

    try:
        # 1. Search for URLs
        print(f"Calling search_jobs tool for: {keyword}")
        result = await session.call_tool("search_jobs", arguments=arguments)
        job_urls = []
        
        # Iterate over all content blocks as per user suggestion
        # 2. Extract job URLs and Debug Info
        debug_info = {}
        
        if result.content:
            for content in result.content:
                if content.type == "text":
                    text = content.text
                    print(f"DEBUG: Raw Tool Response: {text[:500]}...") # Log first 500 chars
                    data = safe_parse_json(text)
                    if not data:
                        print(f"DEBUG: JSON Parsing Failed for: {text}")
                    
                    if data:
                        if isinstance(data, dict):
                            urls = data.get("job_urls", [])
                            job_urls.extend(urls)
                            # Extract debug info if present
                            if "debug_info" in data:
                                debug_info = data["debug_info"]
                        elif isinstance(data, list):
                            urls = [u for u in data if isinstance(u, str)]
                            job_urls.extend(urls)
        
        print(f"Found {len(job_urls)} URLs for {keyword}. Fetching details...")

        # 2. Fetch details for each URL concurrently
        async def get_details(url):
            try:
                # Extract job_id from URL
                import re
                job_id = None
                match = re.search(r'view/(\d+)', url)
                if match:
                    job_id = match.group(1)
                
                if not job_id:
                     print(f"Could not extract job_id from {url}")
                     return None

                # Call tool with job_id
                res = await session.call_tool("get_job_details", arguments={"job_id": job_id})
                if res.content:
                    text = res.content[0].text
                    details = safe_parse_json(text)
                    
                    if isinstance(details, dict):
                        if "url" not in details:
                            details["url"] = url
                        return details
                return None
            except Exception as e:
                print(f"Error fetching details for {url}: {e}")
                return None

        if not job_urls:
            return [], debug_info

        tasks = [get_details(url) for url in job_urls[:limit]]
        jobs = await asyncio.gather(*tasks)
        
        valid_jobs = [j for j in jobs if j is not None]
        print(f"Successfully fetched {len(valid_jobs)} job details")
        return valid_jobs, debug_info

    except Exception as e:
        print(f"Error in search_jobs workflow: {e}")
        return [], {"error": str(e)}

async def get_company_profile(session: ClientSession, url: str):
    import json
    from json import JSONDecoder
    decoder = JSONDecoder()
    
    # Extract company_name from URL
    # https://www.linkedin.com/company/apple/ -> apple
    if "linkedin.com/company/" in url:
        company_name = url.split("linkedin.com/company/")[1].split("/")[0]
    else:
        # Fallback if just name provided? No, assume URL
        company_name = url
        
    try:
        print(f"Fetching company profile for: {company_name}")
        result = await session.call_tool("get_company_profile", arguments={"company_name": company_name})
        
        if result.content:
            text = result.content[0].text
            # Write to file for debugging
            try:
                with open("debug_company_profile.json", "w", encoding="utf-8") as f:
                    f.write(text)
            except:
                pass
            
            # Safe parse
            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                 if "Extra data" in str(e):
                    try:
                        obj, _ = decoder.raw_decode(text)
                        return obj
                    except:
                        pass
                 return None
        return None
    except Exception as e:
        print(f"Error fetching company profile: {e}")
        return None

async def get_company_posts(session: ClientSession, url: str, limit: int = 10):
    import json
    from json import JSONDecoder
    decoder = JSONDecoder()

    # Extract company_name
    if "linkedin.com/company/" in url:
        company_name = url.split("linkedin.com/company/")[1].split("/")[0]
    else:
        company_name = url

    try:
        print(f"Fetching company posts for: {company_name}")
        result = await session.call_tool("get_company_posts", arguments={"company_name": company_name, "limit": limit})
        
        if result.content:
            text = result.content[0].text
            # Safe parse
            try:
                data = json.loads(text)
                return data
            except json.JSONDecodeError as e:
                 if "Extra data" in str(e):
                    try:
                        obj, _ = decoder.raw_decode(text)
                        return obj
                    except:
                        pass
                 return None
        return None
    except Exception as e:
        print(f"Error fetching company posts: {e}")
        return None

async def get_person_profile(session: ClientSession, url: str):
    import json
    from json import JSONDecoder
    decoder = JSONDecoder()

    # Extract linkedin_username
    # https://www.linkedin.com/in/priyanshu-kumar-980b50179/ -> priyanshu-kumar-980b50179
    if "linkedin.com/in/" in url:
        username = url.split("linkedin.com/in/")[1].split("/")[0]
    else:
        username = url

    try:
        print(f"Fetching person profile for: {username}")
        result = await session.call_tool("get_person_profile", arguments={"linkedin_username": username})
        
        if result.content:
            text = result.content[0].text
            
            # Write to file for debugging
            try:
                with open("debug_person_profile.json", "w", encoding="utf-8") as f:
                    f.write(text)
            except:
                pass

            # Safe parse
            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                 if "Extra data" in str(e):
                    try:
                        obj, _ = decoder.raw_decode(text)
                        return obj
                    except:
                        pass
                 return None
        return None
    except Exception as e:
        print(f"Error fetching person profile: {e}")
        return None
