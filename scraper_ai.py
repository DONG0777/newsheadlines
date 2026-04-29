import feedparser
import json
import google.generativeai as genai
from datetime import datetime
import os

# GitHub Secrets থেকে এপিআই কী সংগ্রহ করা হচ্ছে
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Error: API Key পাওয়া যায়নি! দয়া করে GitHub Secrets চেক করুন।")
    exit(1)

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

# আপনার পছন্দের নিউজ সোর্সসমূহ
NEWS_SOURCES = {
    'Anandabazar': 'https://www.anandabazar.com/rss-feed',
    'Sangbad Pratidin': 'https://www.sangbadpratidin.in/feed/',
    'Aajkaal': 'https://www.aajkaal.in/rss-feed',
    'The Telegraph (WB)': 'https://www.telegraphindia.com/feeds/west-bengal.xml'
}

def analyze_news(title, summary):
    prompt = f"""
    তুমি একজন পশ্চিমবঙ্গের প্রখ্যাত রাজনৈতিক বিশ্লেষক। নিচের সংবাদের শিরোনাম ও সারাংশ পড়ে ৫ লাইনের একটি 
    গভীর রাজনৈতিক বিশ্লেষণ (Gist) লেখো। খবরের পেছনের কারণ বা সম্ভাব্য প্রভাব আকর্ষণীয় ভাষায় তুলে ধরো।
    
    শিরোনাম: {title}
    সারাংশ: {summary}
    
    বিশ্লেষণ (বাংলায়):
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "বিশ্লেষণ এই মুহূর্তে তৈরি করা সম্ভব হয়নি।"

def run_system():
    final_data = []
    print("সংবাদ সংগ্রহ ও বিশ্লেষণ শুরু হচ্ছে...")
    for source_name, url in NEWS_SOURCES.items():
        feed = feedparser.parse(url)
        # প্রতি সোর্স থেকে ৩টি করে গুরুত্বপূর্ণ খবর নেবে
        for entry in feed.entries[:3]:
            title = entry.title
            link = entry.link
            summary = entry.get('summary', 'বিস্তারিত তথ্য নেই')
            
            analysis = analyze_news(title, summary)
            
            final_data.append({
                'title': title,
                'link': link,
                'source': source_name,
                'analysis': analysis,
                'time': datetime.now().strftime("%d %b, %I:%M %p")
            })
    
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print("সফলভাবে আপডেট হয়েছে!")

if __name__ == "__main__":
    run_system()
