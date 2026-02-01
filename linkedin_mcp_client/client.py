"""LinkedIn MCP Client implementation."""

import json
import subprocess
import sys
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import httpx
import asyncio
from contextlib import asynccontextmanager

from .exceptions import (
    LinkedInMCPError,
    LinkedInMCPConnectionError,
    LinkedInMCPToolError,
    LinkedInMCPAuthenticationError,
)


class LinkedInMCPClient:
    """Client for interacting with the LinkedIn MCP Server."""

    def __init__(
        self,
        transport: str = "stdio",
        command: Optional[List[str]] = None,
        http_url: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize the LinkedIn MCP Client.

        Args:
            transport: Transport mode - "stdio" or "http"
            command: Command to run the server (for stdio mode)
            http_url: HTTP URL for the server (for http mode)
            timeout: Request timeout in seconds
        """
        self.transport = transport
        self.command = command or [
            "uvx",
            "--from",
            "git+https://github.com/stickerdaniel/linkedin-mcp-server",
            "linkedin-mcp-server",
        ]
        self.http_url = http_url or "http://127.0.0.1:8000/mcp"
        self.timeout = timeout
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self._lock = asyncio.Lock()

    def _get_next_id(self) -> int:
        """Get next request ID."""
        self.request_id += 1
        return self.request_id

    async def _read_next_json_message(self) -> Dict[str, Any]:
        """Read the next valid JSON message from stdout, ignoring non-JSON lines."""
        while True:
            line = await asyncio.to_thread(self.process.stdout.readline)
            if not line:
                raise LinkedInMCPConnectionError("Server closed connection")
            
            decoded_line = line.decode().strip()
            if not decoded_line:
                continue

            try:
                return json.loads(decoded_line)
            except json.JSONDecodeError:
                # Log non-JSON output for debugging but don't crash
                print(f"[MCP Client] Ignored server output: {decoded_line}", file=sys.stderr)
                continue

    async def _send_request_stdio(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request via stdio transport."""
        if self.process is None:
            raise LinkedInMCPConnectionError("Server process not started. Call connect() first.")

        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method,
            "params": params or {},
        }

        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str.encode())
        self.process.stdin.flush()

        # Read response
        response = await self._read_next_json_message()
        
        if "error" in response:
            error = response["error"]
            error_msg = error.get("message", "Unknown error")
            error_code = error.get("code", -1)
            
            if error_code == -32000:  # Authentication error
                raise LinkedInMCPAuthenticationError(error_msg)
            raise LinkedInMCPToolError(f"Server error: {error_msg}")

        return response.get("result", {})

    async def _send_request_http(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request via HTTP transport."""
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method,
            "params": params or {},
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    self.http_url,
                    json=request,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                result = response.json()
                
                if "error" in result:
                    error = result["error"]
                    error_msg = error.get("message", "Unknown error")
                    error_code = error.get("code", -1)
                    
                    if error_code == -32000:  # Authentication error
                        raise LinkedInMCPAuthenticationError(error_msg)
                    raise LinkedInMCPToolError(f"Server error: {error_msg}")

                return result.get("result", {})
            except httpx.RequestError as e:
                raise LinkedInMCPConnectionError(f"HTTP request failed: {e}")

    async def _send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request using the configured transport."""
        if self.transport == "stdio":
            return await self._send_request_stdio(method, params)
        elif self.transport == "http":
            return await self._send_request_http(method, params)
        else:
            raise LinkedInMCPError(f"Unknown transport: {self.transport}")

    async def connect(self):
        """Connect to the MCP server."""
        if self.transport == "stdio":
            if self.process is None:
                try:
                    self.process = subprocess.Popen(
                        self.command,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        bufsize=0,
                    )
                    # Initialize MCP protocol
                    await self._initialize()
                except Exception as e:
                    raise LinkedInMCPConnectionError(f"Failed to start server: {e}")
        elif self.transport == "http":
            # Test connection
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    await client.get(self.http_url.replace("/mcp", "/health"), timeout=5)
            except:
                pass  # Health endpoint might not exist, that's okay

    async def _initialize(self):
        """Initialize MCP protocol handshake."""
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "linkedin-mcp-client",
                    "version": "0.1.0",
                },
            },
        }
        
        init_str = json.dumps(init_request) + "\n"
        self.process.stdin.write(init_str.encode())
        self.process.stdin.flush()
        
        # Read initialize response
        response = await self._read_next_json_message()
        if "error" in response:
             raise LinkedInMCPConnectionError(f"Initialize failed: {response['error']}")
        
        # Send initialized notification
        initialized = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        initialized_str = json.dumps(initialized) + "\n"
        self.process.stdin.write(initialized_str.encode())
        self.process.stdin.flush()

    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the server."""
        result = await self._send_request("tools/list", {})
        return result.get("tools", [])

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.

        Args:
            name: Name of the tool to call
            arguments: Arguments for the tool

        Returns:
            Tool result
        """
        result = await self._send_request(
            "tools/call",
            {
                "name": name,
                "arguments": arguments,
            },
        )
        return result

    # Convenience methods for each tool

    async def get_person_profile(self, url: str) -> Dict[str, Any]:
        """
        Get detailed profile information for a LinkedIn person.

        Args:
            url: LinkedIn profile URL (e.g., https://www.linkedin.com/in/username/)

        Returns:
            Profile information including work history, education, contacts, interests
        """
        return await self.call_tool("get_person_profile", {"url": url})

    async def get_company_profile(self, url: str) -> Dict[str, Any]:
        """
        Get company information from LinkedIn.

        Args:
            url: LinkedIn company URL (e.g., https://www.linkedin.com/company/companyname/)

        Returns:
            Company information including employees, affiliated companies
        """
        return await self.call_tool("get_company_profile", {"url": url})

    async def get_company_posts(self, url: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Get recent posts from a company's LinkedIn feed.

        Args:
            url: LinkedIn company URL
            limit: Maximum number of posts to retrieve (optional)

        Returns:
            Recent company posts
        """
        args = {"url": url}
        if limit is not None:
            args["limit"] = limit
        return await self.call_tool("get_company_posts", args)

    async def search_jobs(
        self,
        keywords: Optional[str] = None,
        location: Optional[str] = None,
        limit: Optional[int] = None,
        time_posted: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search for jobs on LinkedIn.

        Args:
            keywords: Search keywords
            location: Location filter
            limit: Maximum number of results
            time_posted: Time filter (e.g., "24h", "1h", "7d", "30d" for 24 hours, 1 hour, 7 days, 30 days)

        Returns:
            Job search results
        """
        args = {}
        if keywords:
            args["keywords"] = keywords
        if location:
            args["location"] = location
        if limit:
            args["limit"] = limit
        if time_posted:
            args["time_posted"] = time_posted
        return await self.call_tool("search_jobs", args)

    async def get_job_details(self, url: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific job posting.

        Args:
            url: LinkedIn job URL (e.g., https://www.linkedin.com/jobs/view/123456)

        Returns:
            Detailed job information
        """
        return await self.call_tool("get_job_details", {"url": url})

    async def close_session(self) -> Dict[str, Any]:
        """
        Close browser session and clean up resources.

        Returns:
            Confirmation of session closure
        """
        return await self.call_tool("close_session", {})

    @asynccontextmanager
    async def session(self):
        """Context manager for automatic connection/disconnection."""
        await self.connect()
        try:
            yield self
        finally:
            await self.disconnect()
