"""Custom exceptions for the LinkedIn MCP Client."""


class LinkedInMCPError(Exception):
    """Base exception for LinkedIn MCP Client errors."""
    pass


class LinkedInMCPConnectionError(LinkedInMCPError):
    """Raised when connection to MCP server fails."""
    pass


class LinkedInMCPToolError(LinkedInMCPError):
    """Raised when a tool call fails."""
    pass


class LinkedInMCPAuthenticationError(LinkedInMCPError):
    """Raised when authentication fails."""
    pass
