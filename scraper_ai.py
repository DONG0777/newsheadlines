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

# এআই মডেলের সুরক্ষানীতি শিথিল করা যাতে রাজনৈতিক খবর বিশ্লেষণ করতে পারে
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

model = genai.GenerativeModel(model_name='gemini-pro', safety_settings=safety_settings)

# নিউজ সোর্সগুলো আপডেট করা হলো
NEWS_SOURCES = {
    'Anandabazar': 'https://www.anandabazar.com/rss-feed',
    'Sangbad Pratidin': 'https://www.sangbadpratidin.in/feed/',
    'Aajkaal': 'https://www.aajkaal.in/rss-feed',
    'News18 Bangla': 'https://bengali.news18.com/rss/politics.xml'
}

def analyze_news(title, summary):
    # এআই-কে নির্দেশ দেওয়া
    prompt = f"""
    তুমি পশ্চিমবঙ্গের একজন প্রবীণ রাজনৈতিক ভাষ্যকার। নিচের সংবাদটি পড়ে সাধারণ মানুষের জন্য ৫ লাইনের একটি 
    নিরপেক্ষ এবং বুদ্ধিবৃত্তিক রাজনৈতিক বিশ্লেষণ লেখো। 
    শিরোনাম: {title}
    সারাংশ: {summary}
    বিশ্লেষণ (বাংলায়):
    """
    try:
        # এপিআই কল করার মাঝে ২ সেকেন্ড বিরতি যাতে লিমিট শেষ না হয়
        time.sleep(2)
        response = model.generate_content(prompt)
        
        # যদি এআই টেকস্ট জেনারেট করে
        if response and hasattr(response, 'text') and response.text:
            return response.text.strip()
        else:
            # যদি এআই কোনো কারণে ব্লক করে বা ফাঁকা দেয়
            return "এই সংবাদের গভীরতা বিশ্লেষণে কিছুটা সময় প্রয়োজন। মূল খবরটি দেখুন।"
    except Exception as e:
        print(f"AI Error: {e}")
        return "বর্তমানে এই সংবাদের বিশ্লেষণ উপলব্ধ নেই।"

def run_system():
    final_data = []
    print("সংবাদ সংগ্রহ ও বিশ্লেষণ শুরু হচ্ছে...")
    
    for source_name, url in NEWS_SOURCES.items():
        print(f"প্রসেসিং: {source_name}")
        feed = feedparser.parse(url)
        
        # প্রতি সোর্স থেকে ৫টি খবর
        for entry in feed.entries[:5]:
            title = entry.title
            link = entry.link
            summary = entry.get('summary', title) 
            
            analysis = analyze_news(title, summary)
            
            final_data.append({
                'title': title,
                'link': link,
                'source': source_name,
                'analysis': analysis,
                'time': datetime.now().strftime("%d %b, %I:%M %p")
            })
    
    # JSON ফাইলে সেভ করা
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print("সব খবর সফলভাবে প্রসেস করা হয়েছে।")

if __name__ == "__main__":
    run_system()