import os
import re
import sys
import time
import json
import socket
import datetime
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
import jdatetime

IRAN_TZ = datetime.timezone(datetime.timedelta(hours=3, minutes=30))

def get_tehran_shamsi():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_tehran = now_utc.astimezone(IRAN_TZ)
    shamsi = jdatetime.datetime.fromgregorian(datetime=now_tehran)
    return shamsi, now_tehran

def normalize_digits(text: str) -> str:
    tbl = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
    return text.translate(tbl)

def get_public_ip():
    for url in ["https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com"]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.read().decode('utf-8').strip()
        except Exception:
            continue
    return "نامشخص"

def resolve_host_ip(host: str) -> str:
    try:
        return socket.gethostbyname(host)
    except Exception:
        return "عدم کشف IP"

def test_http_https(host, port, proto):
    url = f"{proto}://{host}:{port}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=3.5) as response:
            latency = round((time.time() - start) * 1000, 2)
            return True, f"موفق (کد {response.status})", latency
    except urllib.error.HTTPError as e:
        latency = round((time.time() - start) * 1000, 2)
        return True, f"پاسخ وب (کد {e.code})", latency
    except Exception as e:
        latency = round((time.time() - start) * 1000, 2)
        err = str(e).lower()
        if "timed out" in err or "timeout" in err:
            return False, "تایم‌اوت (احتمال فیلتر/دراپ)", latency
        if "refused" in err:
            return False, "پورت بسته (Refused)", latency
        return False, f"خطا: {str(e)[:20]}", latency

def test_tcp(host, port):
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3.0)
    try:
        sock.connect((host, port))
        sock.close()
        latency = round((time.time() - start) * 1000, 2)
        return True, "پورت باز است", latency
    except socket.timeout:
        latency = round((time.time() - start) * 1000, 2)
        return False, "تایم‌اوت (بلاک فایروال)", latency
    except ConnectionRefusedError:
        latency = round((time.time() - start) * 1000, 2)
        return False, "پورت بسته (سرویس خاموش)", latency
    except Exception as e:
        latency = round((time.time() - start) * 1000, 2)
        return False, f"خطا: {str(e)[:20]}", latency

def test_udp(host, port):
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.5)
    try:
        payload = b"\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01"
        sock.sendto(payload, (host, port))
        try:
            data, _ = sock.recvfrom(512)
            sock.close()
            latency = round((time.time() - start) * 1000, 2)
            return True, f"پاسخ UDP ({len(data)}B)", latency
        except socket.timeout:
            sock.close()
            latency = round((time.time() - start) * 1000, 2)
            return False, "تایم‌اوت UDP (بدون پاسخ)", latency
    except Exception as e:
        sock.close()
        latency = round((time.time() - start) * 1000, 2)
        return False, f"خطا UDP: {str(e)[:20]}", latency

def send_to_rubika(message_text: str):
    bot_token = os.getenv("RUBIKA_BOT_TOKEN")
    channel_id = os.getenv("RUBIKA_CHANNEL_ID")
    if not bot_token or not channel_id:
        return
    url = f"https://botapi.rubika.ir/v3/{bot_token}/sendMessage"
    payload = {"chat_id": channel_id, "text": message_text}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            pass
    except Exception as e:
        print("خطا در ارسال به روبیکا:", e)

def send_rubika_direct(bot_token, chat_id, text):
    url = f"https://botapi.rubika.ir/v3/{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=8):
            pass
    except Exception:
        pass

