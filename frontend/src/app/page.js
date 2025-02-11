"use client"; // Required for client-side rendering in Next.js

import { useState } from "react";
import axios from "axios";

// Main component for the MP3 Scraper
export default function Home() {
  // State variables
  const [pageUrl, setPageUrl] = useState(""); // Stores the inputted webpage URL
  const [mp3Links, setMp3Links] = useState([]); // Stores the fetched MP3 links
  const [loading, setLoading] = useState(false); // Indicates if a request is in progress
  const [error, setError] = useState(""); // Stores error messages

  // Function to handle scraping when the user submits a URL
  const handleScrape = async () => {
    setLoading(true); // Show loading state
    setError(""); // Clear any previous errors
    setMp3Links([]); // Clear previous results

    try {
      // Make a POST request to the Flask backend
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/scrape`, // Use environment variable for backend URL
        {
          page_url: pageUrl, // Send the inputted page URL in the request body
        }
      );

      // Check if MP3 links were found
      if (response.data.mp3_links) {
        setMp3Links(response.data.mp3_links); // Update state with fetched MP3 links
      } else {
        setError("No MP3 files found."); // Display an error message if no MP3s were found
      }
    } catch (err) {
      setError("Error fetching MP3 links."); // Handle API errors
    } finally {
      setLoading(false); // Remove loading state once request is completed
    }
  };

  return (
    <main className="container mx-auto p-6">
      {/* Page Title */}
      <h1 className="text-2xl font-bold mb-4">MP3 Scraper</h1>

      {/* Input Field & Button */}
      <div className="flex gap-4 mb-4">
        <input
          type="text"
          placeholder="Enter webpage URL"
          value={pageUrl}
          onChange={(e) => setPageUrl(e.target.value)} // Update URL state on change
          className="border p-2 w-full"
        />
        <button
          onClick={handleScrape} // Trigger scrape function
          disabled={loading} // Disable button while loading
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {loading ? "Scraping..." : "Scrape MP3s"} {/* Change button text while loading */}
        </button>
      </div>

      {/* Error Message */}
      {error && <p className="text-red-500">{error}</p>}

      {/* MP3 Links List */}
      <ul className="mt-4 space-y-2">
        {mp3Links.map((mp3, index) => (
          <li key={index} className="border p-2 rounded">
            <a
              href={mp3.url} // Direct link to MP3 file
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 underline"
            >
              {mp3.url.split("/").pop()} {/* Extract filename from URL */}
              {mp3.type === "temporary" && " (Temporary)"} {/* Indicate temporary files */}
            </a>
          </li>
        ))}
      </ul>
    </main>
  );
}
