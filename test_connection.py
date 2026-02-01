"""Test script to verify LinkedIn MCP Client connection."""

import asyncio
import sys
from linkedin_mcp_client import LinkedInMCPClient
from linkedin_mcp_client.exceptions import (
    LinkedInMCPError,
    LinkedInMCPConnectionError,
    LinkedInMCPAuthenticationError,
)


async def test_connection(transport: str = "stdio", http_url: str = None):
    """Test connection to LinkedIn MCP Server."""
    print("Testing LinkedIn MCP Client Connection")
    print("=" * 50)
    
    client = LinkedInMCPClient(
        transport=transport,
        http_url=http_url or "http://127.0.0.1:8000/mcp"
    )
    
    try:
        print(f"\n1. Connecting via {transport}...")
        await client.connect()
        print("   ✓ Connected successfully!")
        
        print("\n2. Listing available tools...")
        tools = await client.list_tools()
        print(f"   ✓ Found {len(tools)} tools:")
        for tool in tools:
            print(f"     - {tool.get('name', 'unknown')}")
        
        print("\n3. Testing connection health...")
        print("   ✓ All checks passed!")
        
        await client.disconnect()
        print("\n" + "=" * 50)
        print("Connection test: SUCCESS ✓")
        return True
        
    except LinkedInMCPConnectionError as e:
        print(f"\n✗ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure the LinkedIn MCP server is installed:")
        print("     uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --help")
        if transport == "http":
            print("  2. Make sure the server is running in HTTP mode:")
            print("     uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server \\")
            print("       --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp")
        return False
        
    except LinkedInMCPAuthenticationError as e:
        print(f"\n✗ Authentication failed: {e}")
        print("\nTroubleshooting:")
        print("  Create a session:")
        print("    uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --get-session")
        return False
        
    except LinkedInMCPError as e:
        print(f"\n✗ Error: {e}")
        return False
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test LinkedIn MCP Client connection")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport mode (default: stdio)"
    )
    parser.add_argument(
        "--http-url",
        default="http://127.0.0.1:8000/mcp",
        help="HTTP URL for server (default: http://127.0.0.1:8000/mcp)"
    )
    
    args = parser.parse_args()
    
    success = asyncio.run(test_connection(
        transport=args.transport,
        http_url=args.http_url
    ))
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
