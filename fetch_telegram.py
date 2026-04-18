import json
import os
import requests
from datetime import datetime
import hashlib

# Configuration
API_URL = "https://telegram-feed-reader.milaadfarzian.workers.dev/telegram/channel?channel=VahidOnline"
OUTPUT_DIR = "channel_data"
HISTORY_FILE = "channel_vahidonline.txt"

def ensure_directory():
    """Create output directory if it doesn't exist"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def fetch_channel_data():
    """Fetch data from the API"""
    try:
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data: {e}")
        return None

def save_full_json(data, timestamp):
    """Save complete JSON response"""
    filename = f"{OUTPUT_DIR}/full_data_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved JSON: {filename}")

def append_to_history(data):
    """Append formatted posts to main history file"""
    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*80}\n")
        f.write(f"📡 FETCH TIME: {datetime.now().isoformat()}\n")
        f.write(f"📊 Channel: {data.get('channel', 'Unknown')}\n")
        f.write(f"📈 Total Posts: {data.get('total_posts', 0)}\n")
        f.write(f"{'='*80}\n\n")
        
        posts = data.get('posts', [])
        for i, post in enumerate(posts[:10], 1):  # Save last 10 posts
            f.write(f"--- POST {i} ---\n")
            if 'datetime' in post:
                f.write(f"🕒 Time: {post['datetime']}\n")
            if 'link' in post:
                f.write(f"🔗 Link: {post['link']}\n")
            if 'views' in post:
                f.write(f"👁️ Views: {post['views']}\n")
            if 'text' in post:
                # Truncate long text
                text_preview = post['text'][:500] + "..." if len(post['text']) > 500 else post['text']
                f.write(f"📝 Text: {text_preview}\n")
            f.write("\n")
        
        f.write(f"\n✅ Total posts in this fetch: {len(posts)}\n")
        f.write(f"{'='*80}\n\n")

def save_simple_format(data, timestamp):
    """Save a simplified readable format"""
    filename = f"{OUTPUT_DIR}/readable_{timestamp}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"TELEGRAM CHANNEL: {data.get('channel', 'Unknown')}\n")
        f.write(f"FETCH TIME: {datetime.now().isoformat()}\n")
        f.write(f"TOTAL POSTS AVAILABLE: {data.get('total_posts', 0)}\n")
        f.write(f"RETURNED POSTS: {data.get('returned_posts', 0)}\n")
        f.write(f"\n{'='*60}\n\n")
        
        posts = data.get('posts', [])
        for post in posts:
            if 'datetime' in post and 'link' in post:
                f.write(f"[{post['datetime']}] {post['link']}\n")
                if 'views' in post:
                    f.write(f"  Views: {post['views']}\n")
                if 'text' in post:
                    # Get first 200 chars of text
                    text_short = post['text'][:200].replace('\n', ' ')
                    f.write(f"  Text: {text_short}...\n")
                f.write("\n")

def update_latest_file(data):
    """Always keep a 'latest.json' file"""
    latest_file = f"{OUTPUT_DIR}/latest.json"
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump({
            "last_updated": datetime.now().isoformat(),
            "channel": data.get('channel'),
            "total_posts": data.get('total_posts'),
            "latest_posts_count": len(data.get('posts', []))
        }, f, indent=2)

def main():
    print(f"\n🚀 Starting fetch at {datetime.now().isoformat()}")
    
    # Fetch data
    data = fetch_channel_data()
    if not data:
        print("❌ Failed to fetch data, exiting...")
        return
    
    # Ensure data has expected structure
    if not data.get('success'):
        print(f"❌ API returned success=false: {data}")
        return
    
    # Prepare
    ensure_directory()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save in different formats
    save_full_json(data, timestamp)
    save_simple_format(data, timestamp)
    append_to_history(data)
    update_latest_file(data)
    
    # Create a summary file that's always the same name (easy to view)
    summary_file = "current_status.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"Channel: {data.get('channel')}\n")
        f.write(f"Last Check: {datetime.now().isoformat()}\n")
        f.write(f"Total Posts in Channel: {data.get('total_posts')}\n")
        f.write(f"Posts in this fetch: {len(data.get('posts', []))}\n")
    
    print(f"✅ Complete! Total posts: {len(data.get('posts', []))}")
    print(f"📁 Files saved in: {OUTPUT_DIR}/")
    print(f"📄 History: {HISTORY_FILE}")

if __name__ == "__main__":
    main()
