import os
import aiohttp
import asyncio
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from playwright.async_api import async_playwright

# Directory to store downloaded MP3 files
DOWNLOAD_FOLDER = "downloads"

# Maximum allowed MP3 file size (in MB) to prevent large downloads
MAX_FILE_SIZE_MB = 100  

# Cache for failed URLs to avoid unnecessary repeated requests
FAILED_URL_CACHE = set()  

# Dictionary to track temporary files and their timestamps for auto-deletion
TEMP_FILES = {}

# User-Agent header to mimic a real browser and avoid being blocked by websites
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"

# Ensure the downloads directory exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

async def fetch_page(url):
    """
    Fetch a webpage using Playwright for JavaScript-rendered content.
    This ensures we can scrape dynamic websites where MP3 links are loaded via JavaScript.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Launch headless browser
        page = await browser.new_page()
        await page.set_extra_http_headers({"User-Agent": USER_AGENT})  # Set custom User-Agent
        await page.goto(url, timeout=15000)  # Load the page (15 seconds timeout)
        html = await page.content()  # Get the full page HTML after JavaScript execution
        await browser.close()
        return html

async def check_mp3_availability(session, url):
    """
    Check if an MP3 file is accessible using a HEAD request.
    If the HEAD request fails, attempt a small GET request (first few KB).
    """
    if url in FAILED_URL_CACHE:
        return False  # Skip checking if URL is already marked as failed

    try:
        # Try a HEAD request first (doesn't download the file, just checks availability)
        async with session.head(url, allow_redirects=True, timeout=5) as response:
            if response.status == 200:
                return True  # ✅ MP3 exists

            # If HEAD fails, try fetching the first 1KB of the file
            headers = {"Range": "bytes=0-1024"}
            async with session.get(url, headers=headers, timeout=5) as get_response:
                if get_response.status in [200, 206]:  # 206 = Partial Content
                    return True  # ✅ MP3 is accessible

    except Exception:
        pass  # Ignore request failures

    FAILED_URL_CACHE.add(url)  # Mark URL as failed to avoid checking again
    return False  # ❌ MP3 not accessible

async def get_mp3_size(session, url):
    """
    Get the size of an MP3 file using the Content-Length header from a HEAD request.
    Returns size in MB, or None if size cannot be determined.
    """
    try:
        async with session.head(url, allow_redirects=True, timeout=5) as response:
            content_length = response.headers.get("Content-Length")
            if content_length:
                return int(content_length) / (1024 * 1024)  # Convert bytes to MB
    except Exception:
        pass
    return None  # File size unknown

async def download_mp3(session, url):
    """
    Download an MP3 file asynchronously and save it in the downloads folder.
    If the file size exceeds the limit, it is skipped.
    Returns the filename if successful, None otherwise.
    """
    file_name = os.path.basename(urlparse(url).path)
    file_path = os.path.join(DOWNLOAD_FOLDER, file_name)

    try:
        # Check file size before downloading
        size_mb = await get_mp3_size(session, url)
        if size_mb and size_mb > MAX_FILE_SIZE_MB:
            return None  # Skip large files

        # Download the file in chunks
        async with session.get(url, timeout=15) as response:
            response.raise_for_status()
            with open(file_path, "wb") as f:
                async for chunk in response.content.iter_chunked(1024):  # Download in 1KB chunks
                    f.write(chunk)

        # Store file with timestamp for auto-delete
        TEMP_FILES[file_name] = asyncio.get_event_loop().time()
        return file_name  # Return saved filename

    except Exception:
        return None  # Download failed

async def extract_mp3s_from_html(session, url):
    """
    Extract MP3 links from a webpage.
    - Finds MP3s inside <source> and <a> tags
    - Detects MP3 URLs inside JSON data embedded in <script> tags
    - Extracts MP3s from iframe sources
    """
    try:
        # Try fetching page normally
        async with session.get(url, headers={"User-Agent": USER_AGENT}, timeout=10) as response:
            response.raise_for_status()
            html = await response.text()
    except Exception:
        # If normal fetch fails, use Playwright to render JavaScript-based content
        html = await fetch_page(url)

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Extract MP3 links from <source> and <a> tags
    mp3_urls = {tag["src"] for tag in soup.select('source[type="audio/mpeg"]') if tag.get("src")}
    mp3_urls.update({tag["href"] for tag in soup.select('a[href$=".mp3"]')})

    # Extract MP3 links from JSON data inside <script> tags
    json_text = " ".join(script.text for script in soup.find_all("script"))
    mp3_urls.update(set(re.findall(r'https?://[^\s"]+\.mp3', json_text)))

    # Extract MP3s from iframes (some sites load players inside iframes)
    iframe_urls = [iframe["src"] for iframe in soup.select("iframe[src]")]
    for iframe_url in iframe_urls:
        iframe_mp3s = await extract_mp3s_from_html(session, iframe_url)
        mp3_urls.update(iframe_mp3s)

    return mp3_urls  # Return all extracted MP3 URLs

async def scrape_mp3s(page_url):
    """
    Scrape a webpage for MP3 files, check their availability, and download if needed.
    Returns a dictionary with direct MP3 links or temporary file paths.
    """
    async with aiohttp.ClientSession() as session:
        # Extract MP3 links
        mp3_links = await extract_mp3s_from_html(session, page_url)

        # Check MP3 availability in parallel
        availability_tasks = {url: check_mp3_availability(session, url) for url in mp3_links}
        availability_results = await asyncio.gather(*availability_tasks.values())

        mp3_results = {}
        for url, is_available in zip(availability_tasks.keys(), availability_results):
            if is_available:
                mp3_results[url] = "direct"  # ✅ Direct download link
            else:
                file_name = await download_mp3(session, url)  # Download if not available
                if file_name:
                    mp3_results[file_name] = "temporary"  # ⏳ Temporary download

        return mp3_results  # Return dictionary of MP3 results

async def auto_delete_temp_files():
    """
    Periodically checks and deletes temporary MP3 files that are older than 5 minutes.
    Runs every 60 seconds in the background.
    """
    while True:
        await asyncio.sleep(60)  # Wait for 60 seconds before checking again
        current_time = asyncio.get_event_loop().time()

        # Iterate through tracked temporary files
        for file_name, timestamp in list(TEMP_FILES.items()):
            if current_time - timestamp > 300:  # 300 seconds = 5 minutes
                file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
                if os.path.exists(file_path):
                    os.remove(file_path)  # Delete expired file
                TEMP_FILES.pop(file_name, None)  # Remove from tracking list

# ✅ Fix: Run auto-delete task only when executed as a script
if __name__ == "__main__":
    asyncio.run(auto_delete_temp_files())  # Runs the background task properly