def run_rubika_bot_discovery():
    """شکارچی هوشمند شناسه کانال روبیکا با مکالمه مستقیم /start"""
    bot_token = os.getenv("RUBIKA_BOT_TOKEN")
    if not bot_token:
        with open("summary_comment.md", "w", encoding="utf-8") as f:
            f.write("⚠️ **خطا:** سکرت `RUBIKA_BOT_TOKEN` تنظیم نشده است.")
        return

    url = f"https://botapi.rubika.ir/v3/{bot_token}/getUpdates"
    start_time = time.time()
    awaiting_user = None
    discovered_id = None
    seen_msgs = set()

    while time.time() - start_time < 300: # مهلت ۵ دقیقه
        try:
            payload = {"limit": 15}
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=6) as response:
                res = json.loads(response.read().decode("utf-8"))
                updates = res.get("data", {}).get("updates", []) or []
                for u in updates:
                    msg = u.get("new_message") or u.get("message") or {}
                    mid = msg.get("message_id")
                    uid = msg.get("chat_id")
                    txt = (msg.get("text") or "").strip()

                    if mid and mid in seen_msgs:
                        continue
                    if mid:
                        seen_msgs.add(mid)

                    if txt == "/start":
                        awaiting_user = uid
                        send_rubika_direct(
                            bot_token, uid,
                            "👋 سلام مدیر گرامی!\n\n"
                            "📌 لطفاً همین الان **یک پیام از کانالی که من در آن ادمین هستم** را به این چت فوروارد (هدایت) کنید تا شناسه کانال را شناسایی کنم. ⏳"
                        )
                    elif awaiting_user and uid == awaiting_user:
                        fwd = msg.get("forward_from", {})
                        fwd_id = str(fwd.get("chat_id", ""))
                        if fwd_id.startswith("c0"):
                            discovered_id = fwd_id
                        elif "forwarded_from" in msg and str(msg["forwarded_from"].get("chat_id", "")).startswith("c0"):
                            discovered_id = str(msg["forwarded_from"].get("chat_id"))
                        elif fwd_id:
                            discovered_id = fwd_id

                        if discovered_id:
                            send_rubika_direct(
                                bot_token, uid,
                                "✅ شناسه کانال شما با موفقیت شناسایی شد!\n\n"
                                f"📢 شناسه کانال:\n`{discovered_id}`\n\n"
                                "🛠 این شناسه را در بخش سکرت‌های گیت‌هاب با نام RUBIKA_CHANNEL_ID ذخیره کنید."
                            )
                            break
                        else:
                            send_rubika_direct(bot_token, uid, "⚠️ پیام فوروارد از کانال نبود! لطفاً یک پست را دقیقاً از داخل کانال فوروارد کنید.")
                if discovered_id:
                    break
        except Exception:
            pass
        time.sleep(2)

    with open("summary_comment.md", "w", encoding="utf-8") as f:
        if discovered_id:
            f.write(f"🎉 **شناسه کانال روبیکا دریافت و در چت تلگرام/روبیکا ارسال شد!**\n\n- 📢 **شناسه کانال:** `{discovered_id}`\n\n🛠 مقدار بالا را در سکرت `RUBIKA_CHANNEL_ID` ذخیره کنید.")
        else:
            f.write("⏰ **مهلت ۵ دقیقه به پایان رسید!** پیامی برای استخراج شناسه دریافت نشد.")

def parse_command(raw_text):
    text = normalize_digits(raw_text)
    send_rubika = False
    duration_min = 1

    rubika_match = re.search(r"\(تایم\)\s*-\s*\(روبیکا\)\s*-\s*(\d+)", text)
    if rubika_match:
        send_rubika = True
        duration_min = int(rubika_match.group(1))
        text = text[:rubika_match.start()] + text[rubika_match.end():]
    else:
        time_match = re.search(r"\(تایم\)\s*-\s*(\d+)", text)
        if time_match:
            duration_min = int(time_match.group(1))
            text = text[:time_match.start()] + text[time_match.end():]

    duration_min = max(1, min(duration_min, 59))
    text = re.sub(r"^/ping\s*", "", text, flags=re.IGNORECASE).strip()

    matches = re.findall(r"([a-zA-Z0-9\.\_\-]+):([0-9\,]+)(?:\(([^)]+)\))?", text)
    targets = []
    for host, ports_raw, protos_raw in matches:
        ports = [int(p.strip()) for p in ports_raw.split(",") if p.strip().isdigit()]
        protos = [p.strip().lower() for p in protos_raw.split(",") if p.strip().lower() in ["http", "https", "tcp", "udp"]] if protos_raw else ["tcp"]
        resolved_ip = resolve_host_ip(host.strip())
        for port in ports:
            targets.append({
                "host": host.strip(),
                "resolved_ip": resolved_ip,
                "port": port,
                "protocols": protos
            })
    return targets, duration_min, send_rubika

def execute_single_probe(item):
    host, port, proto, key = item["host"], item["port"], item["proto"], item["key"]
    if proto in ["http", "https"]:
        ok, msg, lat = test_http_https(host, port, proto)
    elif proto == "tcp":
        ok, msg, lat = test_tcp(host, port)
    elif proto == "udp":
        ok, msg, lat = test_udp(host, port)
    else:
        ok, msg, lat = False, "پروتکل نامعتبر", 0
    return key, ok, msg, lat

