import feedparser
import json
import google.generativeai as genai
from datetime import datetime
import os
import time

# এপিআই কী সংগ্রহ
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Error: API Key পাওয়া যায়নি!")
    exit(1)

genai.configure(api_key=API_KEY)
# মডেল কনফিগারেশন আরও উন্নত করা হলো
model = genai.GenerativeModel('gemini-pro')

# নিউজ সোর্স সংখ্যা বাড়ানো হলো এবং আরও স্টেবল লিঙ্ক দেওয়া হলো
NEWS_SOURCES = {
    'Anandabazar': 'https://www.anandabazar.com/rss-feed',
    'Sangbad Pratidin': 'https://www.sangbadpratidin.in/feed/',
    'Aajkaal': 'https://www.aajkaal.in/rss-feed',
    'The Telegraph (WB)': 'https://www.telegraphindia.com/feeds/west-bengal.xml',
    'News18 Bangla': 'https://bengali.news18.com/rss/politics.xml'
}

def analyze_news(title, summary):
    # এআই-কে আরও সুনির্দিষ্ট ইনস্ট্রাকশন দেওয়া
    prompt = f"""
    তুমি একজন অভিজ্ঞ রাজনৈতিক বিশ্লেষক। নিচের সংবাদের শিরোনাম ও সারাংশ গুরুত্ব দিয়ে পড়ো। 
    এরপর সাধারণ মানুষের বোঝার জন্য ৫ লাইনের একটি সারগর্ভ রাজনৈতিক বিশ্লেষণ লেখো। 
    মনে রাখবে, এটি যেন শুধু সংবাদের পুনরাবৃত্তি না হয়, বরং একটি বিশেষজ্ঞ মতামত হয়।
    
    শিরোনাম: {title}
    সারাংশ: {summary}
    
    বিশ্লেষণ (বাংলায়):
    """
    try:
        # মডেলকে একটু সময় দেওয়া হচ্ছে রেসপন্স করার জন্য
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
        else:
            return "বিশ্লেষণ তৈরি করা সম্ভব হয়নি (AI Empty Response)।"
    except Exception as e:
        print(f"AI Error for {title}: {e}")
        return f"বিশ্লেষণ তৈরি করা সম্ভব হয়নি (Error: {str(e)[:50]})"

def run_system():
    final_data = []
    print("সংবাদ সংগ্রহ ও বিশ্লেষণ শুরু হচ্ছে...")
    
    for source_name, url in NEWS_SOURCES.items():
        print(f"চেক করা হচ্ছে: {source_name}")
        feed = feedparser.parse(url)
        
        # প্রতি সোর্স থেকে এখন ৫টি করে খবর নেওয়ার চেষ্টা করবে
        for entry in feed.entries[:5]:
            title = entry.title
            link = entry.link
            # অনেক সময় সারাংশ থাকে না, তাই টাইটেলকেই ডেসক্রিপশন হিসেবে ব্যবহারের ব্যবস্থা
            summary = entry.get('summary', title) 
            
            # এআই-কে বিরতি দিয়ে কল করা হচ্ছে যাতে এপিআই ওভারলোড না হয়
            time.sleep(2) 
            analysis = analyze_news(title, summary)
            
            final_data.append({
                'title': title,
                'link': link,
                'source': source_name,
                'analysis': analysis,
                'time': datetime.now().strftime("%d %b, %I:%M %p")
            })
    
    # ডেটা সেভ করা
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print(f"মোট {len(final_data)}টি খবর প্রসেস করা হয়েছে।")

if __name__ == "__main__":
    run_system()
