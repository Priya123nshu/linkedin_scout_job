# LinkedIn MCP Client

A Python client library and CLI tool for interacting with the [LinkedIn MCP Server](https://github.com/stickerdaniel/linkedin-mcp-server). This client allows you to programmatically access LinkedIn profiles, companies, job postings, and more through the Model Context Protocol (MCP).

## Features

- 🔌 Connect to LinkedIn MCP Server via stdio or HTTP
- 👤 Get detailed LinkedIn person profiles
- 🏢 Retrieve company information and posts
- 💼 Search and get job details
- 🖥️ Interactive CLI mode
- 📚 Simple Python API

## Installation

### Prerequisites

1. **Install the LinkedIn MCP Server** (choose one method):

   **Option 1: Using uvx (Recommended)**
   ```bash
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Create a session (first time only)
   uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --get-session
   ```

   **Option 2: Using Docker**
   ```bash
   docker pull stickerdaniel/linkedin-mcp-server:latest
   ```

2. **Install this client**:
   ```bash
   pip install -r requirements.txt
   # Or for development:
   pip install -e .
   ```

## Quick Start

### Using the CLI

**Interactive Mode:**
```bash
python cli.py interactive
```

**Command Mode:**
```bash
# Get a person profile
python cli.py person "https://www.linkedin.com/in/stickerdaniel/"

# Get a company profile
python cli.py company "https://www.linkedin.com/company/anthropic/"

# Get company posts
python cli.py posts "https://www.linkedin.com/company/anthropic/" --limit 5

# Search for jobs
python cli.py search --keywords "Python Developer" --location "San Francisco" --limit 10

# Get job details
python cli.py job "https://www.linkedin.com/jobs/view/4252026496"

# List available tools
python cli.py list-tools
```

### Using the Python API

```python
import asyncio
from linkedin_mcp_client import LinkedInMCPClient

async def main():
    # Create client (defaults to stdio transport)
    client = LinkedInMCPClient()
    
    # Connect to server
    await client.connect()
    
    try:
        # Get person profile
        profile = await client.get_person_profile(
            "https://www.linkedin.com/in/stickerdaniel/"
        )
        print(profile)
        
        # Get company profile
        company = await client.get_company_profile(
            "https://www.linkedin.com/company/anthropic/"
        )
        print(company)
        
        # Search for jobs
        jobs = await client.search_jobs(
            keywords="Python Developer",
            location="San Francisco",
            limit=10
        )
        print(jobs)
        
    finally:
        # Clean up
        await client.disconnect()

# Or use context manager
async def main_with_context():
    async with LinkedInMCPClient().session() as client:
        profile = await client.get_person_profile(
            "https://www.linkedin.com/in/stickerdaniel/"
        )
        print(profile)

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

### Transport Modes

**stdio (Default):**
The client spawns the MCP server process and communicates via stdin/stdout.

```python
client = LinkedInMCPClient(
    transport="stdio",
    command=["uvx", "--from", "git+https://github.com/stickerdaniel/linkedin-mcp-server", "linkedin-mcp-server"]
)
```

**HTTP:**
Connect to a running MCP server via HTTP (useful for remote servers or Docker).

```python
client = LinkedInMCPClient(
    transport="http",
    http_url="http://127.0.0.1:8000/mcp"
)
```

To run the server in HTTP mode:
```bash
uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server \
  --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp
```

### Custom Server Command

If you have the server installed locally or want to use Docker:

```python
# Local installation
client = LinkedInMCPClient(
    command=["uv", "run", "-m", "linkedin_mcp_server"]
)

# Docker
client = LinkedInMCPClient(
    command=["docker", "run", "-i", "--rm", "stickerdaniel/linkedin-mcp-server:latest"]
)
```

## Available Methods

### `get_person_profile(url: str) -> Dict`
Get detailed profile information including work history, education, contacts, and interests.

### `get_company_profile(url: str) -> Dict`
Extract company information including employees and affiliated companies.

### `get_company_posts(url: str, limit: Optional[int] = None) -> Dict`
Get recent posts from a company's LinkedIn feed.

### `search_jobs(keywords: Optional[str] = None, location: Optional[str] = None, limit: Optional[int] = None) -> Dict`
Search for jobs with keywords and location filters.

### `get_job_details(url: str) -> Dict`
Get detailed information about a specific job posting.

### `close_session() -> Dict`
Close browser session and clean up resources.

### `list_tools() -> List[Dict]`
List all available tools from the server.

## CLI Options

```
usage: cli.py [-h] [--transport {stdio,http}] [--http-url HTTP_URL]
              [--command COMMAND [COMMAND ...]] [--timeout TIMEOUT]
              {list-tools,person,company,posts,search,job,close,interactive} ...

LinkedIn MCP Client - Interact with LinkedIn via MCP Server

options:
  -h, --help            show this help message and exit
  --transport {stdio,http}
                        Transport mode (default: stdio)
  --http-url HTTP_URL   HTTP URL for server (default: http://127.0.0.1:8000/mcp)
  --command COMMAND [COMMAND ...]
                        Command to run server (for stdio mode)
  --timeout TIMEOUT     Request timeout in seconds (default: 30)

Commands:
  list-tools            List available tools
  person                Get person profile
  company               Get company profile
  posts                 Get company posts
  search                Search for jobs
  job                   Get job details
  close                 Close session
  interactive           Start interactive mode
```

## Examples

### Example 1: Research a Candidate

```python
async def research_candidate(profile_url: str):
    async with LinkedInMCPClient().session() as client:
        profile = await client.get_person_profile(profile_url)
        
        print(f"Name: {profile.get('name')}")
        print(f"Headline: {profile.get('headline')}")
        print(f"Experience: {len(profile.get('experiences', []))} positions")
        print(f"Education: {len(profile.get('educations', []))} institutions")
        
        return profile
```

### Example 2: Monitor Company Posts

```python
async def monitor_company(company_url: str):
    async with LinkedInMCPClient().session() as client:
        posts = await client.get_company_posts(company_url, limit=10)
        
        for post in posts.get('posts', []):
            print(f"Date: {post.get('date')}")
            print(f"Content: {post.get('content', '')[:100]}...")
            print("---")
```

### Example 3: Job Search Automation

```python
async def find_jobs(keywords: str, location: str):
    async with LinkedInMCPClient().session() as client:
        results = await client.search_jobs(
            keywords=keywords,
            location=location,
            limit=20
        )
        
        jobs = results.get('jobs', [])
        print(f"Found {len(jobs)} jobs")
        
        for job in jobs:
            print(f"{job.get('title')} at {job.get('company')}")
            print(f"  {job.get('url')}")
```

## Error Handling

The client provides specific exception types:

```python
from linkedin_mcp_client.exceptions import (
    LinkedInMCPError,
    LinkedInMCPConnectionError,
    LinkedInMCPToolError,
    LinkedInMCPAuthenticationError,
)

try:
    profile = await client.get_person_profile(url)
except LinkedInMCPConnectionError:
    print("Failed to connect to server")
except LinkedInMCPAuthenticationError:
    print("Authentication failed - run --get-session")
except LinkedInMCPToolError as e:
    print(f"Tool error: {e}")
```

## Troubleshooting

### Connection Issues

**Problem:** `Connection error: Failed to start server`

**Solution:** Make sure the LinkedIn MCP server is installed and accessible:
```bash
uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --help
```

### Authentication Issues

**Problem:** `Authentication error`

**Solution:** Create or refresh your session:
```bash
uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --get-session
```

### HTTP Mode Issues

**Problem:** HTTP connection fails

**Solution:** Make sure the server is running in HTTP mode:
```bash
uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server \
  --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp
```

## License

This project is licensed under the Apache 2.0 license.

## Related Projects

- [LinkedIn MCP Server](https://github.com/stickerdaniel/linkedin-mcp-server) - The MCP server this client connects to
- [Model Context Protocol](https://modelcontextprotocol.io/) - The protocol specification

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
#   l i n k e d i n _ s c o u t _ j o b  
 