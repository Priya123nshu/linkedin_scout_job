"""
LinkedIn job scraping tools with search and detail extraction.

Provides MCP tools for job posting details and job searches
with comprehensive filtering and structured data extraction.
"""

import logging
from typing import Any, Dict, Optional

from fastmcp import Context, FastMCP
from linkedin_scraper import JobScraper, JobSearchScraper
from mcp.types import ToolAnnotations

from linkedin_mcp_server.callbacks import MCPContextProgressCallback
from linkedin_mcp_server.drivers.browser import (
    ensure_authenticated,
    get_or_create_browser,
)
from linkedin_mcp_server.error_handler import handle_tool_error

logger = logging.getLogger(__name__)

# --- Custom Scraper Logic ---
class CustomJobScraper(JobScraper):
    """
    Subclass of JobScraper to provide robust title extraction.
    """
    async def _get_job_title(self) -> Optional[str]:
        """Extract job title from h1 heading with fallbacks."""
        try:
            # Try multiple selectors commonly used by LinkedIn
            selectors = [
                'h1.top-card-layout__title',
                '.job-details-jobs-unified-top-card__job-title h1',
                'h1.t-24',
                'h1'
            ]
            
            for selector in selectors:
                if await self.page.locator(selector).count() > 0:
                    title = await self.page.locator(selector).first.inner_text()
                    if title and len(title.strip()) > 0:
                         return title.strip()
            
            # Fallback: Try page title
            page_title = await self.page.title()
            if page_title:
                return page_title.split("|")[0].strip()
                
            return None
        except Exception as e:
            logger.error(f"Error extracting job title: {e}")
            return None

class CustomJobSearchScraper(JobSearchScraper):
    """
    Subclass with debugging for 0 results.
    """
    async def search(self, keywords: str, location: str | None = None, limit: int = 25, offset: int = 0) -> list[str]:
        results = await super().search(keywords, location, limit, offset)
        if not results:
             title = await self.page.title()
             content = await self.page.content()
             logger.error(f"DEBUG: Found 0 results. Page Title: {title}")
             if "authwall" in content.lower() or "sign in" in title.lower():
                 logger.error("DEBUG: Hit Authwall/Login page.")
             elif "security check" in title.lower():
                 logger.error("DEBUG: Hit Security Check (Captcha).")
        return results

def register_job_tools(mcp: FastMCP) -> None:
    """
    Register all job-related tools with the MCP server.

    Args:
        mcp: The MCP server instance
    """

    @mcp.tool(
        annotations=ToolAnnotations(
            title="Get Job Details",
            readOnlyHint=True,
            destructiveHint=False,
            openWorldHint=True,
        )
    )
    async def get_job_details(job_id: str, ctx: Context) -> Dict[str, Any]:
        """
        Get job details for a specific job posting on LinkedIn.

        Args:
            job_id: LinkedIn job ID (e.g., "4252026496", "3856789012")
            ctx: FastMCP context for progress reporting

        Returns:
            Structured job data including title, company, location,
            posting date, and job description.
        """
        try:
            # Validate session before scraping
            await ensure_authenticated()

            # Construct LinkedIn URL from job ID
            job_url = f"https://www.linkedin.com/jobs/view/{job_id}/"

            logger.info(f"Scraping job: {job_url}")

            browser = await get_or_create_browser()
            # Use CustomJobScraper instead of JobScraper
            scraper = CustomJobScraper(browser.page, callback=MCPContextProgressCallback(ctx))
            job = await scraper.scrape(job_url)
            
            data = job.to_dict()
            
            # Normalize keys for frontend: ensure 'title' exists
            if "title" not in data and "job_title" in data:
                data["title"] = data["job_title"]
                
            return data

        except Exception as e:
            return handle_tool_error(e, "get_job_details")

    @mcp.tool(
        annotations=ToolAnnotations(
            title="Search Jobs",
            readOnlyHint=True,
            destructiveHint=False,
            openWorldHint=True,
        )
    )
    async def search_jobs(
        keywords: str,
        ctx: Context,
        location: str | None = None,
        limit: int = 25,
    ) -> Dict[str, Any]:
        """
        Search for jobs on LinkedIn.

        Args:
            keywords: Search keywords (e.g., "software engineer", "data scientist")
            ctx: FastMCP context for progress reporting
            location: Optional location filter (e.g., "San Francisco", "Remote")
            limit: Maximum number of job URLs to return (default: 25)

        Returns:
            Dict with job_urls list and count. Use get_job_details to get
            full details for specific jobs.
        """
        try:
            # Validate session before scraping
            await ensure_authenticated()

            logger.info(f"Searching jobs: keywords='{keywords}', location='{location}'")

            browser = await get_or_create_browser()
            # Use CustomJobSearchScraper for debugging
            scraper = CustomJobSearchScraper(
                browser.page, callback=MCPContextProgressCallback(ctx)
            )
            job_urls = await scraper.search(
                keywords=keywords,
                location=location,
                limit=limit,
            )

            return {"job_urls": job_urls, "count": len(job_urls)}

        except Exception as e:
            return handle_tool_error(e, "search_jobs")
