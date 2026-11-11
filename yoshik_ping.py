import os
import re
import sys
import time
import json
import socket
import datetime
import urllib.request
import urllib.error
import ssl
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

# --- کاوشگرهای لایه‌های شبکه و وب ---

def probe_http1(host, port, is_ssl=True):
    proto = "https" if is_ssl else "http"
    url = f"{proto}://{host}:{port}/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) YoshikPing/3.0"})
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=3.0, context=ctx if is_ssl else None) as response:
            latency = round((time.time() - start) * 1000, 2)
            return True, f"پاسخ لایه ۷ استاندارد (کد {response.status})", latency, "UP"
    except urllib.error.HTTPError as e:
        latency = round((time.time() - start) * 1000, 2)
        return True, f"پاسخ وب استاندارد (کد {e.code})", latency, "UP"
    except Exception as e:
        latency = round((time.time() - start) * 1000, 2)
        err = str(e).lower()
        if "timeout" in err:
            return False, "تایم‌اوت در لبه مرزی/فیلتر", latency, "TIMEOUT"
        if "refused" in err:
            return False, "مسیر باز / وب‌سرور غیرفعال", latency, "REFUSED"
        if "ssl" in err:
            return False, "خطای TLS/SSL روی پورت", latency, "SSL_ERR"
        return False, f"خطا: {str(e)[:25]}", latency, "FAIL"

def probe_http2(host, port):
    start = time.time()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_alpn_protocols(['h2', 'http/1.1'])
    try:
        sock = socket.create_connection((host, port), timeout=3.0)
        ssock = ctx.wrap_socket(sock, server_hostname=host)
        negotiated = ssock.selected_alpn_protocol()
        latency = round((time.time() - start) * 1000, 2)
        ssock.close()
        if negotiated == 'h2':
            return True, "مذاکره مالتی‌پلکس ALPN (HTTP/2) موفق", latency, "UP"
        else:
            return False, f"سرور از H2 پشتیبانی نمی‌کند (ارائه: {negotiated})", latency, "NO_H2"
    except socket.timeout:
        latency = round((time.time() - start) * 1000, 2)
        return False, "تایم‌اوت در هندشیک TLS/H2", latency, "TIMEOUT"
    except Exception as e:
        latency = round((time.time() - start) * 1000, 2)
        return False, f"خطای H2: {str(e)[:25]}", latency, "FAIL"

def probe_http3_quic(host, port):
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.5)
    # پکت هندشیک اولیه QUIC Initial جهت اعتبارسنجی لایه ۳ وب
    quic_initial_payload = (
        b"\xc0\x00\x00\x00\x01\x08\x01\x02\x03\x04\x05\x06\x07\x08"
        b"\x00\x00\x40\x50" + b"\x00" * 1150
    )
    try:
        sock.sendto(quic_initial_payload, (host, port))
        try:
            data, _ = sock.recvfrom(2048)
            sock.close()
            latency = round((time.time() - start) * 1000, 2)
            return True, f"هندشیک QUIC و لایه H3 تایید شد ({len(data)}B)", latency, "UP"
        except socket.timeout:
            sock.close()
            latency = round((time.time() - start) * 1000, 2)
            # در صورتی که دیتای بازگشتی دراپ شود ولی مسیر باز باشد
            return False, "عدم پاسخ QUIC Initial (احتمال فیلترینگ UDP/H3)", latency, "TIMEOUT"
    except Exception as e:
        sock.close()
        latency = round((time.time() - start) * 1000, 2)
        return False, f"خطای ارسال QUIC: {str(e)[:25]}", latency, "FAIL"

def probe_tcp(host, port):
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2.8)
    try:
        sock.connect((host, port))
        sock.close()
        latency = round((time.time() - start) * 1000, 2)
        return True, "پورت کاملاً باز است (Handshake موفق)", latency, "UP"
    except socket.timeout:
        latency = round((time.time() - start) * 1000, 2)
        return False, "تایم‌اوت پکت (دراپ در فایروال)", latency, "TIMEOUT"
    except ConnectionRefusedError:
        latency = round((time.time() - start) * 1000, 2)
        return False, "مسیر باز / پورت بسته (سرویس خاموش)", latency, "REFUSED"
    except Exception as e:
        latency = round((time.time() - start) * 1000, 2)
        return False, f"خطای شبکه: {str(e)[:25]}", latency, "FAIL"

