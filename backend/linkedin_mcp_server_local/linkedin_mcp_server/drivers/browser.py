"""
Playwright browser management for LinkedIn scraping.

This module provides async browser lifecycle management using linkedin_scraper v3's
BrowserManager. Implements a singleton pattern for browser reuse across tool calls
with session persistence via JSON files.
"""

import logging
from pathlib import Path

from linkedin_scraper import (
    AuthenticationError,
    BrowserManager,
    is_logged_in,
    login_with_cookie,
)
from linkedin_scraper.core import detect_rate_limit

# Resources to block to save memory
BLOCKED_RESOURCES = [
    "image",
    "media",
    "font",
    "stylesheet",
    "other",
    "ping",
]

async def _block_heavy_resources(route):
    """Block images and other heavy resources."""
    if route.request.resource_type in BLOCKED_RESOURCES:
        await route.abort()
    else:
        await route.continue_()

from linkedin_mcp_server.config import get_config
from linkedin_mcp_server.utils import get_linkedin_cookie

logger = logging.getLogger(__name__)


# Default session file location
DEFAULT_SESSION_PATH = Path.home() / ".linkedin-mcp" / "session.json"

# Global browser instance (singleton)
_browser: BrowserManager | None = None
_headless: bool = True


def _apply_browser_settings(browser: BrowserManager) -> None:
    """Apply configuration settings to browser instance."""
    config = get_config()
    browser.page.set_default_timeout(config.browser.default_timeout)


async def get_or_create_browser(
    headless: bool | None = None,
    session_path: Path | None = None,
) -> BrowserManager:
    """
    Get existing browser or create and initialize a new one.

    Uses a singleton pattern to reuse the browser across tool calls.
    Loads session from file if available.

    Args:
        headless: Run browser in headless mode. Defaults to config value.
        session_path: Path to session file. Defaults to ~/.linkedin-mcp/session.json

    Returns:
        Initialized BrowserManager instance
    """
    global _browser, _headless

    if headless is not None:
        _headless = headless

    if session_path is None:
        session_path = DEFAULT_SESSION_PATH

    if _browser is not None:
        return _browser

    config = get_config()
    viewport = {
        "width": config.browser.viewport_width,
        "height": config.browser.viewport_height,
    }

    # Build launch options for custom browser path
    launch_options: dict[str, any] = {}
    if config.browser.chrome_path:
        launch_options["executable_path"] = config.browser.chrome_path
        logger.info("Using custom Chrome path: %s", config.browser.chrome_path)

    # Docker compatibility args
    launch_options["args"] = [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-accelerated-2d-canvas",
        "--disable-gpu",
        "--single-process", # Run in single process inside Docker to save memory
        "--no-zygote",
        "--renderer-process-limit=1",
    ]

    # Stealth args to avoid detection/slow loading
    launch_options["args"].extend([
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--disable-logging",
        "--disable-notifications",
        "--window-size=1280,720",
    ])

    logger.info(
        "Creating new browser (headless=%s, slow_mo=%sms, viewport=%sx%s)",
        _headless,
        config.browser.slow_mo,
        viewport["width"],
        viewport["height"],
    )
    _browser = BrowserManager(
        headless=_headless,
        slow_mo=config.browser.slow_mo,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport=viewport,
        **launch_options,
    )
    await _browser.start()

    # Priority 1: Load session file if available
    if session_path.exists():
        try:
            await _browser.load_session(str(session_path))
            logger.info(f"Loaded session from {session_path}")
            
            # Optimization: Block heavy resources
            await _browser.page.route("**/*", _block_heavy_resources)
            
            # Increase timeout for slow cloud environment (120s)
            _browser.page.set_default_timeout(120000)

            # Navigate to LinkedIn to validate session (wait until domcontentloaded is enough)
            await _browser.page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
            if await is_logged_in(_browser.page):
                _apply_browser_settings(_browser)
                return _browser
            logger.warning(
                "Session loaded but expired, trying to create session from cookie"
            )
        except Exception as e:
            logger.warning(f"Failed to load session: {e}")

    # Priority 2: Use cookie from environment
    if cookie := get_linkedin_cookie():
        try:
            # Optimization: Block heavy resources BEFORE login
            await _browser.page.route("**/*", _block_heavy_resources)
            
             # Increase timeout for slow cloud environment (120s)
            _browser.page.set_default_timeout(120000)

            await login_with_cookie(_browser.page, cookie)
            logger.info("Authenticated using LINKEDIN_COOKIE")
            _apply_browser_settings(_browser)
            return _browser
        except Exception as e:
            logger.warning(f"Cookie authentication failed: {e}")

    # No auth available - fail fast with clear error
    raise AuthenticationError(
        "No authentication found. Run with --get-session to create a session."
    )


async def close_browser() -> None:
    """Close the browser and cleanup resources."""
    global _browser

    if _browser is not None:
        logger.info("Closing browser...")
        await _browser.close()
        _browser = None
        logger.info("Browser closed")


def session_exists(session_path: Path | None = None) -> bool:
    """Check if a session file exists."""
    if session_path is None:
        session_path = DEFAULT_SESSION_PATH
    return session_path.exists()


def set_headless(headless: bool) -> None:
    """Set headless mode for future browser creation."""
    global _headless
    _headless = headless


async def validate_session() -> bool:
    """
    Check if the current session is still valid (logged in).

    Returns:
        True if session is valid and user is logged in
    """
    browser = await get_or_create_browser()
    return await is_logged_in(browser.page)


async def ensure_authenticated() -> None:
    """
    Validate session and raise if expired.

    Raises:
        AuthenticationError: If session is expired or invalid
    """
    if not await validate_session():
        raise AuthenticationError("Session expired or invalid.")


async def check_rate_limit() -> None:
    """
    Proactively check for rate limiting.

    Should be called after navigation to detect if LinkedIn is blocking requests.

    Raises:
        RateLimitError: If rate limiting is detected
    """
    browser = await get_or_create_browser()
    await detect_rate_limit(browser.page)


def reset_browser_for_testing() -> None:
    """Reset global browser state for test isolation."""
    global _browser, _headless
    _browser = None
    _headless = True
