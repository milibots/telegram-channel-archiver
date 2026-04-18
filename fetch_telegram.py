import os
import requests
import json
from datetime import datetime

# Configuration
CHANNELS_LIST_FILE = "channels.json"
BASE_URL = "https://telegram-feed-reader.milaadfarzian.workers.dev/telegram/channel?channel="
OUTPUT_DIR = "channel_data"
UPDATES_FILE = "updates.json"

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

def extract_post_ids(data):
    """Helper to extract all post_ids from the custom JSON structure"""
    ids = set()
    if not data or 'posts' not in data:
        return ids
    for item in data['posts']:
        if 'post_id' in item:
            ids.add(str(item['post_id']))
    return ids

def fetch_channel_data(channel):
    try:
        url = f"{BASE_URL}{channel}"
        response = requests.get(url, timeout=25)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"   - Error fetching {channel}: {e}")
        return None

def main():
    ensure_directory()
    channels = load_channels()
    
    if not channels:
        print("📭 No channels to process.")
        return

    print(f"🚀 Processing {len(channels)} channels...")
    
    update_summary = {}
    success_count = 0

    for channel in channels:
        channel_filename = f"{OUTPUT_DIR}/{channel.lower()}.json"
        
        # 1. Load OLD data to compare
        old_ids = set()
        if os.path.exists(channel_filename):
            try:
                with open(channel_filename, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                    old_ids = extract_post_ids(old_data)
            except:
                pass # If file is corrupt, treat as 0 old posts

        # 2. Fetch NEW data
        new_data = fetch_channel_data(channel)
        
        if new_data and new_data.get('success'):
            # 3. Calculate how many are new
            new_ids = extract_post_ids(new_data)
            # Find IDs in new_ids that are NOT in old_ids
            diff = new_ids - old_ids
            new_count = len(diff)
            
            # Store update message
            update_summary[channel] = f"{new_count} new messages"

            # 4. Save the full new JSON data
            new_data['fetch_metadata'] = {
                "last_updated_at": datetime.now().isoformat(),
                "status": "success",
                "new_posts_found": new_count
            }
            with open(channel_filename, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ {channel} updated: {new_count} new.")
            success_count += 1
        else:
            print(f"⚠️ {channel} failed or returned no data.")
            update_summary[channel] = "Failed to fetch"

    # 5. Write the updates.json file
    with open(UPDATES_FILE, "w", encoding='utf-8') as f:
        json.dump(update_summary, f, ensure_ascii=False, indent=2)

    # Status update for GitHub Actions logs
    with open("current_status.txt", "w") as f:
        f.write(f"Last Run: {datetime.now().isoformat()}\n")
        f.write(f"Result: {success_count}/{len(channels)} channels synced.\n")
        f.write(f"Updates saved to {UPDATES_FILE}")

if __name__ == "__main__":
    main()
