"use client"; // Required for client-side components in App Router

import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [pageUrl, setPageUrl] = useState("");
  const [mp3Links, setMp3Links] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleScrape = async () => {
    setLoading(true);
    setError("");
    setMp3Links([]);

    try {
      const response = await axios.post("http://localhost:5000/api/scrape", {
        page_url: pageUrl,
      });

      if (response.data.mp3_links) {
        setMp3Links(response.data.mp3_links);
      } else {
        setError("No MP3 files found.");
      }
    } catch (err) {
      setError("Error fetching MP3 links.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>MP3 Scraper</h1>
      <input
        type="text"
        placeholder="Enter webpage URL"
        value={pageUrl}
        onChange={(e) => setPageUrl(e.target.value)}
      />
      <button onClick={handleScrape} disabled={loading}>
        {loading ? "Scraping..." : "Scrape MP3s"}
      </button>

      {error && <p className="error">{error}</p>}
      <ul>
        {mp3Links.map((link, index) => {
          const filename = link.split("/").pop();
          
          return (
            <li key={index}>
              <a href={link} target="_blank" rel="noopener noreferrer">
                {filename}
              </a>
          </li>

        )
          
        })}
      </ul>
    </div>
  );
}
