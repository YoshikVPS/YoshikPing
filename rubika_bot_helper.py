import os
import sys
import time
import json
import urllib.request
import urllib.error

def main():
    bot_token = os.getenv("RUBIKA_BOT_TOKEN")
    if not bot_token:
        print("❌ خطا: توکن RUBIKA_BOT_TOKEN تنظیم نشده است.")
        with open("bot_discovery.md", "w", encoding="utf-8") as f:
            f.write("⚠️ **خطا:** توکن ربات روبیکا (`RUBIKA_BOT_TOKEN`) در سکرت‌های گیت‌هاب تعریف نشده است.")
        sys.exit(1)

    url = f"https://botapi.rubika.ir/v3/{bot_token}/getUpdates"
    print("⏳ بات در حال شنود پیام‌ها از سرور روبیکا است...")
    
    start_time = time.time()
    discovered_chat_id = None
    last_update_id = None

    while time.time() - start_time < 300: # مهلت ۵ دقیقه
        try:
            payload = {"limit": 20}
            if last_update_id:
                payload["offset"] = last_update_id

            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                }
            )

            with urllib.request.urlopen(req, timeout=6) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)

                # پیمایش ساختار بازگشتی روبیکا
                updates = res_json.get("data", {}).get("updates", []) or res_json.get("data", []) or []
                if isinstance(updates, list):
                    for u in updates:
                        # دریافت چت آیدی از انواع مدل‌های پیام
                        chat_id = (
                            u.get("chat_id") or 
                            u.get("new_message", {}).get("chat_id") or
                            u.get("message", {}).get("chat_id")
                        )
                        
                        # بررسی اگر پیام فوروارد از کانال باشد
                        msg_obj = u.get("new_message") or u.get("message") or {}
                        fwd = msg_obj.get("forward_from", {})
                        if fwd and fwd.get("chat_id"):
                            chat_id = fwd.get("chat_id")

                        if chat_id:
                            discovered_chat_id = chat_id
                            break

                if discovered_chat_id:
                    break

        except Exception as e:
            # در صورت بروز خطای مقطعی، حلقه ادامه می‌یابد
            pass

        time.sleep(2)

    if discovered_chat_id:
        print(f"✅ CHAT_ID: {discovered_chat_id}")
        with open("bot_discovery.md", "w", encoding="utf-8") as f:
            f.write(f"🎉 **شناسه چت / کانال روبیکا با موفقیت کشف شد!**\n\n")
            f.write(f"- 🆔 **شناسه کانال (chat_id):** `{discovered_chat_id}`\n\n")
            f.write("🛠 **اقدام نهایی:**\n")
            f.write("به مسیر `Settings` ➔ `Secrets and variables` ➔ `Actions` بروید، یک سکرت با نام **`RUBIKA_CHANNEL_ID`** بسازید و این مقدار را درون آن قرار دهید.\n")
    else:
        print("⏰ TIME OUT")
        with open("bot_discovery.md", "w", encoding="utf-8") as f:
            f.write("⏰ **مهلت ۵ دقیقه به پایان رسید اما پیامی دریافت نشد!**\n\n"
                    "مطمئن شوید ربات را در کانال ادمین کرده‌اید و یک پیام داخل کانال فرستاده‌اید، سپس مجدداً دستور `/bot` را ارسال کنید.")

if __name__ == "__main__":
    main()
