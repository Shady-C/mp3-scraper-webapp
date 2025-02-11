# MP3 Scraper WebApp

## Overview
The **MP3 Scraper WebApp** is a web-based tool that allows users to download multiple MP3 files from websites that do not provide a bulk download option. The application automates the process of identifying and downloading MP3 files, making it easier for users to collect and manage their audio content.

## Features
- **Web-based interface**: Uses an HTML template for user-friendly interaction.
- **Flask-powered backend**: Handles web scraping, downloads, and user interactions.
- **Web scraper integration**: Extracts MP3 links from provided web pages.
- **Automated downloads**: Saves MP3 files in a designated local folder.
- **Batch processing**: Iteratively downloads all detected files.
- **No pre-selection**: The app downloads all found MP3s without asking for user selection.

## Version 1: Initial Features
### How It Works
1. **Frontend**: A simple HTML interface allows users to input a URL for scraping (CLI module to be added if demand is high).
2. **Backend**:
   - Uses **Flask** to manage requests, making the web scraper accessible and easy to use.
   - Flask is chosen for its lightweight nature, easy API integration, and scalability.
   - Extracts MP3 links from the specified URL and queues them for download.
   - Automatically stores downloaded files in a local folder.
3. **Download Process**:
   - Scrapes the provided webpage for MP3 files.
   - Adds all found MP3 links to a queue.
   - Downloads each file sequentially without user confirmation.
   - Saves the files in a predefined directory.

### Development Notes
- No CI/CD pipeline is implemented yet.
- Basic logging and error handling.

---

## Version 2: Upcoming Updates
### Enhancements & New Features
- **Selectable Downloads**: After scraping, users can view a list of MP3 files and choose which ones to download.
- **Rename Option**: Allows users to rename files before downloading, with the existing name as the default.
- **Download Dialog**: Instead of auto-downloading, prompt users with a download confirmation.
- **Bulk Download as ZIP**: If many MP3s are found, bundle them into a ZIP file for easier downloads.

---

## Version 3: Future Plans
- **Storage System**:
  - Store MP3 file links for future access rather than downloading immediately.
  - Implement a feature called **Crates**, allowing users to group MP3 links.
  - Users can download an entire crate or delete it when done.
- **Frontend Enhancement**:
  - Consider building a more dynamic frontend (possible frameworks: **Next.js, Vue.js, or React**).
  - Lightweight and minimal for initial implementation.

---

## Version 4: Advanced Features
- **Messaging Platform Integration**:
  - Enable integration with WhatsApp, Telegram, etc.
  - Users send a link to a bot and receive the MP3 file back.
- **Enhanced UI/UX**:
  - Improve the user interface with animations, interactive elements, and better navigation.
  - Brainstorm additional UI features for better usability and aesthetics.

---

## Contributing
- Open to feedback and suggestions.
- Looking for contributors to enhance functionality and UI.
- CI/CD integration and code refactoring planned for future updates.

Stay tuned for further updates and improvements!