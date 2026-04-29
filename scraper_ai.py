import feedparser
import json
import google.generativeai as genai
from datetime import datetime
import os
import time

# এপিআই কী সংগ্রহ
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Error: API Key missing!")
    exit(1)

genai.configure(api_key=API_KEY)

# এআই মডেল কনফিগারেশন (সরাসরি সেফটি সেটিংস সহ)
def get_analysis(title, summary):
    # সুরক্ষানীতি শিথিল করা যাতে রাজনীতি বিশ্লেষণ করা যায়
    safety = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]
    
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash', # এখানে flash মডেল ব্যবহার করছি যা দ্রুত এবং ফ্রি-তে ভালো চলে
        safety_settings=safety
    )

    prompt = f"তুমি একজন সাংবাদিক। নিচের খবরটি বিশ্লেষণ করে ৫ লাইনে এর গুরুত্ব বুঝিয়ে বলো। খবর: {title}. সারাংশ: {summary}. উত্তর শুধুমাত্র বাংলায় দাও।"
    
    try:
        # রিকোয়েস্ট লিমিট এড়াতে বিরতি
        time.sleep(4) 
        response = model.generate_content(prompt)
        
        # রেসপন্স চেক করা
        if response and response.candidates:
            return response.text.strip()
        else:
            return "বিশ্লেষণ এই মুহূর্তে করা যায়নি (AI blocked content)।"
    except Exception as e:
        print(f"Error: {e}")
        return "বিশ্লেষণ তৈরি করা সম্ভব হয়নি।"

def run_system():
    NEWS_SOURCES = {
        'Anandabazar': 'https://www.anandabazar.com/rss-feed',
        'Sangbad Pratidin': 'https://www.sangbadpratidin.in/feed/',
        'Aajkaal': 'https://www.aajkaal.in/rss-feed'
    }

    final_data = []
    for source, url in NEWS_SOURCES.items():
        feed = feedparser.parse(url)
        # সোর্স প্রতি ৪টি নিউজ
        for entry in feed.entries[:4]:
            title = entry.title
            link = entry.link
            summary = entry.get('summary', title[:100])
            
            print(f"Analysing: {title[:50]}...")
            analysis = get_analysis(title, summary)
            
            final_data.append({
                'title': title,
                'link': link,
                'source': source,
                'analysis': analysis,
                'time': datetime.now().strftime("%d %b, %I:%M %p")
            })

    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_system()
