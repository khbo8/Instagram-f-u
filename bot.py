from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired
import json
import os
from datetime import datetime, timedelta
import random
import time

USERNAME = os.environ.get('IG_USERNAME')
PASSWORD = os.environ.get('IG_PASSWORD')
TARGET_ACCOUNT = "instagram" # ضع هنا يوزر الحساب المستهدف

DATA_FILE = "following_data.json"
SESSION_FILE = "session.json" # ملف حفظ الجلسة

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    if not USERNAME or not PASSWORD:
        print("خطأ: لم يتم العثور على بيانات تسجيل الدخول في الـ Secrets")
        return

    cl = Client()
    print("جاري تسجيل الدخول...")
    
    # محاولة تسجيل الدخول مع حفظ الجلسة وتخطي التحديات
    try:
        if os.path.exists(SESSION_FILE):
            cl.load_settings(SESSION_FILE)
            cl.login(USERNAME, PASSWORD)
            print("تم تسجيل الدخول بنجاح باستخدام الجلسة المحفوظة!")
        else:
            cl.login(USERNAME, PASSWORD)
            cl.dump_settings(SESSION_FILE)
            print("تم تسجيل الدخول لأول مرة وحفظ الجلسة بنجاح!")
            
    except ChallengeRequired:
        print("\n[تنبيه هام] إنستقرام يطلب تأكيد الدخول!")
        print("الرجاء فتح تطبيق إنستقرام في هاتفك الآن والضغط على 'هذا أنا' (This was me).")
        print("السكريبت سينتظر 60 ثانية لتتمكن من التأكيد...")
        time.sleep(60) # الانتظار دقيقة كاملة للتأكيد من الهاتف
        
        try:
            cl.login(USERNAME, PASSWORD)
            cl.dump_settings(SESSION_FILE)
            print("تم تسجيل الدخول بنجاح بعد التأكيد، وحفظ الجلسة!")
        except Exception as e:
            print(f"فشل تسجيل الدخول حتى بعد وقت الانتظار: {e}")
            return
            
    except Exception as e:
        print(f"فشل تسجيل الدخول: {e}")
        return

    data = load_data()
    now = datetime.now()

    # إلغاء المتابعة بعد 24 ساعة
    users_to_unfollow = [uid for uid, t_str in data.items() if now - datetime.fromisoformat(t_str) >= timedelta(hours=24)]

    if users_to_unfollow:
        print(f"جاري إلغاء متابعة {len(users_to_unfollow)} حساب...")
        for user_id in users_to_unfollow:
            try:
                cl.user_unfollow(user_id)
                print(f"تم إلغاء متابعة الحساب: {user_id}")
                del data[user_id]
                save_data(data)
                time.sleep(random.randint(10, 20)) 
            except Exception as e:
                print(f"خطأ أثناء إلغاء المتابعة: {e}")

    # جلب مستخدمين جدد ومتابعتهم
    try:
        print(f"جاري البحث عن متابعين من: {TARGET_ACCOUNT}")
        target_id = cl.user_id_from_username(TARGET_ACCOUNT)
        followers = cl.user_followers(target_id, amount=15) 
        
        for user_id in followers.keys():
            if str(user_id) not in data:
                print(f"جاري متابعة الحساب: {user_id}")
                cl.user_follow(user_id)
                data[str(user_id)] = now.isoformat()
                save_data(data)
                time.sleep(random.randint(15, 30))
                
    except Exception as e:
        print(f"حدث خطأ أثناء المتابعة: {e}")

    print("تم الانتهاء بنجاح.")

if __name__ == "__main__":
    main()
