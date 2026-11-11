import os
import sys
import time
import json
import urllib.request

def send_reply(bot_token, chat_id, text):
    """ارسال پاسخ مستقیم به پیوی کاربر در روبیکا"""
    url = f"https://botapi.rubika.ir/v3/{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            pass
    except Exception as e:
        print(f"خطا در ارسال پاسخ: {e}")

def main():
    bot_token = os.getenv("RUBIKA_BOT_TOKEN")
    if not bot_token:
        print("❌ خطا: توکن RUBIKA_BOT_TOKEN تنظیم نشده است.")
        sys.exit(1)

    url = f"https://botapi.rubika.ir/v3/{bot_token}/getUpdates"
    print("⏳ دستیار تعاملی فعال شد؛ در انتظار /start در روبیکا...")

    start_time = time.time()
    awaiting_forward_from_user = None
    discovered_channel_id = None
    last_update_id = None
    processed_message_ids = set()

    # مهلت ۵ دقیقه‌ای اکشنز
    while time.time() - start_time < 300:
        try:
            payload = {"limit": 15}
            if last_update_id:
                payload["offset"] = last_update_id

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
                    msg_id = msg.get("message_id")
                    user_chat_id = msg.get("chat_id")
                    text = (msg.get("text") or "").strip()

                    if msg_id and msg_id in processed_message_ids:
                        continue
                    if msg_id:
                        processed_message_ids.add(msg_id)

                    # مرحله اول: کاربر /start را می‌زند
                    if text == "/start":
                        awaiting_forward_from_user = user_chat_id
                        print(f"📩 دستور start از کاربر {user_chat_id} دریافت شد.")
                        send_reply(
                            bot_token,
                            user_chat_id,
                            "👋 سلام مدیر گرامی!\n\n"
                            "📌 لطفاً همین الان **یک پیام یا پستی از کانالی که مرا در آن ادمین کرده‌اید** به این چت فوروارد (هدایت) کنید تا شناسه کانال را شناسایی کنم. ⏳"
                        )

                    # مرحله دوم: بررسی پیام ارسالی/فوروارد شده پس از استارت
                    elif awaiting_forward_from_user and user_chat_id == awaiting_forward_from_user:
                        fwd = msg.get("forward_from", {})
                        fwd_chat_id = str(fwd.get("chat_id", ""))
                        
                        # اگر پیام فوروارد از کانال باشد یا شناسه تو در تو داشته باشد
                        if fwd_chat_id and fwd_chat_id.startswith("c0"):
                            discovered_channel_id = fwd_chat_id
                        elif "forwarded_from" in msg and str(msg["forwarded_from"].get("chat_id", "")).startswith("c0"):
                            discovered_channel_id = str(msg["forwarded_from"].get("chat_id"))
                        elif fwd_chat_id: # حتی اگر فرمت دیگری از شناسه کانال باشد
                            discovered_channel_id = fwd_chat_id

                        if discovered_channel_id:
                            print(f"🎉 شناسه کشف شد: {discovered_channel_id}")
                            # ارسال شناسه مستقیم به پیوی مدیر در روبیکا
                            reply_success = (
                                "✅ شناسه کانال شما با موفقیت شناسایی شد!\n\n"
                                f"📢 شناسه کانال:\n`{discovered_channel_id}`\n\n"
                                "🛠 این شناسه را کپی کنید و در بخش سکرت‌های گیت‌هاب با نام RUBIKA_CHANNEL_ID ذخیره کنید. از این پس گزارش‌ها مستقیماً در کانال پست خواهند شد."
                            )
                            send_reply(bot_token, user_chat_id, reply_success)
                            break
                        else:
                            # اگر کاربر متنی فرستاده که فوروارد نبوده است
                            send_reply(
                                bot_token,
                                user_chat_id,
                                "⚠️ پیام دریافتی فوروارد از کانال نبود!\nلطفاً یک پست را دقیقاً از داخل کانال به اینجا هدایت (Forward) کنید."
                            )

                if discovered_channel_id:
                    break

        except Exception as e:
            pass

        time.sleep(2)

    # ثبت نتیجه در ایشو گیت‌هاب
    if discovered_channel_id:
        with open("bot_discovery.md", "w", encoding="utf-8") as f:
            f.write(f"🎉 **شناسه رسمی کانال با موفقیت دریافت و در روبیکا برای شما ارسال شد!**\n\n")
            f.write(f"- 📢 **شناسه کانال (chat_id):** `{discovered_channel_id}`\n\n")
            f.write("🛠 **اقدام نهایی:** این مقدار را در سکرت **`RUBIKA_CHANNEL_ID`** ذخیره کنید.\n")
    else:
        with open("bot_discovery.md", "w", encoding="utf-8") as f:
            f.write("⏰ **مهلت ۵ دقیقه به پایان رسید!**\nدستور `/start` یا پیام فوروارد کانال در این بازه دریافت نشد.")

if __name__ == "__main__":
    main()
