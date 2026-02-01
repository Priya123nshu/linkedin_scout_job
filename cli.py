"""Command-line interface for LinkedIn MCP Client."""

import asyncio
import argparse
import json
import sys
from typing import Optional
from pathlib import Path

from linkedin_mcp_client import LinkedInMCPClient
from linkedin_mcp_client.exceptions import (
    LinkedInMCPError,
    LinkedInMCPConnectionError,
    LinkedInMCPToolError,
    LinkedInMCPAuthenticationError,
)


def print_json(data: dict, indent: int = 2):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=indent, ensure_ascii=False))


async def cmd_list_tools(client: LinkedInMCPClient):
    """List available tools."""
    try:
        tools = await client.list_tools()
        print(f"\nAvailable tools ({len(tools)}):\n")
        for tool in tools:
            print(f"  • {tool.get('name', 'unknown')}")
            if 'description' in tool:
                print(f"    {tool['description']}")
            print()
    except LinkedInMCPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


async def cmd_get_person_profile(client: LinkedInMCPClient, url: str):
    """Get person profile."""
    try:
        result = await client.get_person_profile(url)
        print_json(result)
    except LinkedInMCPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


async def cmd_get_company_profile(client: LinkedInMCPClient, url: str):
    """Get company profile."""
    try:
        result = await client.get_company_profile(url)
        print_json(result)
    except LinkedInMCPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


async def cmd_get_company_posts(client: LinkedInMCPClient, url: str, limit: Optional[int]):
    """Get company posts."""
    try:
        result = await client.get_company_posts(url, limit=limit)
        print_json(result)
    except LinkedInMCPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


async def cmd_search_jobs(
    client: LinkedInMCPClient,
    keywords: Optional[str],
    location: Optional[str],
    limit: Optional[int],
    time_posted: Optional[str] = None,
):
    """Search for jobs."""
    try:
        result = await client.search_jobs(
            keywords=keywords,
            location=location,
            limit=limit,
            time_posted=time_posted
        )
        print_json(result)
    except LinkedInMCPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


async def cmd_get_job_details(client: LinkedInMCPClient, url: str):
    """Get job details."""
    try:
        result = await client.get_job_details(url)
        print_json(result)
    except LinkedInMCPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


async def cmd_close_session(client: LinkedInMCPClient):
    """Close session."""
    try:
        result = await client.close_session()
        print_json(result)
    except LinkedInMCPError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


