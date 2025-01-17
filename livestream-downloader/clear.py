import os
import shutil

def clear_downloads():
    downloads_dir = "downloads"
    
    # Check if downloads directory exists
    if not os.path.exists(downloads_dir):
        print("Downloads directory does not exist.")
        return
    
    try:
        # Remove all files and subdirectories in the downloads directory
        for item in os.listdir(downloads_dir):
            item_path = os.path.join(downloads_dir, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        print("Successfully cleared downloads directory.")
    except Exception as e:
        print(f"Error clearing downloads directory: {e}")

if __name__ == "__main__":
    clear_downloads()