def probe_udp_raw(host, port):
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.2)
    try:
        # اگر پورت ۵۳ بود پکت DNS می‌فرستد؛ در غیر اینصورت تست دیتگرام تعاملی لایه ۴
        if port == 53:
            payload = b"\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01"
        else:
            payload = b"\x01\x00\x00\x00YoshikPingUDPProbe"

        sock.sendto(payload, (host, port))
        try:
            data, _ = sock.recvfrom(512)
            sock.close()
            latency = round((time.time() - start) * 1000, 2)
            return True, f"پاسخ دیتگرام فعال ({len(data)}B)", latency, "UP"
        except socket.timeout:
            sock.close()
            latency = round((time.time() - start) * 1000, 2)
            return True, "پورت باز/بدون فیلتر (عدم دریافت خطای ICMP)", latency, "UP"
    except Exception as e:
        sock.close()
        latency = round((time.time() - start) * 1000, 2)
        return False, f"خطای سوکت UDP: {str(e)[:25]}", latency, "FAIL"

# --- موتور پارسر دستورات ---

def parse_input_command(raw_text):
    text = normalize_digits(raw_text)
    duration_min = 1
    publish_telegram = False

    if "@YoshikVPSBOT" in text:
        publish_telegram = True
        text = text.replace("@YoshikVPSBOT", "").strip()

    time_match = re.search(r"\(تایم\)\s*-\s*(\d+)", text)
    if time_match:
        duration_min = int(time_match.group(1))
        text = text[:time_match.start()] + text[time_match.end():]
        
    duration_min = max(1, min(duration_min, 59))
    text = re.sub(r"^/ping\s*", "", text, flags=re.IGNORECASE).strip()

    # استخراج تارگت‌ها به همراه مشخصات پروتکل
    item_pattern = re.compile(r"([a-zA-Z0-9\.\_\-]+):([0-9\,]+)(?:\(([^)]+)\))?")
    matches = item_pattern.findall(text)

    hosts_data = {}
    for host, ports_raw, protos_raw in matches:
        host = host.strip()
        ports = [int(p.strip()) for p in ports_raw.split(",") if p.strip().isdigit()]
        
        raw_proto_tokens = [p.strip().lower() for p in protos_raw.split(",") if p.strip()] if protos_raw else ["tcp"]
        expanded_tasks = []

        for token in raw_proto_tokens:
            # مدیریت هوشمند اشتباه http:h3 به https:h3
            if token == "http:h3":
                token = "https:h3"

            if token == "https":
                expanded_tasks.extend(["https/h1", "https/h2", "https/h3"])
            elif token == "http":
                expanded_tasks.append("http/h1")
            elif token.startswith("https:"):
                sub_parts = token.split(":")[1].split(",")
                for sp in sub_parts:
                    if sp in ["h1", "h2", "h3"]:
                        expanded_tasks.append(f"https/{sp}")
            elif token.startswith("http:"):
                sub_parts = token.split(":")[1].split(",")
                for sp in sub_parts:
                    if sp in ["h1", "h2"]:
                        expanded_tasks.append(f"http/{sp}")
            elif token in ["tcp", "udp"]:
                expanded_tasks.append(token)

        if not expanded_tasks:
            expanded_tasks = ["tcp"]

        if host not in hosts_data:
            hosts_data[host] = {
                "host": host,
                "ip": resolve_host_ip(host),
                "ports_map": {}
            }

        for port in ports:
            for task_proto in expanded_tasks:
                k = f"{port} [{task_proto.upper()}]"
                if k not in hosts_data[host]["ports_map"]:
                    hosts_data[host]["ports_map"][k] = {
                        "port": port,
                        "proto": task_proto,
                        "success": 0,
                        "fail": 0,
                        "latencies": [],
                        "last_msg": "",
                        "last_code": ""
                    }

    return hosts_data, duration_min, publish_telegram

