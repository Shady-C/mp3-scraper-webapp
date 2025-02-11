from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS 
from scraper import scrape_and_download_mp3s  # Import scraper logic

app = Flask(__name__)
CORS(app)

# Define the directory where MP3s are saved
DOWNLOAD_FOLDER = "downloads"
app.config["DOWNLOAD_FOLDER"]= DOWNLOAD_FOLDER


@app.route("/api/scrape", methods=["POST"])
def scrape():
    data = request.json
    page_url = data.get("page_url")
    
    if not page_url:
        return jsonify({"error": "No URL provided"}), 400

    # Scrape MP3 links
    print(f"Scraping: {page_url}")
    mp3_files = scrape_and_download_mp3s(page_url) # Returns filenames, not URLs


    if not mp3_files:
        return jsonify({"message": "No MP3 files found"}), 404
    
    # Construct correct URLs pointing to the backend
    mp3_urls = [f"http://localhost:5000/downloads/{file}" for file in mp3_files]

    return jsonify({"mp3_links": mp3_urls}), 200

@app.route("/downloads/<filename>")
def serve_mp3(filename):
    return send_from_directory(
        app.config["DOWNLOAD_FOLDER"],
        filename,
        as_attachment=True  # Forces browser to download the file
    )

if __name__ == "__main__":
    app.run(debug=True)