async def interactive_mode(client: LinkedInMCPClient):
    """Interactive mode for exploring tools."""
    print("LinkedIn MCP Client - Interactive Mode")
    print("Type 'help' for commands, 'exit' to quit\n")

    while True:
        try:
            command = input("linkedin> ").strip()
            
            if not command:
                continue
            
            if command == "exit":
                break
            elif command == "help":
                print("\nCommands:")
                print("  list-tools              - List available tools")
                print("  person <url>            - Get person profile")
                print("  company <url>           - Get company profile")
                print("  posts <url> [limit]     - Get company posts")
                print("  search [keywords] [location] [limit] - Search jobs")
                print("  job <url>               - Get job details")
                print("  close                   - Close session")
                print("  exit                    - Exit interactive mode")
                print()
            elif command == "list-tools":
                await cmd_list_tools(client)
            elif command.startswith("person "):
                url = command[7:].strip()
                if url:
                    await cmd_get_person_profile(client, url)
                else:
                    print("Error: URL required", file=sys.stderr)
            elif command.startswith("company "):
                url = command[8:].strip()
                if url:
                    await cmd_get_company_profile(client, url)
                else:
                    print("Error: URL required", file=sys.stderr)
            elif command.startswith("posts "):
                parts = command[6:].strip().split()
                url = parts[0] if parts else None
                limit = int(parts[1]) if len(parts) > 1 else None
                if url:
                    await cmd_get_company_posts(client, url, limit)
                else:
                    print("Error: URL required", file=sys.stderr)
            elif command.startswith("search "):
                parts = command[7:].strip().split(maxsplit=3)
                keywords = parts[0] if len(parts) > 0 and parts[0] else None
                location = parts[1] if len(parts) > 1 and parts[1] else None
                limit = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
                await cmd_search_jobs(client, keywords, location, limit)
            elif command.startswith("job "):
                url = command[4:].strip()
                if url:
                    await cmd_get_job_details(client, url)
                else:
                    print("Error: URL required", file=sys.stderr)
            elif command == "close":
                await cmd_close_session(client)
            else:
                print(f"Unknown command: {command}. Type 'help' for commands.", file=sys.stderr)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="LinkedIn MCP Client - Interact with LinkedIn via MCP Server"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport mode (default: stdio)",
    )
    parser.add_argument(
        "--http-url",
        default="http://127.0.0.1:8000/mcp",
        help="HTTP URL for server (default: http://127.0.0.1:8000/mcp)",
    )
    parser.add_argument(
        "--command",
        nargs="+",
        dest="command_list",
        help="Command to run server (for stdio mode)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List tools
    subparsers.add_parser("list-tools", help="List available tools")

    # Get person profile
    person_parser = subparsers.add_parser("person", help="Get person profile")
    person_parser.add_argument("url", help="LinkedIn profile URL")

    # Get company profile
    company_parser = subparsers.add_parser("company", help="Get company profile")
    company_parser.add_argument("url", help="LinkedIn company URL")

    # Get company posts
    posts_parser = subparsers.add_parser("posts", help="Get company posts")
    posts_parser.add_argument("url", help="LinkedIn company URL")
    posts_parser.add_argument("--limit", type=int, help="Maximum number of posts")

    # Search jobs
    search_parser = subparsers.add_parser("search", help="Search for jobs")
    search_parser.add_argument("--keywords", help="Search keywords")
    search_parser.add_argument("--location", help="Location filter")
    search_parser.add_argument("--limit", type=int, help="Maximum number of results")
    search_parser.add_argument("--time-posted", help="Time filter (e.g., 1h, 24h, 7d, 30d)")

    # Get job details
    job_parser = subparsers.add_parser("job", help="Get job details")
    job_parser.add_argument("url", help="LinkedIn job URL")

    # Close session
    subparsers.add_parser("close", help="Close session")

    # Interactive mode
    subparsers.add_parser("interactive", help="Start interactive mode")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Create client
    client = LinkedInMCPClient(
        transport=args.transport,
        command=args.command_list if hasattr(args, 'command_list') and args.command_list else None,
        http_url=args.http_url,
        timeout=args.timeout,
    )

    async def run():
        try:
            await client.connect()

            if args.command == "list-tools":
                await cmd_list_tools(client)
            elif args.command == "person":
                await cmd_get_person_profile(client, args.url)
            elif args.command == "company":
                await cmd_get_company_profile(client, args.url)
            elif args.command == "posts":
                await cmd_get_company_posts(client, args.url, args.limit)
            elif args.command == "search":
                await cmd_search_jobs(client, args.keywords, args.location, args.limit, args.time_posted)
            elif args.command == "job":
                await cmd_get_job_details(client, args.url)
            elif args.command == "close":
                await cmd_close_session(client)
            elif args.command == "interactive":
                await interactive_mode(client)

            await client.disconnect()
        except LinkedInMCPConnectionError as e:
            print(f"Connection error: {e}", file=sys.stderr)
            print("\nMake sure the LinkedIn MCP server is running:", file=sys.stderr)
            print("  uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server", file=sys.stderr)
            sys.exit(1)
        except LinkedInMCPAuthenticationError as e:
            print(f"Authentication error: {e}", file=sys.stderr)
            print("\nYou may need to create a session:", file=sys.stderr)
            print("  uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --get-session", file=sys.stderr)
            sys.exit(1)
        except LinkedInMCPError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    asyncio.run(run())


if __name__ == "__main__":
    main()
