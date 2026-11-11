import os
import sys
import time
import json
import urllib.request

def main():
    bot_token = os.getenv("RUBIKA_BOT_TOKEN")
    if not bot_token:
        print("❌ خطا: توکن RUBIKA_BOT_TOKEN تنظیم نشده است.")
        sys.exit(1)

    url = f"https://botapi.rubika.ir/v3/{bot_token}/getUpdates"
    print("⏳ بات در حال شنود پیام‌های کانال است...")
    
    start_time = time.time()
    discovered_channel_id = None

    while time.time() - start_time < 300: # ۵ دقیقه مهلت
        try:
            payload = {"limit": 25}
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(req, timeout=6) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)

                updates = res_json.get("data", {}).get("updates", []) or res_json.get("data", []) or []
                if isinstance(updates, list):
                    for u in updates:
                        # بررسی پیام ارسال شده مستقیماً در کانال (channel_post)
                        msg = u.get("channel_post") or u.get("new_message") or u.get("message") or {}
                        chat_id = str(msg.get("chat_id", ""))

                        # بررسی پیام فوروارد شده از کانال
                        fwd = msg.get("forward_from", {})
                        fwd_chat_id = str(fwd.get("chat_id", ""))

                        # کانال واقعی همیشه با c0 شروع می‌شود
                        if fwd_chat_id.startswith("c0"):
                            discovered_channel_id = fwd_chat_id
                            break
                        elif chat_id.startswith("c0"):
                            discovered_channel_id = chat_id
                            break

                if discovered_channel_id:
                    break
        except Exception:
            pass

        time.sleep(2)

    if discovered_channel_id:
        print(f"✅ CHANNEL_ID: {discovered_channel_id}")
        with open("bot_discovery.md", "w", encoding="utf-8") as f:
            f.write(f"🎉 **شناسه واقعی کانال روبیکا استخراج شد!**\n\n")
            f.write(f"- 📢 **شناسه کانال (chat_id):** `{discovered_channel_id}`\n\n")
            f.write("🛠 **اقدام نهایی:**\n")
            f.write("به بخش `Settings` ➔ `Secrets and variables` ➔ `Actions` بروید، مقدار سکرت **`RUBIKA_CHANNEL_ID`** را به این مقدار تغییر دهید.\n")
    else:
        print("⏰ TIME OUT")
        with open("bot_discovery.md", "w", encoding="utf-8") as f:
            f.write("⏰ **مهلت ۵ دقیقه‌ای تمام شد!**\n\n"
                    "⚠️ مطمئن شوید که ربات در کانال ادمین است و بعد از زدن کامند، **یک پیام تستی جدید داخل کانال بفرستید**.")

if __name__ == "__main__":
    main()
