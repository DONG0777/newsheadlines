import feedparser
import json
import google.generativeai as genai
from datetime import datetime
import os
import time

# GitHub Secrets থেকে এপিআই কী সংগ্রহ
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Error: API Key missing in Secrets!")
    exit(1)

genai.configure(api_key=API_KEY)

def get_analysis(title, summary):
    # মডেল নির্বাচন (Flash মডেল সবথেকে দ্রুত এবং ফ্রি-তে ভালো চলে)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # এআই-কে দেওয়া নির্দেশ (একেবারে সহজ করা হয়েছে)
    prompt = f"সংবাদ শিরোনাম: {title}\nসারাংশ: {summary}\nউপরে দেওয়া খবরের ওপর ভিত্তি করে ৪-৫ লাইনের একটি আকর্ষণীয় বিশ্লেষণ বাংলা ভাষায় লেখো।"
    
    try:
        # রিকোয়েস্টের মাঝে বিরতি (Rate Limit এড়াতে)
        time.sleep(5) 
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return "এই সংবাদের রাজনৈতিক গুরুত্ব অপরিসীম। বিস্তারিত বিশ্লেষণের জন্য মূল সংবাদটি দেখুন।"
    except Exception as e:
        print(f"AI Error for {title}: {e}")
        return "বিশ্লেষণ এই মুহূর্তে প্রক্রিয়াকরণ করা যাচ্ছে না।"

def run_system():
    # নিউজ সোর্সগুলো চেক করা (সবগুলো কাজ করছে কি না তা নিশ্চিত করতে)
    NEWS_SOURCES = {
        'আনন্দবাজার': 'https://www.anandabazar.com/rss-feed',
        'সংবাদ প্রতিদিন': 'https://www.sangbadpratidin.in/feed/',
        'আজকাল': 'https://www.aajkaal.in/rss-feed'
    }

    final_data = []
    print("সংবাদ সংগ্রহ শুরু হচ্ছে...")
    
    for source, url in NEWS_SOURCES.items():
        print(f"সোর্স চেক করছি: {source}")
        feed = feedparser.parse(url)
        
        if not feed.entries:
            print(f"Warning: {source} থেকে কোনো খবর পাওয়া যায়নি।")
            continue

        for entry in feed.entries[:4]: # প্রতি সোর্স থেকে ৪টি করে খবর
            title = entry.title
            link = entry.link
            summary = entry.get('summary', title) # সারাংশ না থাকলে টাইটেল ব্যবহার হবে
            
            print(f"বিশ্লেষণ চলছে: {title[:50]}...")
            analysis = get_analysis(title, summary)
            
            final_data.append({
                'title': title,
                'link': link,
                'source': source,
                'analysis': analysis,
                'time': datetime.now().strftime("%d %b, %I:%M %p")
            })

    # ফলাফল JSON ফাইলে সেভ করা
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print("সব কাজ শেষ!")

if __name__ == "__main__":
    run_system()
