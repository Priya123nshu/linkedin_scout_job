import sys
import os
import asyncio
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    try:
        # Ensure we can import linkedin_utils
        sys.path.append(os.getcwd())
        
        import linkedin_utils
        print(f"Using linkedin_utils from: {linkedin_utils.__file__}")
        
        from linkedin_utils import get_server_parameters, search_jobs
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        server_params = get_server_parameters()
        print("Starting MCP client...")
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("MCP Session Initialized.")
                
                keyword = "React"
                print(f"\n--- Test 1: Direct Tool Call (No time_posted) ---")
                try:
                    res = await session.call_tool("search_jobs", arguments={"keywords": keyword, "location": "India", "limit": 2})
                    if res.content:
                        text = res.content[0].text
                        print(f"Success! Content length: {len(text)}")
                        # print(f"Snippet: {text[:200]}...")
                    else:
                        print("Success but NO content?")
                except Exception as e:
                    print(f"FAILED: {e}")
                
                print(f"\n--- Test 2: linkedin_utils.search_jobs (WITH time_posted='24h') ---")
                try:
                    jobs = await search_jobs(session, keyword, limit=2, location="India", time_posted="24h")
                    print(f"search_jobs returned {len(jobs)} jobs.")
                    for j in jobs:
                        print(f" - {j.get('title', 'No Title')} ({j.get('url', 'No URL')})")
                except Exception as e:
                    print(f"FAILED: {e}")
                    traceback.print_exc()

    except Exception as e:
        print(f"Top Level Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
