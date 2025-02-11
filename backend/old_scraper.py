# scraper.py

import os
import requests
from bs4 import BeautifulSoup

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def check_mp3_availability(url):
    """
    Check if an MP3 file is accessible via HEAD or small GET request.
    Returns True if accessible, False otherwise.
    """
    try:
        # First attempt: HEAD request
        response = requests.head(url, allow_redirects=True, timeout=5)
        
        if response.status_code == 200:
            return True  # ✅ File exists

        # Some servers block HEAD requests, try small GET request
        headers = {"Range": "bytes=0-1024"}  # Request first KB only
        response = requests.get(url, headers=headers, stream=True, timeout=5)

        if response.status_code == 206 or response.status_code == 200:
            return True  # ✅ File exists

    except requests.RequestException:
        pass  # Ignore errors, fallback needed

    return False  # ❌ Not accessible

def scrape_and_download_mp3s(page_url, download_folder=DOWNLOAD_FOLDER):
    """
    Fetch page_url, parse out .mp3 links, and download them
    into download_folder. Returns a list of downloaded filenames.
    """
    downloaded_files = []
    try:
        response = requests.get(page_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {page_url}: {e}")
        return downloaded_files  # Return empty list if error
    
    soup = BeautifulSoup(response.text, "html.parser")

    # Collect MP3 URLs from <source type="audio/mpeg">
    audio_urls = []
    for source in soup.find_all('source', {'type': 'audio/mpeg'}):
        src = source.get('src')
        if src:
            src = src.split('?')[0]  # remove query param if present
        if src and src.lower().endswith('.mp3'):
            audio_urls.append(src)

    # Also check <a> tags ending in .mp3
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.lower().endswith('.mp3'):
            audio_urls.append(href)

    # Remove duplicates
    audio_urls = list(set(audio_urls))

    # Download each MP3 link
    for url in audio_urls:
        base_name = os.path.basename(url.split('?')[0])  # e.g., "01.mp3"
        file_path = os.path.join(download_folder, base_name)

        try:
            r = requests.get(url)
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                f.write(r.content)
            downloaded_files.append(base_name)
        except requests.exceptions.RequestException as e:
            print(f"  Failed to download {url}: {e}")

    return downloaded_files