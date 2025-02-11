# app.py

from flask import Flask, request, render_template, send_from_directory
import os

# Import your scraping logic
from scraper import scrape_and_download_mp3s, DOWNLOAD_FOLDER

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # The user submitted the form
        page_url = request.form.get("page_url", "").strip()
        if not page_url:
            # If no URL provided, just render results with no data
            return render_template("results.html", downloaded=None)
        
        # Scrape and download
        downloaded_files = scrape_and_download_mp3s(page_url, DOWNLOAD_FOLDER)
        return render_template("results.html", downloaded=downloaded_files)
    
    # GET request: Show the form
    return render_template("index.html")

@app.route("/downloads/<path:filename>")
def downloaded_file(filename):
    """
    Serve the requested file from the downloads folder,
    forcing the browser to download it (as_attachment=True).
    """
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)