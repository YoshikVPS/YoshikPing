import os
import re
import sys
import time
import json
import urllib.request

def get_chat_by_username(bot_token, username):
    """استخراج مستقیم اطلاعات کانال با آیدی عمومی از سرور روبیکا"""
    clean_username = username.replace("@", "").strip()
    url = f"https://botapi.rubika.ir/v3/{bot_token}/getChat"
    
    payload = {"username": clean_username}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            chat_data = res.get("data", {}).get("chat", {}) or res.get("data", {})
            chat_id = chat_data.get("chat_id")
            title = chat_data.get("title", clean_username)
            if chat_id:
                return chat_id, title
    except Exception as e:
        pass
    return None, None

def listen_for_forwarded_message(bot_token):
    """شنود پیام فوروارد شده از کانال به پیوی ربات"""
    url = f"https://botapi.rubika.ir/v3/{bot_token}/getUpdates"
    start_time = time.time()
    
    while time.time() - start_time < 240: # مهلت ۴ دقیقه
        try:
            payload = {"limit": 20}
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=6) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                
                updates = res_json.get("data", {}).get("updates", []) or []
                for u in updates:
                    msg = u.get("new_message") or u.get("message") or {}
                    
                    # استخراج اطلاعات پیام فوروارد شده
                    fwd = msg.get("forward_from", {})
                    fwd_chat_id = str(fwd.get("chat_id", ""))
                    
                    if fwd_chat_id.startswith("c0"):
                        return fwd_chat_id, fwd.get("title", "کانال شما")
                    
                    # بررسی متادیتاهای تو در توی روبیکا
                    if "forwarded_from" in msg:
                        nested_id = str(msg["forwarded_from"].get("chat_id", ""))
                        if nested_id.startswith("c0"):
                            return nested_id, "کانال شما"
        except Exception:
            pass
        time.sleep(2)
        
    return None, None

def main():
    bot_token = os.getenv("RUBIKA_BOT_TOKEN")
    comment_body = sys.argv[1] if len(sys.argv) > 1 else ""
    
    if not bot_token:
        print("❌ خطا: توکن RUBIKA_BOT_TOKEN موجود نیست.")
        sys.exit(1)

    # بررسی اگر کاربر آیدی کانال را در کامنت نوشته باشد: /bot @my_channel
    username_match = re.search(r"@([a-zA-Z0-9\_]+)", comment_body)
    
    discovered_id = None
    channel_title = ""

    if username_match:
        target_username = username_match.group(1)
        print(f"🔍 در حال استعلام مستقیم کانال @{target_username} از روبیکا...")
        discovered_id, channel_title = get_chat_by_username(bot_token, target_username)

    if not discovered_id:
        print("⏳ در حال شنود پیام‌های فوروارد شده به پیوی ربات...")
        discovered_id, channel_title = listen_for_forwarded_message(bot_token)

    if discovered_id:
        print(f"✅ موفقیت: {discovered_id}")
        with open("bot_discovery.md", "w", encoding="utf-8") as f:
            f.write(f"🎉 **شناسه رسمی کانال با موفقیت دریافت شد!**\n\n")
            f.write(f"- 📢 **عنوان کانال:** `{channel_title}`\n")
            f.write(f"- 🆔 **شناسه یکتای کانال (chat_id):** `{discovered_id}`\n\n")
            f.write("🛠 **اقدام نهایی:**\n")
            f.write("به مسیر `Settings` ➔ `Secrets and variables` ➔ `Actions` بروید، مقدار سکرت **`RUBIKA_CHANNEL_ID`** را برابر این مقدار قرار دهید.\n")
    else:
        print("❌ ناموفق")
        with open("bot_discovery.md", "w", encoding="utf-8") as f:
            f.write("⚠️ **شناسه پیدا نشد!**\n\n"
                    "💡 **ساده‌ترین راه:** کافی است دستور را همراه با آیدی کانال خود بفرستید، مثال:\n"
                    "`/bot @YourChannelID`\n"
                    "(به جای YourChannelID، آیدی عمومی کانال خود در روبیکا را بنویسید).")

if __name__ == "__main__":
    main()
