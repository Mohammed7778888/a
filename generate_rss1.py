import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://3asq.org"
SOURCE_URL = f"{BASE_URL}/manga/one-piece/"
OUTPUT_FILE = "rss.xml"

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
    print(f"✅ RSS feed generated at {OUTPUT_FILE}")

def main():
    try:
        latest_url = fetch_latest_chapter()
        print("📘 Latest chapter URL found:", latest_url)
        generate_rss(latest_url)
    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    main()
