
import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession
from linkedin_utils import get_server_parameters
import json

async def main():
    url = "https://www.linkedin.com/jobs/view/4365029569/"
    server_params = get_server_parameters()
    
    print(f"Testing search_jobs with time_posted")

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("Calling search_jobs with time_posted...")
                result = await session.call_tool("search_jobs", arguments={
                    "keywords": "react", 
                    "location": "India", 
                    "limit": 1,
                    "time_posted": "24h"
                })
                
                if result.content:
                    text = result.content[0].text
                    print("--- WRITING TO debug_output.txt ---")
                    with open("debug_output.txt", "w", encoding="utf-8") as f:
                        f.write(text)
                    print("--- DONE WRITING ---")
                    
                    try:
                        data = json.loads(text)
                        print("JSON Parse Success")
                    except Exception as e:
                        print(f"JSON Parse Error: {e}")
                else:
                    print("No content returned")

    except Exception as e:
        print(f"Script Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
