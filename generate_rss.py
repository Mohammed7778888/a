import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import subprocess
import sys

BASE_URL = "https://3asq.org"
SOURCE_URL = f"{BASE_URL}/manga/one-piece/"
OUTPUT_FILE = "rss.xml"
CHECK_INTERVAL = 120  # seconds

# ANSI color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def print_colored(text, color):
    print(f"{color}{text}{RESET}")

def fetch_latest_chapter():
    res = requests.get(SOURCE_URL)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    latest_link = soup.find("a", id="btn-read-first")
    if not latest_link:
        raise Exception("Latest chapter link not found.")

    chapter_url = latest_link["href"]
    full_url = chapter_url if chapter_url.startswith("http") else BASE_URL + chapter_url
    return full_url

def generate_rss(latest_url):
    pub_date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>ون بيس - العاشق</title>
    <description>أحدث فصول مانجا ون بيس مترجمة من موقع العاشق</description>
    <link>{SOURCE_URL}</link>
    <lastBuildDate>{pub_date}</lastBuildDate>
    <language>ar</language>

    <item>
      <title>الفصل الأحدث</title>
      <link>{latest_url}</link>
      <description>رابط الفصل الأحدث من ون بيس</description>
      <pubDate>{pub_date}</pubDate>
      <guid>{latest_url}</guid>
    </item>
  </channel>
</rss>
'''
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(rss)

def get_current_branch():
    result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception("Failed to get current git branch: " + result.stderr.strip())
    return result.stdout.strip()

def git_push():
    branch = get_current_branch()
    # Stage the changes
    subprocess.run(["git", "add", OUTPUT_FILE], check=True)

    # Check if there are changes to commit
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode == 0:
        print_colored("🟡 No updates detected, skipping git push.", YELLOW)
        return False

    # Commit changes
    commit_msg = "Update RSS feed"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)

    # Push to the current branch
    subprocess.run(["git", "push", "origin", branch], check=True)
    return True

def main():
    last_url = None
    while True:
        now = datetime.now().strftime("%H:%M:%S")
        try:
            print(f"🔍 Checking for updates at {now}...")
            latest_url = fetch_latest_chapter()

            if latest_url != last_url:
                generate_rss(latest_url)
                pushed = git_push()
                if pushed:
                    print_colored(f"✅ New chapter found and pushed: {latest_url}", GREEN)
                else:
                    print_colored(f"✅ New chapter found but no push needed: {latest_url}", GREEN)
                last_url = latest_url
            else:
                print_colored("🟡 No new chapter found.", YELLOW)

        except Exception as e:
            print_colored(f"❌ Error: {e}", RED)

        print(f"⏳ Waiting {CHECK_INTERVAL//60} minutes before next check...\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
