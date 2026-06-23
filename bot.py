from instagrapi import Client
import json
import os
from datetime import datetime, timedelta
import random
import time

# قراءة البيانات من متغيرات البيئة بـ GitHub
USERNAME = os.environ.get('IG_USERNAME')
PASSWORD = os.environ.get('IG_PASSWORD')
TARGET_ACCOUNT = "instagram" # غيره للحساب المستهدف

DATA_FILE = "following_data.json"

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
    try:
        cl.login(USERNAME, PASSWORD)
        print("تم تسجيل الدخول بنجاح!")
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

    # جلب مستخدمين جدد ومتابعتهم (تم تقليل العدد لـ 15 لتفادي الحظر الفوري)
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
