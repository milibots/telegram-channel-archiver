import json
import os
import requests
from datetime import datetime

# Configuration
CHANNELS = ["VahidOnline", "BBCPersian", "Man_Zad1"]
BASE_URL = "https://telegram-feed-reader.milaadfarzian.workers.dev/telegram/channel?channel="
OUTPUT_DIR = "channel_data"

def ensure_directory():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def fetch_channel_data(channel):
    """Fetch data for a specific channel"""
    try:
        url = f"{BASE_URL}{channel}"
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching {channel}: {e}")
        return None

def save_channel_json(channel, data):
    """Save/Overwrite the single json file for this channel"""
    filename = f"{OUTPUT_DIR}/{channel.lower()}.json"
    
    # Add a 'last_updated' field to the data
    data['last_updated_at'] = datetime.now().isoformat()
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Updated: {filename}")

def main():
    print(f"🚀 Starting multi-channel fetch at {datetime.now().isoformat()}")
    ensure_directory()
    
    success_count = 0
    for channel in CHANNELS:
        print(f"📡 Fetching: {channel}...")
        data = fetch_channel_data(channel)
        
        if data and data.get('success'):
            save_channel_json(channel, data)
            success_count += 1
        else:
            print(f"⚠️ Skipping {channel} due to API error.")

    # Create a simple global status file
    with open("current_status.txt", "w") as f:
        f.write(f"Last Run: {datetime.now().isoformat()}\n")
        f.write(f"Channels Processed: {success_count}/{len(CHANNELS)}")

    print(f"\n✨ Process complete. {success_count} channels updated.")

if __name__ == "__main__":
    main()
