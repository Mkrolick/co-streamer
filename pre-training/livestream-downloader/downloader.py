import yt_dlp
import os
from datetime import datetime
import logging
import pandas as pd
import threading
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_requirements():
    """Check and verify required dependencies and directories."""
    # Create downloads directory if it doesn't exist
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        logging.info("Created downloads directory")

    # Check for ffmpeg
    if not shutil.which('ffmpeg'):
        logging.error("ffmpeg is not installed. Please install ffmpeg to continue.")
        raise SystemExit("ffmpeg is required but not found. Please install ffmpeg first.")

def download_livestreams(channel_name: str, max_downloads: int) -> None:
    """
    Download active livestreams from a specified YouTube channel.
    
    Args:
        channel_name (str): The name of the YouTube channel
    """
    try:
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join('downloads', f'{channel_name}_%(title)s_%(id)s.%(ext)s'),
            'concurrent_fragments': 4,  # Number of fragments to download concurrently
            'quiet': True,  # Suppress yt-dlp's output
            'playlistend': max_downloads, # Max number of videos to download from the channel
            'ignoreerrors': True
        }
        
        # Create URL for channel's live streams
        channel_url = f'https://www.youtube.com/@{channel_name}/streams'
        
        logging.info(f"Checking for livestreams on channel: {channel_name}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Extract info and download
                info = ydl.extract_info(channel_url, download=True)
                if info:
                    logging.info(f"Successfully downloaded stream: {info.get('title', 'Unknown Title')}")
                else:
                    logging.info(f"No active livestream found for channel: {channel_name}")
                    
            except yt_dlp.utils.DownloadError as e:
                if "This live event will begin in" in str(e):
                    logging.info(f"Stream is scheduled but hasn't started yet for channel: {channel_name}")
                elif "No active livestream" in str(e):
                    logging.info(f"No active livestream found for channel: {channel_name}")
                else:
                    raise  # Re-raise if it's a different download error
                
    except Exception as e:
        logging.error(f"Error downloading livestream for {channel_name}: {str(e)}")
        raise

if __name__ == "__main__":
    # Check requirements before starting
    check_requirements()
    
    max_downloads = 1200

    # Read channel names from accounts.csv
    file = pd.read_csv("accounts.csv")
    channel_names = file["channel_url"]

    # Create and start threads for each channel
    threads = []
    for name in channel_names:
        thread = threading.Thread(target=download_livestreams, args=(name, max_downloads))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()