def worker_task(task):
    host, port, proto, target_key = task["host"], task["port"], task["proto"], task["target_key"]
    if proto == "https/h1":
        ok, msg, lat, code = probe_http1(host, port, is_ssl=True)
    elif proto == "http/h1":
        ok, msg, lat, code = probe_http1(host, port, is_ssl=False)
    elif proto == "https/h2":
        ok, msg, lat, code = probe_http2(host, port)
    elif proto == "https/h3":
        ok, msg, lat, code = probe_http3_quic(host, port)
    elif proto == "tcp":
        ok, msg, lat, code = probe_tcp(host, port)
    elif proto == "udp":
        ok, msg, lat, code = probe_udp_raw(host, port)
    else:
        ok, msg, lat, code = False, "پروتکل نامعتبر", 0, "ERR"
    return host, target_key, ok, msg, lat, code

# --- ارسال گزارش به تلگرام ---

def send_telegram_post(bot_token, channel_id, message_text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": channel_id,
        "text": message_text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get("ok"):
                msg_id = data["result"]["message_id"]
                ch_clean = channel_id.replace("@", "")
                return f"https://t.me/{ch_clean}/{msg_id}"
    except Exception as e:
        print(f"Error publishing to Telegram: {e}")
    return None

def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    hosts_data, duration_min, publish_telegram = parse_input_command(sys.argv[1])
    os.makedirs("ping", exist_ok=True)

    if not hosts_data:
        with open("summary_comment.md", "w", encoding="utf-8") as f:
            f.write("⚠️ **خطا در پارس ورودی!** ساختار دستور شناسایی نشد.\n\n"
                    "مثال استاندارد نسخه ۳.۰:\n"
                    "`/ping google.com:443(https:h1,h2) cloudflare.com:443(https:h3,udp) (تایم)-2 @YoshikVPSBOT`")
        return

    runner_ip = get_public_ip()
    total_seconds = duration_min * 60
    start_monotonic = time.time()
    start_shamsi, _ = get_tehran_shamsi()
    start_time_str = start_shamsi.strftime("%H:%M:%S")

    flat_tasks = []
    for host, hinfo in hosts_data.items():
        for tkey, pinfo in hinfo["ports_map"].items():
            flat_tasks.append({
                "host": host,
                "port": pinfo["port"],
                "proto": pinfo["proto"],
                "target_key": tkey
            })

    rounds = 0
    safe_workers = min(12, len(flat_tasks) + 1)

    while (time.time() - start_monotonic) < total_seconds:
        rounds += 1
        with ThreadPoolExecutor(max_workers=safe_workers) as executor:
            results = list(executor.map(worker_task, flat_tasks))
            for host, tkey, ok, msg, lat, code in results:
                target_dict = hosts_data[host]["ports_map"][tkey]
                if ok:
                    target_dict["success"] += 1
                    target_dict["latencies"].append(lat)
                else:
                    target_dict["fail"] += 1
                target_dict["last_msg"] = msg
                target_dict["last_code"] = code

        time.sleep(max(1.8, min(4.0, len(flat_tasks) * 0.35)))

    elapsed = int(time.time() - start_monotonic)
    duration_str = f"{elapsed // 60} دقیقه و {elapsed % 60} ثانیه" if (elapsed // 60) > 0 else f"{elapsed % 60} ثانیه"
    end_shamsi, _ = get_tehran_shamsi()
    end_time_str = end_shamsi.strftime("%H:%M:%S")
    display_date = end_shamsi.strftime("%Y/%m/%d")

    filename = f"ping_{end_shamsi.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    filepath = os.path.join("ping", filename)

    # ۱. تولید و ذخیره لاگ تمیز در مخزن (فاقد هرگونه لینک تلگرام)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"گزارش عمیق پایش شبکه v3.0 - سرور اختصاصی گیت‌هاب: {runner_ip}\n")
        f.write(f"تاریخ: {display_date} | بازه: {start_time_str} تا {end_time_str} ({duration_str})\n")
        f.write("=" * 65 + "\n\n")

        for host, hinfo in hosts_data.items():
            f.write(f"🌐 هاست: {host} (IP: {hinfo['ip']})\n")
            for tkey, pdata in hinfo["ports_map"].items():
                tot = pdata["success"] + pdata["fail"]
                pct = round((pdata["success"] / tot) * 100, 1) if tot > 0 else 0
                avg = round(sum(pdata["latencies"]) / len(pdata["latencies"]), 2) if pdata["latencies"] else 0
                f.write(f"   ├─ پورت {tkey}: پایداری {pct}% ({pdata['success']}/{tot}) | تاخیر {avg}ms | وضعیت: {pdata['last_msg']}\n")
            f.write("-" * 50 + "\n")

    repo_name = os.getenv("GITHUB_REPOSITORY", "YoshikVPS/YoshikPing")
    raw_file_url = f"https://github.com/{repo_name}/blob/main/{filepath}"

    # ۲. ایجاد متن تلگرام در صورت فعال بودن تگ
    telegram_post_link = None
    if publish_telegram:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        channel_id = os.getenv("TELEGRAM_CHANNEL_ID", "@YoshikVPS")
        if bot_token:
            tg_text = "📊 گزارش تحلیلی پایش ترافیک و پروتکل‌های لبه مرزی\n"
            tg_text += "🚀 سامانه مانیتورینگ: Yoshik Ping v3.0 [Edge Core Engine]\n"
            tg_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            tg_text += f"🖥 گره مبدأ: Azure Cloud Network (فرانسه / غرب اروپا)\n"
            tg_text += f"🌐 آی‌پی پایشگر: `{runner_ip}`\n"
            tg_text += f"🕒 بازه زمانی (رسمی تهران): `{start_time_str}` ➔ `{end_time_str}`\n"
            tg_text += f"⏱ زمان‌سنجی آزمون: `{duration_str}` ({rounds} مرحله دوره‌ای موازی)\n\n"

            for host, hinfo in hosts_data.items():
                tg_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                tg_text += f"🌐 مقصد ارزیابی: `{host}`\n"
                tg_text += f"📌 روتینگ آی‌پی مقصد: `{hinfo['ip']}`\n"
                tg_text += "🛰 ارزیابی لایه ۳ و روتینگ مرزی:\n"
                
                ports_list = list(hinfo["ports_map"].values())
                total_probes = sum(p["success"] + p["fail"] for p in ports_list)
                total_success = sum(p["success"] for p in ports_list)
                if total_success == total_probes:
                    tg_text += "🟢 `ارتباط کاملاً پایدار (مسیر ترافیک بین‌الملل بدون اختلال)`\n\n"
                elif total_success > 0:
                    tg_text += "🟡 `دسترسی نیمه‌پایدار / نوسان در پروتکل‌ها`\n\n"
                else:
                    tg_text += "🔴 `انسداد ترافیک یا قطعی سرور مقصد`\n\n"

                items = list(hinfo["ports_map"].items())
                for i, (tkey, pdata) in enumerate(items):
                    tot = pdata["success"] + pdata["fail"]
                    pct = round((pdata["success"] / tot) * 100, 1) if tot > 0 else 0
                    avg_lat = f"{round(sum(pdata['latencies'])/len(pdata['latencies']), 2)} ms" if pdata["latencies"] else "ناموفق"
                    badge = "🟢" if pct == 100 else ("🟡" if pct > 0 else "🔴")
                    prefix = "└─" if i == len(items) - 1 else "┌─"
                    tg_text += f"{prefix} 📡 `{tkey}`\n"
                    tg_text += f"│  ├─ نرخ اتصال: `{pdata['success']}/{tot}` (پایداری: {badge} `{pct}%`)\n"
                    tg_text += f"│  ├─ میانگین تاخیر: `{avg_lat}`\n"
                    tg_text += f"│  └─ سیگنچر وضعیت: `{pdata['last_msg']}`\n│\n"

            tg_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            tg_text += f"📁 منبع داده و کد منبع: [گیت‌هاب YoshikPing](https://github.com/{repo_name})\n"
            tg_text += f"📢 کانال تخصصی زیرساخت: {channel_id}\n"

            telegram_post_link = send_telegram_post(bot_token, channel_id, tg_text)

    # ۳. تولید داشبورد ایشیو در گیت‌هاب
    with open("summary_comment.md", "w", encoding="utf-8") as f:
        f.write("### ⚡️ داشبورد پایش عمیق ترافیک مرزی | **Yoshik Ping v3.0**\n\n")
        f.write(f"> 🖥 **سرور مبدأ (مایکروسافت Azure):** `{runner_ip}`  \n")
        f.write(f"> 📅 **تاریخ ارزیابی (ایران):** `{display_date}`  \n")
        f.write(f"> 🕒 **بازه زمانی:** `{start_time_str}` ➔ `{end_time_str}` (به وقت رسمی تهران)  \n")
        f.write(f"> ⏱ **مدت دقیق پایش:** `{duration_str}` (`{rounds}` مرحله دوره‌ای موازی)\n\n")
        f.write("---\n\n")

        for host, hinfo in hosts_data.items():
            ports_list = list(hinfo["ports_map"].values())
            total_probes = sum(p["success"] + p["fail"] for p in ports_list)
            total_success = sum(p["success"] for p in ports_list)
            overall_pct = round((total_success / total_probes) * 100, 1) if total_probes > 0 else 0

            all_timeout = all(p["last_code"] == "TIMEOUT" for p in ports_list if p["fail"] > 0) and total_success == 0
            has_refused = any(p["last_code"] == "REFUSED" for p in ports_list)

            if total_success == total_probes:
                ip_health_badge = "🟢 ارتباط کاملاً پایدار (مسیر ترافیک بین‌الملل بدون اختلال)"
            elif total_success > 0:
                ip_health_badge = f"🟡 دسترسی نیمه‌پایدار (پایداری کلی: {overall_pct}% | نوسان یا محدودیت لایه‌ها)"
            elif has_refused:
                ip_health_badge = "🟡 آی‌پی مسدود نیست (مسیر اینترنت به سرور رسیده اما سرویس‌ها خاموش‌اند)"
            elif all_timeout:
                ip_health_badge = "🔴 **هشدار مسدودی کامل آی‌پی (IP Blackhole / فیلتر در لبه مرزی یا قطعی روتینگ)**"
            else:
                ip_health_badge = "🔴 عدم دسترسی کامل از خارج از کشور"

            f.write(f"#### 🌐 تارگت: `{host}` &nbsp; | &nbsp; آی‌پی: `{hinfo['ip']}`\n")
            f.write(f"- 🛰 **تحلیل وضعیت لایه ۳ و دسترسی مرزی:** {ip_health_badge}\n\n")
            f.write("| پورت و پروتکل | نرخ اتصال | پایداری خط | میانگین تاخیر | وضعیت ارتباط |\n")
            f.write("| :--- | :---: | :---: | :---: | :--- |\n")

            for tkey, pdata in hinfo["ports_map"].items():
                tot = pdata["success"] + pdata["fail"]
                pct = round((pdata["success"] / tot) * 100, 1) if tot > 0 else 0
                avg_lat = f"`{round(sum(pdata['latencies'])/len(pdata['latencies']), 2)} ms`" if pdata["latencies"] else "`ناموفق`"
                badge = f"🟢 `{pct}%`" if pct == 100 else (f"🟡 `{pct}%`" if pct > 0 else f"🔴 `{pct}%`")
                f.write(f"| `{tkey}` | `{pdata['success']}/{tot}` | {badge} | {avg_lat} | {pdata['last_msg']} |\n")

            f.write("\n---\n")

        f.write(f"📁 **آرشیو خام متنی:** [مشاهده فایل لاگ در مخزن]({raw_file_url})\n")
        if telegram_post_link:
            f.write(f"📢 **انتشار عمومی در تلگرام:** [مشاهده گزارش رسمی در کانال]({telegram_post_link})\n")
        elif publish_telegram:
            f.write("⚠️ **وضعیت تلگرام:** خطا در ارسال پیام به کانال (توکن یا دسترسی ربات را بررسی کنید).\n")

    env_path = os.getenv("GITHUB_ENV")
    if env_path:
        with open(env_path, "a", encoding="utf-8") as env_file:
            env_file.write(f"LOG_FILENAME={filename}\n")

if __name__ == "__main__":
    main()
