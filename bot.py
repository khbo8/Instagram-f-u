from instagrapi import Client
import json
import os
import random
import time
from datetime import datetime, timedelta

SESSION_ID = os.environ.get('IG_SESSIONID')
TARGET_ACCOUNT = "instagram" 
DATA_FILE = "following_data.json"

def human_delay(min_sec=30, max_sec=90):
    time.sleep(random.randint(min_sec, max_sec))

def simulate_human_behavior(cl):
    print("جاري محاكاة سلوك بشري...")
    # تصفح الصفحة الرئيسية
    cl.get_timeline_feed()
    human_delay(10, 30)
    # تصفح الريلز
    cl.get_reels_tab_feed()
    human_delay(10, 30)

def main():
    cl = Client()
    cl.login_by_sessionid(SESSION_ID)
    
    data = json.load(open(DATA_FILE)) if os.path.exists(DATA_FILE) else {}
    
    # 1. إلغاء المتابعة (بشكل عشوائي)
    now = datetime.now()
    users_to_unfollow = [uid for uid, t_str in data.items() if now - datetime.fromisoformat(t_str) >= timedelta(hours=24)]
    
    if users_to_unfollow:
        random.shuffle(users_to_unfollow) # عشوائية في الإلغاء
        for user_id in users_to_unfollow[:3]: # الغاء عدد بسيط جداً لتبدو طبيعي
            cl.user_unfollow(user_id)
            del data[user_id]
            time.sleep(random.randint(20, 60))

    # 2. المتابعة (سلوك بشري)
    simulate_human_behavior(cl)
    
    try:
        target_id = cl.user_id_from_username(TARGET_ACCOUNT)
        followers = cl.user_followers(target_id, amount=20) 
        
        # اختيار عدد عشوائي جداً من 2 إلى 4 متابعات فقط في كل دورة
        to_follow = random.sample(list(followers.keys()), min(len(followers), random.randint(2, 4)))
        
        for user_id in to_follow:
            if str(user_id) not in data:
                cl.user_follow(user_id)
                data[str(user_id)] = now.isoformat()
                print(f"تمت متابعة: {user_id}")
                human_delay(40, 120) # تأخير طويل بين المتابعات
                
        json.dump(data, open(DATA_FILE, 'w'), indent=4)
        
    except Exception as e:
        print(f"خطأ: {e}")

if __name__ == "__main__":
    main()
