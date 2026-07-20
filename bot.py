from instagrapi import Client
import json
import os
import random
import time
from datetime import datetime, timedelta

SESSION_ID = os.environ.get('IG_SESSIONID')

# القائمة الجديدة للحسابات الأجنبية المستهدفة (قراء الكتب الإلكترونية)
TARGET_ACCOUNTS = ["amazonkindle", "bookbub", "goodreads", "epicreads"] 
DATA_FILE = "following_data.json"

def human_delay(min_sec=30, max_sec=90):
    time.sleep(random.randint(min_sec, max_sec))

def simulate_human_behavior(cl):
    print("جاري محاكاة سلوك بشري...")
    try:
        # تصفح الصفحة الرئيسية
        cl.get_timeline_feed()
        print("تم تصفح الصفحة الرئيسية بنجاح.")
        human_delay(15, 45)
        
        # تفقد الملف الشخصي
        cl.user_info(cl.user_id)
        print("تم تفقد الملف الشخصي.")
        human_delay(10, 30)
    except Exception as e:
        print(f"تخطي خطأ أثناء الأنسنة: {e}")

def main():
    if not SESSION_ID:
        print("خطأ: لم يتم العثور على IG_SESSIONID في الـ Secrets")
        return

    # تأخير عشوائي في البداية لكسر روتين الجدولة
    initial_delay = random.randint(60, 300)
    print(f"تم بدء التشغيل... سيتم الانتظار {initial_delay} ثانية للتمويه.")
    time.sleep(initial_delay)

    cl = Client()
    print("جاري تسجيل الدخول باستخدام Session ID...")
    
    try:
        cl.login_by_sessionid(SESSION_ID)
        print("تم الدخول بنجاح!")
    except Exception as e:
        print(f"حدث خطأ أثناء تسجيل الدخول: {e}")
        return
    
    data = json.load(open(DATA_FILE)) if os.path.exists(DATA_FILE) else {}
    now = datetime.now()
    
    # 1. إلغاء المتابعة (لمن مر عليهم 24 ساعة)
    users_to_unfollow = [uid for uid, t_str in data.items() if now - datetime.fromisoformat(t_str) >= timedelta(hours=24)]
    
    if users_to_unfollow:
        random.shuffle(users_to_unfollow) # عشوائية في الإلغاء
        for user_id in users_to_unfollow[:3]: # إبقاء العدد قليل حالياً
            try:
                cl.user_unfollow(user_id)
                print(f"تم إلغاء المتابعة للحساب: {user_id}")
                del data[user_id]
                time.sleep(random.randint(20, 60))
            except Exception as e:
                print(f"خطأ أثناء الإلغاء: {e}")

    # 2. محاكاة التصفح قبل بدء المتابعة
    simulate_human_behavior(cl)
    
    # 3. المتابعة العشوائية من القائمة المستهدفة
    try:
        # هنا الكود يختار حساباً عشوائياً من القائمة في الأعلى
        chosen_target = random.choice(TARGET_ACCOUNTS)
        print(f"الحساب المستهدف لهذه الدورة هو: {chosen_target}")
        
        target_id = cl.user_id_from_username(chosen_target)
        followers = cl.user_followers(target_id, amount=40) 
        
        # اختيار عدد عشوائي جداً من 2 إلى 4 متابعات فقط في هذه الدورة
        to_follow = random.sample(list(followers.keys()), min(len(followers), random.randint(25, 40)))
        
        for user_id in to_follow:
            if str(user_id) not in data:
                cl.user_follow(user_id)
                data[str(user_id)] = now.isoformat()
                print(f"تمت متابعة الحساب: {user_id}")
                human_delay(40, 120) 
                
        # حفظ البيانات الجديدة
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        print("تم الانتهاء وحفظ البيانات بنجاح.")
        
    except Exception as e:
        print(f"خطأ أثناء المتابعة: {e}")

if __name__ == "__main__":
    main()
