import os
import re
import time
import logging
from typing import List
import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_429_TOO_MANY_REQUESTS
from prometheus_client import Counter, Histogram
import functools

# Load environment variables from .env if present (for local dev)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- CONFIGURATION ---
API_KEY = os.getenv("MCP_API_KEY", "change-me-please")
RATE_LIMIT = int(os.getenv("MCP_RATE_LIMIT", "60"))
# requests per minute per IP
ALLOWED_DOMAINS = [
    "docs.python.org", "realpython.com", "stackoverflow.com", "w3schools.com",
    "geeksforgeeks.org", "tutorialspoint.com", "pythonbasics.org", "pypi.org",
    "github.com", "medium.com", "dev.to", "towardsdatascience.com"
]
MAX_URLS = 10
SEARCH_ENGINE = "https://duckduckgo.com/html/?q="
USER_AGENT = (
    "Mozilla/5.0 (compatible; MCPBot/1.0; +https://modelcontextprotocol.io)"
)

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("url_injector_mcp")


# --- RATE LIMITING ---
class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, max_requests=RATE_LIMIT, window_seconds=60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        # Clean up old entries
        self.request_counts = {
            ip: (count, ts)
            for ip, (count, ts) in self.request_counts.items()
            if now - ts < self.window_seconds
        }
        count, ts = self.request_counts.get(client_ip, (0, now))
        if now - ts >= self.window_seconds:
            count = 0
            ts = now
        count += 1
        self.request_counts[client_ip] = (count, ts)
        if count > self.max_requests:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                {"detail": "Rate limit exceeded"},
                status_code=HTTP_429_TOO_MANY_REQUESTS
            )
        return await call_next(request)


# --- AUTHENTICATION ---
class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/health"):
            return await call_next(request)
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer ") or auth.replace("Bearer ", "") != API_KEY:
            logger.warning("Unauthorized access attempt.")
            return JSONResponse(
                {"detail": "Unauthorized"},
                status_code=HTTP_401_UNAUTHORIZED
            )
        return await call_next(request)


# --- MCP SERVER ---
mcp = FastMCP("url-injector")


# --- KEYWORD EXTRACTION ---
def extract_keywords(text: str) -> List[str]:
    # Simple: split, remove stopwords, deduplicate, filter short
    stopwords = set([
        "the", "is", "in", "at", "of", "a", "an", "and", "or", "to", "for", "with",
        "on", "by", "as", "from", "using", "how", "do", "i", "you", "it", "this",
        "that", "what", "when", "where", "which", "be", "are", "was", "were",
        "can", "should", "could", "would", "will", "may", "might"
    ])
    words = re.findall(r"\b\w+\b", text.lower())
    keywords = [
        w for w in words if w not in stopwords and len(w) > 2
    ]
    # deduplicate, preserve order   
    return list(dict.fromkeys(keywords))


# --- SIMPLE ASYNC CACHE FOR WEB SEARCH ---
SEARCH_CACHE = {}
CACHE_TTL = 600  # 10 minutes


async def search_web(query: str) -> List[str]:
    now = time.time()
    # Clean up expired cache entries
    expired = [k for k, (t, _) in SEARCH_CACHE.items() if now - t > CACHE_TTL]
    for k in expired:
        del SEARCH_CACHE[k]
    # Check cache
    if query in SEARCH_CACHE and now - SEARCH_CACHE[query][0] <= CACHE_TTL:
        logger.info(f"Cache hit for query: {query}")
        return SEARCH_CACHE[query][1]
    urls = []
    try:
        async with httpx.AsyncClient(
            timeout=10, headers={"User-Agent": USER_AGENT}
        ) as client:
            resp = await client.get(
                SEARCH_ENGINE + httpx.utils.quote(query)
            )
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http"):
                    urls.append(href)
    except Exception as e:
        logger.error(f"Web search failed for '{query}': {e}")
    # Store in cache
    SEARCH_CACHE[query] = (now, urls)
    return urls


# --- URL FILTERING ---
def filter_urls(urls: List[str]) -> List[str]:
    filtered = []
    for url in urls:
        for domain in ALLOWED_DOMAINS:
            if domain in url:
                filtered.append(url)
                break
        if len(filtered) >= MAX_URLS:
            break
    return list(dict.fromkeys(filtered))  # deduplicate


# --- PROMETHEUS METRICS ---
REQUEST_COUNT = Counter(
    'mcp_requests_total', 'Total MCP requests', ['endpoint']
)
REQUEST_LATENCY = Histogram(
    'mcp_request_latency_seconds', 'Request latency', ['endpoint']
)

def track_metrics(endpoint):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            with REQUEST_LATENCY.labels(endpoint=endpoint).time():
                REQUEST_COUNT.labels(endpoint=endpoint).inc()
                return await func(*args, **kwargs)
        return wrapper
    return decorator


# --- MCP TOOL ---


@mcp.tool()
@track_metrics("inject_urls_into_prompt")
async def inject_urls_into_prompt(user_prompt: str) -> str:
    """Injects relevant URLs into the user's prompt based on its content.

    Args:
        user_prompt: The original prompt provided by the user.
    """
    logger.info(f"inject_urls_into_prompt called with prompt: {user_prompt}")
    # 1. Extract keywords
    keywords = extract_keywords(user_prompt)
    logger.info(f"Extracted keywords: {keywords}")
    # 2. For each keyword, search web
    all_urls = []
    for kw in keywords:
        urls = await search_web(kw)
        all_urls.extend(urls)
        if len(all_urls) >= MAX_URLS * 2:
            break
    # 3. Filter and select top N URLs
    filtered = filter_urls(all_urls)
    # 4. Format URLs and append to prompt
    if filtered:
        url_section = (
            "\n\nHere are some relevant resources:\n" +
            "\n".join(f"- {u}" for u in filtered)
        )
    else:
        url_section = "\n\n(No relevant resources found.)"
    augmented = user_prompt.strip() + url_section
    logger.info(
        f"Returning augmented prompt with {len(filtered)} URLs."
    )
    return augmented


# --- HEALTH CHECK ---
@mcp.custom_route("/health", methods=["GET"])
@track_metrics("health")
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


# --- SERVER ENTRY POINT ---
def build_app():
    # Compose Starlette app with middleware
    app = mcp.app
    app.add_middleware(AuthMiddleware)
    app.add_middleware(RateLimitMiddleware)
    return app


if __name__ == "__main__":
    logger.info("Starting url-injector-mcp server...")
    port = int(os.environ.get("PORT", 8000))
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=port
    )
# Note: To change the port in MCP 1.x, set the PORT environment variable before running this script.
# Example (PowerShell): $env:PORT=8001; python url_injector_mcp.py