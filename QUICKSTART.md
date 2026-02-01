# Quick Start Guide

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up LinkedIn MCP Server:**
   ```bash
   # Install uv if needed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Create a LinkedIn session (first time only)
   uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --get-session
   ```

3. **Test the connection:**
   ```bash
   python test_connection.py
   ```

## Basic Usage

### Command Line Interface

**Interactive mode:**
```bash
python cli.py interactive
```

**Get a person profile:**
```bash
python cli.py person "https://www.linkedin.com/in/stickerdaniel/"
```

**Get a company profile:**
```bash
python cli.py company "https://www.linkedin.com/company/anthropic/"
```

**Search for jobs:**
```bash
python cli.py search --keywords "Python Developer" --location "San Francisco" --limit 10
```

### Python API

```python
import asyncio
from linkedin_mcp_client import LinkedInMCPClient

async def main():
    async with LinkedInMCPClient().session() as client:
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
        
        # Search jobs
        jobs = await client.search_jobs(
            keywords="Python Developer",
            location="San Francisco",
            limit=10
        )
        print(jobs)

asyncio.run(main())
```

## Run Examples

```bash
python examples.py
```

## Troubleshooting

### Connection Issues

If you get connection errors:
1. Make sure the LinkedIn MCP server is installed
2. Run `python test_connection.py` to diagnose issues
3. Check that you have a valid session: `~/.linkedin-mcp/session.json`

### Authentication Issues

If you get authentication errors:
```bash
uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --get-session
```

### HTTP Mode

To use HTTP transport mode:
1. Start the server in HTTP mode:
   ```bash
   uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server \
     --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp
   ```

2. Use the client with HTTP:
   ```python
   client = LinkedInMCPClient(
       transport="http",
       http_url="http://127.0.0.1:8000/mcp"
   )
   ```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out [examples.py](examples.py) for more usage examples
- Explore the interactive CLI: `python cli.py interactive`
