import json
import os
import requests
from datetime import datetime

# Configuration
CHANNELS_LIST_FILE = "channels.json"
BASE_URL = "https://telegram-feed-reader.milaadfarzian.workers.dev/telegram/channel?channel="
OUTPUT_DIR = "channel_data"

def ensure_directory():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def load_channels():
    """Load the list of channels from the local JSON file"""
    try:
        if not os.path.exists(CHANNELS_LIST_FILE):
            print(f"❌ Error: {CHANNELS_LIST_FILE} not found!")
            return []
        with open(CHANNELS_LIST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error reading channels file: {e}")
        return []

def fetch_channel_data(channel):
    try:
        url = f"{BASE_URL}{channel}"
        response = requests.get(url, timeout=25)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"   - Error fetching {channel}: {e}")
        return None

def save_channel_json(channel, data):
    # This overwrites the existing file, keeping only the latest version
    filename = f"{OUTPUT_DIR}/{channel.lower()}.json"
    data['fetch_metadata'] = {
        "last_updated_at": datetime.now().isoformat(),
        "status": "success"
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    ensure_directory()
    channels = load_channels()
    
    if not channels:
        print("📭 No channels to process.")
        return

    print(f"🚀 Processing {len(channels)} channels...")
    
    success_count = 0
    for channel in channels:
        data = fetch_channel_data(channel)
        if data and data.get('success'):
            save_channel_json(channel, data)
            print(f"✅ {channel} updated.")
            success_count += 1
        else:
            print(f"⚠️ {channel} failed or returned no data.")

    # Status update for GitHub Actions logs
    with open("current_status.txt", "w") as f:
        f.write(f"Last Run: {datetime.now().isoformat()}\n")
        f.write(f"Result: {success_count}/{len(channels)} channels synced.")

if __name__ == "__main__":
    main()
