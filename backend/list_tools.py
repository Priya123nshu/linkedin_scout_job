
import asyncio
import json
from mcp.client.stdio import stdio_client
from mcp import ClientSession
from linkedin_utils import get_server_parameters

async def main():
    server_params = get_server_parameters()
    
    print("Listing tools...")

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                result = await session.list_tools()
                # result is ListToolsResult, tools attribute is list of Tool
                if result.tools:
                    for tool in result.tools:
                        if tool.name in ["get_person_profile", "get_company_profile", "get_company_posts"]:
                            print(f"\nTOOL: {tool.name}")
                            print(f"SCHEMA: {json.dumps(tool.inputSchema, indent=2)}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
