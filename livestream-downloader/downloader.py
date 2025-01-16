#!/usr/bin/env python3
import csv
import os
import yt_dlp
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LivestreamDownloader:
    def __init__(self, accounts_file='accounts.csv', output_dir='downloads'):
        self.accounts_file = accounts_file
        self.output_dir = output_dir
        self.ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(output_dir, '%(uploader)s/%(title)s-%(id)s.%(ext)s'),
            'download_archive': 'downloaded.txt',
            'ignoreerrors': True,
        }

    def read_accounts(self):
        """Read YouTube channel URLs from accounts.csv"""
        accounts = []
        try:
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'channel_url' in row:
                        accounts.append(row['channel_url'])
        except FileNotFoundError:
            logger.error(f"Accounts file {self.accounts_file} not found")
            return []
        return accounts

    def get_recent_livestreams(self, channel_url, num_streams=5):
        """Get recent livestreams from a channel"""
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                # Extract channel information and recent videos
                channel_info = ydl.extract_info(
                    channel_url,
                    download=False,
                    process=False
                )
                
                # Get list of videos and filter for livestreams
                if 'entries' in channel_info:
                    streams = []
                    for entry in channel_info['entries']:
                        if entry and ('was_live' in entry and entry['was_live']):
                            streams.append(entry['url'])
                            if len(streams) >= num_streams:
                                break
                    return streams
            except Exception as e:
                logger.error(f"Error getting livestreams from {channel_url}: {str(e)}")
                return []
        return []

    def download_livestream(self, video_url):
        """Download a single livestream"""
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                logger.info(f"Downloading: {video_url}")
                ydl.download([video_url])
                return True
            except Exception as e:
                logger.error(f"Error downloading {video_url}: {str(e)}")
                return False

    def process_channels(self, num_streams_per_channel=5):
        """Process all channels and download their recent livestreams"""
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        accounts = self.read_accounts()
        if not accounts:
            logger.error("No accounts found to process")
            return

        for channel_url in accounts:
            logger.info(f"Processing channel: {channel_url}")
            streams = self.get_recent_livestreams(channel_url, num_streams_per_channel)
            
            for stream_url in streams:
                self.download_livestream(stream_url)

def main():
    downloader = LivestreamDownloader()
    # Number of recent livestreams to download per channel
    num_streams = 5
    downloader.process_channels(num_streams)

if __name__ == "__main__":
    main()
