"""LinkedIn MCP Client - A client library for interacting with the LinkedIn MCP Server."""

from .client import LinkedInMCPClient
from .exceptions import LinkedInMCPError, LinkedInMCPConnectionError

__version__ = "0.1.0"
__all__ = ["LinkedInMCPClient", "LinkedInMCPError", "LinkedInMCPConnectionError"]
