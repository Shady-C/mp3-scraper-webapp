from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import asyncio
from scraper import scrape_mp3s  # Import the async MP3 scraper

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from the frontend

# Directory where MP3 files are temporarily stored
DOWNLOAD_FOLDER = "downloads"
app.config["DOWNLOAD_FOLDER"] = DOWNLOAD_FOLDER

@app.route("/api/scrape", methods=["POST"])
def scrape():
    """
    Convert the async scraper function to synchronous execution.
    """
    data = request.json  # Parse incoming JSON request
    page_url = data.get("page_url")  # Extract the page URL

    if not page_url:
        return jsonify({"error": "No URL provided"}), 400  # Return error if no URL is given

    print(f"Scraping: {page_url}")  # Debug log

    # Run async scraper function in a synchronous manner
    mp3_links = asyncio.run(scrape_mp3s(page_url))

    if not mp3_links:
        return jsonify({"message": "No MP3 files found"}), 404  # Return 404 if no MP3s are found

    base_url = request.host_url.rstrip("/")
    
    response_data = [
        {"url": f"{base_url}/downloads/{key}" if status == "temporary" else key, "type": status}
        for key, status in mp3_links.items()
    ]

    return jsonify({"mp3_links": response_data}), 200  # Return JSON response with MP3 links


@app.route("/downloads/<filename>")
def serve_mp3(filename):
    """
    Endpoint to serve downloaded MP3 files.
    - Provides temporary access to locally stored MP3 files.
    """
    return send_from_directory(
        app.config["DOWNLOAD_FOLDER"],
        filename,
        as_attachment=True  # Forces browser to download the file
    )

if __name__ == "__main__":
    app.run(debug=True)  # Run Flask in debug mode (for development only)
