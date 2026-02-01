"""Example usage of the LinkedIn MCP Client."""

import asyncio
from linkedin_mcp_client import LinkedInMCPClient
from linkedin_mcp_client.exceptions import LinkedInMCPError


async def example_get_person_profile():
    """Example: Get a person's LinkedIn profile."""
    print("Example 1: Get Person Profile")
    print("=" * 50)
    
    async with LinkedInMCPClient().session() as client:
        try:
            profile = await client.get_person_profile(
                "https://www.linkedin.com/in/stickerdaniel/"
            )
            print(f"Name: {profile.get('name', 'N/A')}")
            print(f"Headline: {profile.get('headline', 'N/A')}")
            print(f"Location: {profile.get('location', 'N/A')}")
            if 'experiences' in profile:
                print(f"Experiences: {len(profile['experiences'])} positions")
            if 'educations' in profile:
                print(f"Education: {len(profile['educations'])} institutions")
        except LinkedInMCPError as e:
            print(f"Error: {e}")
    print()


async def example_get_company_profile():
    """Example: Get a company's LinkedIn profile."""
    print("Example 2: Get Company Profile")
    print("=" * 50)
    
    async with LinkedInMCPClient().session() as client:
        try:
            company = await client.get_company_profile(
                "https://www.linkedin.com/company/anthropic/"
            )
            print(f"Company: {company.get('name', 'N/A')}")
            print(f"Description: {company.get('description', 'N/A')[:100]}...")
            print(f"Website: {company.get('website', 'N/A')}")
            if 'employees' in company:
                print(f"Employees: {company['employees']}")
        except LinkedInMCPError as e:
            print(f"Error: {e}")
    print()


async def example_get_company_posts():
    """Example: Get recent company posts."""
    print("Example 3: Get Company Posts")
    print("=" * 50)
    
    async with LinkedInMCPClient().session() as client:
        try:
            posts = await client.get_company_posts(
                "https://www.linkedin.com/company/anthropic/",
                limit=3
            )
            if 'posts' in posts:
                print(f"Found {len(posts['posts'])} posts:")
                for i, post in enumerate(posts['posts'][:3], 1):
                    print(f"\nPost {i}:")
                    print(f"  Date: {post.get('date', 'N/A')}")
                    print(f"  Content: {post.get('content', 'N/A')[:100]}...")
            else:
                print("No posts found")
        except LinkedInMCPError as e:
            print(f"Error: {e}")
    print()


async def example_search_jobs():
    """Example: Search for jobs."""
    print("Example 4: Search Jobs")
    print("=" * 50)
    
    async with LinkedInMCPClient().session() as client:
        try:
            results = await client.search_jobs(
                keywords="Python Developer",
                location="San Francisco",
                limit=5
            )
            if 'jobs' in results:
                print(f"Found {len(results['jobs'])} jobs:")
                for i, job in enumerate(results['jobs'][:5], 1):
                    print(f"\nJob {i}:")
                    print(f"  Title: {job.get('title', 'N/A')}")
                    print(f"  Company: {job.get('company', 'N/A')}")
                    print(f"  Location: {job.get('location', 'N/A')}")
                    print(f"  URL: {job.get('url', 'N/A')}")
            else:
                print("No jobs found")
        except LinkedInMCPError as e:
            print(f"Error: {e}")
    print()


async def example_get_job_details():
    """Example: Get detailed job information."""
    print("Example 5: Get Job Details")
    print("=" * 50)
    
    async with LinkedInMCPClient().session() as client:
        try:
            job = await client.get_job_details(
                "https://www.linkedin.com/jobs/view/4252026496"
            )
            print(f"Title: {job.get('title', 'N/A')}")
            print(f"Company: {job.get('company', 'N/A')}")
            print(f"Location: {job.get('location', 'N/A')}")
            print(f"Description: {job.get('description', 'N/A')[:200]}...")
        except LinkedInMCPError as e:
            print(f"Error: {e}")
    print()


async def example_list_tools():
    """Example: List available tools."""
    print("Example 6: List Available Tools")
    print("=" * 50)
    
    async with LinkedInMCPClient().session() as client:
        try:
            tools = await client.list_tools()
            print(f"Available tools ({len(tools)}):")
            for tool in tools:
                print(f"  • {tool.get('name', 'unknown')}")
                if 'description' in tool:
                    print(f"    {tool['description']}")
        except LinkedInMCPError as e:
            print(f"Error: {e}")
    print()


async def example_http_mode():
    """Example: Using HTTP transport mode."""
    print("Example 7: HTTP Transport Mode")
    print("=" * 50)
    print("Note: This requires the server to be running in HTTP mode:")
    print("  uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server \\")
    print("    linkedin-mcp-server --transport streamable-http --host 127.0.0.1 --port 8000")
    print()
    
    client = LinkedInMCPClient(
        transport="http",
        http_url="http://127.0.0.1:8000/mcp"
    )
    
    try:
        await client.connect()
        tools = await client.list_tools()
        print(f"Connected via HTTP! Found {len(tools)} tools.")
        await client.disconnect()
    except LinkedInMCPError as e:
        print(f"Error: {e}")
        print("Make sure the server is running in HTTP mode.")
    print()


async def main():
    """Run all examples."""
    print("\n" + "=" * 50)
    print("LinkedIn MCP Client - Usage Examples")
    print("=" * 50 + "\n")
    
    # Run examples
    await example_list_tools()
    # Uncomment the examples you want to run:
    # await example_get_person_profile()
    # await example_get_company_profile()
    # await example_get_company_posts()
    # await example_search_jobs()
    # await example_get_job_details()
    # await example_http_mode()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
