import feedparser
import json
import google.generativeai as genai
from datetime import datetime

# ১. এআই সেটআপ (আপনার API Key এখানে বসান)
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel('gemini-pro')

# ২. নিউজ সোর্স (RSS Feeds)
NEWS_SOURCES = {
    'Anandabazar': 'https://www.anandabazar.com/rss-feed',
    'Sangbad Pratidin': 'https://www.sangbadpratidin.in/feed/',
    'Aajkaal': 'https://www.aajkaal.in/rss-feed'
}

def analyze_news(title, summary):
    prompt = f"""
    তুমি একজন অভিজ্ঞ রাজনৈতিক বিশ্লেষক। নিচের সংবাদটির শিরোনাম এবং সারাংশ পড়ে ৪-৫ লাইনের একটি গভীর বিশ্লেষণধর্মী 'Gist' লেখো। 
    তোমার ভাষা হবে আকর্ষণীয় এবং নিরপেক্ষ। এমনভাবে লেখো যেন সাধারণ মানুষ খবরটির গুরুত্ব বুঝতে পারে। 
    সংবাদ শিরোনাম: {title}
    সংবাদ সারাংশ: {summary}
    বিশ্লেষণ (বাংলায়):
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "বিশ্লেষণ তৈরি করা সম্ভব হয়নি।"

def get_automated_news():
    final_report = []
    print("সংবাদ সংগ্রহ ও বিশ্লেষণ শুরু হচ্ছে...")

    for source_name, url in NEWS_SOURCES.items():
        feed = feedparser.parse(url)
        # প্রতি পেপার থেকে সেরা ৩টি খবর বিশ্লেষণ করবে
        for entry in feed.entries[:3]:
            title = entry.title
            link = entry.link
            summary = entry.get('summary', 'বিস্তারিত তথ্য নেই')
            
            print(f"বিশ্লেষণ চলছে: {title[:50]}...")
            
            # AI দিয়ে বিশ্লেষণ তৈরি
            ai_analysis = analyze_news(title, summary)
            
            final_report.append({
                'title': title,
                'link': link,
                'source': source_name,
                'ai_gist': ai_analysis,
                'time': datetime.now().strftime("%Y-%m-%d %H:%M")
            })
    
    # রেজাল্ট JSON ফাইলে সেভ করা
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_report, f, ensure_ascii=False, indent=4)
    print("সব খবর বিশ্লেষণ করা হয়েছে!")

if __name__ == "__main__":
    get_automated_news()