def run_ping_engine(raw_command):
    targets, duration_min, send_rubika = parse_command(raw_command)
    os.makedirs("ping", exist_ok=True)

    if not targets:
        with open("summary_comment.md", "w", encoding="utf-8") as f:
            f.write("⚠️ **خطای ورودی:** ساختار دستور شناخته نشد.")
        return

    runner_ip = get_public_ip()
    total_seconds = duration_min * 60
    start_monotonic = time.time()
    start_shamsi, _ = get_tehran_shamsi()
    start_time_display = start_shamsi.strftime("%H:%M:%S")

    summary = {}
    probe_queue = []
    for t in targets:
        for proto in t["protocols"]:
            target_key = f"{t['host']}:{t['port']} [{proto.upper()}]"
            summary[target_key] = {
                "host": t["host"], "ip": t["resolved_ip"], "port": t["port"],
                "proto": proto.upper(), "success": 0, "fail": 0, "latencies": [], "last_msg": ""
            }
            probe_queue.append({"host": t["host"], "port": t["port"], "proto": proto, "key": target_key})

    rounds = 0
    while (time.time() - start_monotonic) < total_seconds:
        rounds += 1
        with ThreadPoolExecutor(max_workers=min(16, len(probe_queue) + 1)) as executor:
            results = list(executor.map(execute_single_probe, probe_queue))
            for key, ok, msg, lat in results:
                if ok:
                    summary[key]["success"] += 1
                    summary[key]["latencies"].append(lat)
                else:
                    summary[key]["fail"] += 1
                summary[key]["last_msg"] = msg
        time.sleep(max(1.5, min(4.0, len(targets) * 0.4)))

    elapsed = int(time.time() - start_monotonic)
    duration_str = f"{elapsed // 60} دقیقه و {elapsed % 60} ثانیه" if (elapsed // 60) > 0 else f"{elapsed % 60} ثانیه"
    end_shamsi, _ = get_tehran_shamsi()
    filename = f"ping_{end_shamsi.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    filepath = os.path.join("ping", filename)
    display_date = end_shamsi.strftime("%Y/%m/%d")
    end_time_display = end_shamsi.strftime("%H:%M:%S")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"گزارش پایش شبکه - آی‌پی سرور: {runner_ip} | تاریخ: {display_date} | مدت: {duration_str}\n\n")
        for key, data in summary.items():
            tot = data["success"] + data["fail"]
            avg = round(sum(data["latencies"]) / len(data["latencies"]), 2) if data["latencies"] else 0
            f.write(f"🎯 {key} -> موفق: {data['success']}/{tot} | میانگین: {avg}ms | پاسخ: {data['last_msg']}\n")

    repo_name = os.getenv("GITHUB_REPOSITORY", "")
    raw_file_url = f"https://github.com/{repo_name}/blob/main/{filepath}"
    rubika_badge = "✅ ارسال شد" if send_rubika else "خاموش"

    with open("summary_comment.md", "w", encoding="utf-8") as f:
        f.write("### ⚡️ نتیجه ارزیابی دقیق شبکه | **Yoshik Ping v2.0**\n\n")
        f.write(f"> 🖥 **آی‌پی سرور مایکروسافت:** `{runner_ip}`  \n")
        f.write(f"> 📅 **تاریخ ارزیابی (شمسی):** `{display_date}`  \n")
        f.write(f"> 🕒 **بازه زمانی:** `{start_time_display}` ➔ `{end_time_display}` (به وقت تهران)  \n")
        f.write(f"> ⏱ **مدت زمان دقیق:** `{duration_str}` (`{rounds}` مرحله پایش)  \n")
        f.write(f"> 📢 **انتشار در کانال روبیکا:** `{rubika_badge}`\n\n")
        f.write("| هدف ارزیابی | آی‌پی مقصد (Resolved IP) | پروتکل | نرخ موفقیت | میانگین Latency | وضعیت پورت |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :--- |\n")
        for key, data in summary.items():
            tot = data["success"] + data["fail"]
            avg_lat = f"`{round(sum(data['latencies'])/len(data['latencies']), 2)} ms`" if data["latencies"] else "`ناموفق`"
            status_badge = "🟢 پایدار" if data["success"] == tot else ("🟡 نوسان" if data["success"] > 0 else "🔴 قطع")
            f.write(f"| `{data['host']}:{data['port']}` | `{data['ip']}` | `{data['proto']}` | `{data['success']}/{tot}` | {avg_lat} | {status_badge} ({data['last_msg']}) |\n")
        f.write(f"\n📁 **آرشیو لاگ:** [مشاهده فایل ذخیره شده]({raw_file_url})\n")

    if send_rubika:
        rubika_post = [
            "📡 رادار پایش ترافیک بین‌الملل به مقصد ایران",
            "🌐 سنجش اتصال لبه مرزی از دیتاسنترهای مایکروسافت",
            "─────────────────────",
            f"🗓 تاریخ: {display_date}",
            f"🕒 بازه تست: {start_time_display} الی {end_time_display} (به وقت تهران)",
            f"⏱ مدت پایش: {duration_str}",
            f"🖥 آی‌پی نود تست: {runner_ip}",
            "\n📊 وضعیت دسترسی و سلامت پورت‌ها:",
            "─────────────────────"
        ]
        for key, data in summary.items():
            tot = data["success"] + data["fail"]
            avg_lat = f"{round(sum(data['latencies'])/len(data['latencies']), 2)}ms" if data["latencies"] else "ناموفق"
            icon = "🟢" if data["success"] == tot else ("🟡" if data["success"] > 0 else "🔴")
            cmsg = data["last_msg"]
            if "ssl" in cmsg.lower() or "urlopen error" in cmsg.lower():
                cmsg = "عدم تطابق SSL/TLS روی پورت"
            rubika_post.append(f"{icon} {key}\n   ├ وضعیت: {data['success']}/{tot} | تاخیر: {avg_lat}\n   └ پاسخ: {cmsg}")
        rubika_post.append("─────────────────────\n💡 پایش خودکار با موتور مستقل شبکه")
        send_to_rubika("\n".join(rubika_post))

    env_path = os.getenv("GITHUB_ENV")
    if env_path:
        with open(env_path, "a", encoding="utf-8") as env_file:
            env_file.write(f"LOG_FILENAME={filename}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].startswith("/bot"):
        run_rubika_bot_discovery()
    elif len(sys.argv) > 1:
        run_ping_engine(sys.argv[1])
