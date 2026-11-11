import os
import sys
import time
import json
import urllib.request

def main():
    bot_token = os.getenv("RUBIKA_BOT_TOKEN")
    if not bot_token:
        print("ERROR: سکرت RUBIKA_BOT_TOKEN تنظیم نشده است.")
        sys.exit(1)

    url = f"https://botapi.rubika.ir/v3/{bot_token}/getUpdates"
    print("⏳ بات در حال گوش دادن به پیام‌های جدید است...")
    
    start_time = time.time()
    discovered_chat_id = None
    title = ""

    # ۵ دقیقه مهلت برای دریافت پیام ارسالی از کانال به بات
    while time.time() - start_time < 300:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                
                # استخراج پیام‌ها از getUpdates طبق مستندات روبیکا
                updates = data.get("data", {}).get("updates", [])
                for update in updates:
                    msg = update.get("new_message", {})
                    chat_id = msg.get("chat_id")
                    
                    # اگر پیام از طرف کانال یا فوروارد از کانال باشد
                    forward_from = msg.get("forward_from", {})
                    if forward_from and forward_from.get("chat_id"):
                        discovered_chat_id = forward_from.get("chat_id")
                        title = forward_from.get("title", "کانال شما")
                        break
                    elif chat_id and (str(chat_id).startswith("c0") or str(chat_id).startswith("b0")):
                        discovered_chat_id = chat_id
                        break
                    elif chat_id:
                        discovered_chat_id = chat_id
                        break

                if discovered_chat_id:
                    break
        except Exception as e:
            pass
        time.sleep(3)

    if discovered_chat_id:
        print(f"FOUND:{discovered_chat_id}")
        with open("bot_discovery.md", "w", encoding="utf-8") as f:
            f.write(f"🎉 **شناسه چت/کانال روبیکا با موفقیت استخراج شد!**\n\n")
            f.write(f"🔹 **شناسه عددی (chat_id):** `{discovered_chat_id}`\n\n")
            f.write("🛠 **اقدام بعدی مدیر:**\n")
            f.write("وارد بخش `Settings` ➔ `Secrets and variables` ➔ `Actions` مخزن شوید، یک سکرت به نام **`RUBIKA_CHANNEL_ID`** بسازید و این مقدار را در آن ذخیره کنید.\n")
    else:
        print("TIMEOUT")
        with open("bot_discovery.md", "w", encoding="utf-8") as f:
            f.write("⏰ **مهلت ۵ دقیقه‌ای به پایان رسید!**\nهیچ پیامی در این بازه دریافت نشد. مطمئن شوید پیامی از کانال برای ربات فرستاده‌اید و دوباره امتحان کنید.\n")

if __name__ == "__main__":
    main()
