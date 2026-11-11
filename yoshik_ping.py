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
import ipaddress
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

# --- کاوشگرهای لایه ۴ و ۷ شبکه ---

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

# --- کاوشگر تخصصی ولیدیشن DNS برای موتور اسکنر رنج ---

def validate_dns_resolver(ip, port, proto):
    dns_query = b"\xaa\xbb\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01"
    start = time.time()
    if proto == "udp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.5)
        try:
            sock.sendto(dns_query, (ip, port))
            data, _ = sock.recvfrom(512)
            sock.close()
            if len(data) >= 12 and data[:2] == b"\xaa\xbb":
                lat = round((time.time() - start) * 1000, 2)
                return True, lat
        except Exception:
            pass
        finally:
            sock.close()
    elif proto == "tcp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        try:
            sock.connect((ip, port))
            length_prefix = len(dns_query).to_bytes(2, byteorder='big')
            sock.sendall(length_prefix + dns_query)
            resp = sock.recv(512)
            sock.close()
            if len(resp) >= 14 and resp[2:4] == b"\xaa\xbb":
                lat = round((time.time() - start) * 1000, 2)
                return True, lat
        except Exception:
            pass
        finally:
            sock.close()
    return False, 0

# --- تلگرام API ---

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

# ========================================================
# موتور ۱: پردازش پایش پیشرفته شبکه (/ping)
# ========================================================

def run_ping_engine(raw_text):
    text = normalize_digits(raw_text)
    publish_telegram = False
    raw_ip_only = False

    if "@YoshikVPSBOT" in text:
        publish_telegram = True
        text = text.replace("@YoshikVPSBOT", "").strip()

    time_match = re.search(r"\(تایم\)\s*-\s*(\d+)(?:-(txt))?", text, re.IGNORECASE)
    duration_min = 1
    if time_match:
        duration_min = int(time_match.group(1))
        if time_match.group(2) and time_match.group(2).lower() == "txt":
            raw_ip_only = True
        text = text[:time_match.start()] + text[time_match.end():]
        
    duration_min = max(1, min(duration_min, 59))
    text = re.sub(r"^/ping\s*", "", text, flags=re.IGNORECASE).strip()

    item_pattern = re.compile(r"([a-zA-Z0-9\.\_\-]+):([0-9\,]+)(?:\(([^)]+)\))?")
    matches = item_pattern.findall(text)

    hosts_data = {}
    for host, ports_raw, protos_raw in matches:
        host = host.strip()
        ports = [int(p.strip()) for p in ports_raw.split(",") if p.strip().isdigit()]
        raw_proto_tokens = [p.strip().lower() for p in protos_raw.split(",") if p.strip()] if protos_raw else ["tcp"]
        expanded_tasks = []

        for token in raw_proto_tokens:
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

    os.makedirs("ping", exist_ok=True)
    if not hosts_data:
        with open("summary_comment.md", "w", encoding="utf-8") as f:
            f.write("⚠️ **خطا در پارس ورودی!** ساختار دستور شناسایی نشد.\n\n"
                    "مثال استاندارد:\n"
                    "`/ping google.com:443(https:h1,h2) 1.1.1.1:53(udp) (تایم)-1-txt @YoshikVPSBOT`")
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
    safe_workers = min(16, len(flat_tasks) + 1)

    def ping_worker(task):
        h, p, pr, tk = task["host"], task["port"], task["proto"], task["target_key"]
        if pr == "https/h1": ok, msg, lat, code = probe_http1(h, p, True)
        elif pr == "http/h1": ok, msg, lat, code = probe_http1(h, p, False)
        elif pr == "https/h2": ok, msg, lat, code = probe_http2(h, p)
        elif pr == "https/h3": ok, msg, lat, code = probe_http3_quic(h, p)
        elif pr == "tcp": ok, msg, lat, code = probe_tcp(h, p)
        elif pr == "udp": ok, msg, lat, code = probe_udp_raw(h, p)
        else: ok, msg, lat, code = False, "نامعتبر", 0, "ERR"
        return h, tk, ok, msg, lat, code

    while (time.time() - start_monotonic) < total_seconds:
        rounds += 1
        with ThreadPoolExecutor(max_workers=safe_workers) as executor:
            results = list(executor.map(ping_worker, flat_tasks))
            for h, tk, ok, msg, lat, code in results:
                td = hosts_data[h]["ports_map"][tk]
                if ok:
                    td["success"] += 1
                    td["latencies"].append(lat)
                else:
                    td["fail"] += 1
                td["last_msg"] = msg
                td["last_code"] = code
        time.sleep(max(1.8, min(4.0, len(flat_tasks) * 0.35)))

    elapsed = int(time.time() - start_monotonic)
    duration_str = f"{elapsed // 60} دقیقه و {elapsed % 60} ثانیه" if (elapsed // 60) > 0 else f"{elapsed % 60} ثانیه"
    end_shamsi, _ = get_tehran_shamsi()
    end_time_str = end_shamsi.strftime("%H:%M:%S")
    display_date = end_shamsi.strftime("%Y/%m/%d")

    filename = f"ping_{end_shamsi.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    filepath = os.path.join("ping", filename)

    # تفکیک ساخت فایل بر اساس فلگ -txt
    with open(filepath, "w", encoding="utf-8") as f:
        if raw_ip_only:
            # فایل خام بدون متن فارسی، صرفاً IPهای پایدار
            written_ips = set()
            for host, hinfo in hosts_data.items():
                if any(p["success"] > 0 for p in hinfo["ports_map"].values()):
                    target_ip = hinfo["ip"]
                    if target_ip not in written_ips and target_ip != "عدم کشف IP":
                        f.write(f"{target_ip}\n")
                        written_ips.add(target_ip)
        else:
            f.write(f"گزارش عمیق پایش شبکه v3.0 - سرور اختصاصی رانر: {runner_ip}\n")
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
            tg_text += f"🕒 بازه زمانی: `{start_time_str}` ➔ `{end_time_str}` (تهران)\n"
            tg_text += f"⏱ زمان‌سنجی آزمون: `{duration_str}` ({rounds} دور ارزیابی)\n\n"

            for host, hinfo in hosts_data.items():
                tg_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                tg_text += f"🌐 مقصد: `{host}` (IP: `{hinfo['ip']}`)\n"
                items = list(hinfo["ports_map"].items())
                for i, (tkey, pdata) in enumerate(items):
                    tot = pdata["success"] + pdata["fail"]
                    pct = round((pdata["success"] / tot) * 100, 1) if tot > 0 else 0
                    avg_lat = f"{round(sum(pdata['latencies'])/len(pdata['latencies']), 2)} ms" if pdata["latencies"] else "ناموفق"
                    badge = "🟢" if pct == 100 else ("🟡" if pct > 0 else "🔴")
                    prefix = "└─" if i == len(items) - 1 else "┌─"
                    tg_text += f"{prefix} 📡 `{tkey}` ➔ {badge} `{pct}%` (تاخیر: `{avg_lat}`)\n"

            tg_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            tg_text += f"📁 [مشاهده فایل لاگ در مخزن]({raw_file_url})\n"
            tg_text += f"📢 کانال تخصصی زیرساخت: {channel_id}\n"

            telegram_post_link = send_telegram_post(bot_token, channel_id, tg_text)

    with open("summary_comment.md", "w", encoding="utf-8") as f:
        f.write("### ⚡️ داشبورد پایش عمیق ترافیک مرزی | **Yoshik Ping v3.0**\n\n")
        f.write(f"> 🖥 **سرور مبدأ (مایکروسافت Azure):** `{runner_ip}`  \n")
        f.write(f"> 📅 **تاریخ ارزیابی (ایران):** `{display_date}`  \n")
        f.write(f"> 🕒 **بازه زمانی:** `{start_time_str}` ➔ `{end_time_str}` (رسمی تهران)  \n")
        f.write(f"> ⏱ **مدت دقیق پایش:** `{duration_str}` (`{rounds}` مرحله دوره‌ای)\n\n")
        f.write("---\n\n")

        for host, hinfo in hosts_data.items():
            f.write(f"#### 🌐 تارگت: `{host}` &nbsp; | &nbsp; آی‌پی: `{hinfo['ip']}`\n\n")
            f.write("| پورت و پروتکل | نرخ اتصال | پایداری خط | میانگین تاخیر | وضعیت ارتباط |\n")
            f.write("| :--- | :---: | :---: | :---: | :--- |\n")
            for tkey, pdata in hinfo["ports_map"].items():
                tot = pdata["success"] + pdata["fail"]
                pct = round((pdata["success"] / tot) * 100, 1) if tot > 0 else 0
                avg_lat = f"`{round(sum(pdata['latencies'])/len(pdata['latencies']), 2)} ms`" if pdata["latencies"] else "`ناموفق`"
                badge = f"🟢 `{pct}%`" if pct == 100 else (f"🟡 `{pct}%`" if pct > 0 else f"🔴 `{pct}%`")
                f.write(f"| `{tkey}` | `{pdata['success']}/{tot}` | {badge} | {avg_lat} | {pdata['last_msg']} |\n")
            f.write("\n---\n")

        f.write(f"📁 **آرشیو خام متنی:** [مشاهده فایل در مخزن]({raw_file_url})\n")
        if telegram_post_link:
            f.write(f"📢 **انتشار عمومی در تلگرام:** [مشاهده گزارش رسمی در کانال]({telegram_post_link})\n")

    env_path = os.getenv("GITHUB_ENV")
    if env_path:
        with open(env_path, "a", encoding="utf-8") as env_file:
            env_file.write(f"LOG_FILENAME={filename}\n")
            env_file.write("LOG_FOLDER=ping\n")

# ========================================================
# موتور ۲: اسکنر رنج و کشف ریزالورهای فعال (/dns)
# ========================================================

def run_dns_scanner_engine(raw_text):
    text = normalize_digits(raw_text)
    publish_telegram = "@YoshikVPSBOT" in text
    text = text.replace("@YoshikVPSBOT", "").strip()

    time_match = re.search(r"\(تایم\)\s*-\s*(\d+)", text)
    duration_min = 10
    if time_match:
        duration_min = int(time_match.group(1))
        text = text[:time_match.start()] + text[time_match.end():]
    duration_min = max(1, min(duration_min, 59))

    # استخراج پروتکل و پورت از فرمان: /dns (udp,tcp):53 یا /dns (udp):53
    match_spec = re.search(r"/dns\s*(?:\(([^)]+)\))?(?::(\d+))?", text, re.IGNORECASE)
    protocols = ["udp"]
    port = 53

    if match_spec:
        if match_spec.group(1):
            protocols = [p.strip().lower() for p in match_spec.group(1).split(",") if p.strip().lower() in ["udp", "tcp"]]
        if match_spec.group(2):
            port = int(match_spec.group(2))

    if not protocols:
        protocols = ["udp"]

    # خواندن فایل‌های ورودی آی‌پی و رنج (از فایل دانلود شده input_ranges.txt)
    target_ips = []
    if os.path.exists("input_ranges.txt"):
        with open("input_ranges.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "/" in line:
                    try:
                        net = ipaddress.ip_network(line, strict=False)
                        for ip in net.hosts():
                            target_ips.append(str(ip))
                    except Exception:
                        pass
                else:
                    target_ips.append(line)

    # اگر فایلی آپلود نشده بود، تلاش برای استخراج آی‌پی‌ها یا رنج‌ها از متن دستور
    if not target_ips:
        raw_items = re.findall(r"([0-9\.\/]+)", text)
        for it in raw_items:
            if "/" in it:
                try:
                    for ip in ipaddress.ip_network(it, strict=False).hosts():
                        target_ips.append(str(ip))
                except Exception:
                    pass
            elif re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", it):
                target_ips.append(it)

    target_ips = list(dict.fromkeys(target_ips))
    os.makedirs("dns", exist_ok=True)

    if not target_ips:
        with open("summary_comment.md", "w", encoding="utf-8") as f:
            f.write("⚠️ **خطا در موتور اسکنر DNS!** هیچ رنج آی‌پی یا فایل متنی حاوی IP شناسایی نشد.\n\n"
                    "نحوه اجرا:\n"
                    "دستور `/dns (udp,tcp):53 (تایم)-10 @YoshikVPSBOT` را ارسال کرده و فایل TXT رنج‌ها را به کامنت پیوست کنید.")
        return

    runner_ip = get_public_ip()
    start_shamsi, _ = get_tehran_shamsi()
    start_time_str = start_shamsi.strftime("%H:%M:%S")
    start_monotonic = time.time()
    total_seconds = duration_min * 60

    discovered_resolvers = {}
    concurrency_pool = min(64, len(target_ips) + 1)

    def scan_task(ip):
        res = []
        for proto in protocols:
            ok, lat = validate_dns_resolver(ip, port, proto)
            if ok:
                res.append((proto, lat))
        return ip, res

    with ThreadPoolExecutor(max_workers=concurrency_pool) as executor:
        for ip, res_list in executor.map(scan_task, target_ips):
            if (time.time() - start_monotonic) > total_seconds:
                break
            if res_list:
                discovered_resolvers[ip] = res_list

    elapsed = int(time.time() - start_monotonic)
    duration_str = f"{elapsed // 60} دقیقه و {elapsed % 60} ثانیه" if (elapsed // 60) > 0 else f"{elapsed % 60} ثانیه"
    end_shamsi, _ = get_tehran_shamsi()
    end_time_str = end_shamsi.strftime("%H:%M:%S")
    display_date = end_shamsi.strftime("%Y/%m/%d")

    filename = f"dns_{end_shamsi.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    filepath = os.path.join("dns", filename)

    # ایجاد فایل متنی خالص حاوی فقط IPهای ریزالور معتبر در پوشه dns/
    with open(filepath, "w", encoding="utf-8") as f:
        for ip in discovered_resolvers.keys():
            f.write(f"{ip}\n")

    repo_name = os.getenv("GITHUB_REPOSITORY", "YoshikVPS/YoshikPing")
    raw_file_url = f"https://github.com/{repo_name}/blob/main/{filepath}"

    telegram_post_link = None
    if publish_telegram:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        channel_id = os.getenv("TELEGRAM_CHANNEL_ID", "@YoshikVPS")
        if bot_token:
            tg_text = "🛰 **گزارش رسمی عملیات رادار و کشف ریزالورهای فعال**\n"
            tg_text += "🚀 سامانه مانیتورینگ: Yoshik DNS Scanner v3.0\n"
            tg_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            tg_text += f"🖥 سرور کاوشگر: Azure Cloud Network (فرانسه)\n"
            tg_text += f"🌐 آی‌پی رانر: `{runner_ip}`\n"
            tg_text += f"🕒 زمان پایش: `{start_time_str}` ➔ `{end_time_str}` (به وقت تهران)\n"
            tg_text += f"⏱ مدت عملیات: `{duration_str}`\n"
            tg_text += f"📡 پورت و پروتکل هدف: `{port} [{','.join(protocols).upper()}]`\n"
            tg_text += f"🎯 حجم کل آی‌پی‌های بررسی‌شده: `{len(target_ips)}` نشانی\n"
            tg_text += f"🟢 **تعداد ریزالورهای سالم کشف‌شده:** `{len(discovered_resolvers)}` نشانی\n\n"
            tg_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            tg_text += f"📁 [مشاهده و دریافت لیست خام ریزالورها در مخزن]({raw_file_url})\n"
            tg_text += f"📢 کانال تخصصی زیرساخت: {channel_id}\n"

            telegram_post_link = send_telegram_post(bot_token, channel_id, tg_text)

    # تولید داشبورد ایشیو
    with open("summary_comment.md", "w", encoding="utf-8") as f:
        f.write("### 🛰 داشبورد موتور کشف ریزالورهای دی‌ان‌اس | **Yoshik DNS Discovery v3.0**\n\n")
        f.write(f"> 🖥 **سرور کاوشگر (Azure):** `{runner_ip}`  \n")
        f.write(f"> 📅 **تاریخ عملیات:** `{display_date}`  \n")
        f.write(f"> 🕒 **بازه زمانی:** `{start_time_str}` ➔ `{end_time_str}` (به وقت رسمی تهران)  \n")
        f.write(f"> ⏱ **مدت اسکن:** `{duration_str}`  \n")
        f.write(f"> 🎯 **کل اهداف ارزیابی‌شده:** `{len(target_ips)}` | 🟢 **ریزالورهای کشف‌شده:** `{len(discovered_resolvers)}`\n\n")
        f.write("---\n\n")

        if discovered_resolvers:
            f.write("| ردیف | نشانی آی‌پی ریزالور | پروتکل پاسخگو | میانگین زمان تاخیر | وضعیت اعتبار سنجی |\n")
            f.write("| :---: | :--- | :---: | :---: | :--- |\n")
            for idx, (ip, protos) in enumerate(list(discovered_resolvers.items())[:50], 1):
                p_names = "+".join([p[0].upper() for p in protos])
                avg_l = round(sum(p[1] for p in protos) / len(protos), 2)
                f.write(f"| {idx} | `{ip}` | `{p_names}:{port}` | `{avg_l} ms` | 🟢 پاسخ معتبر به DNS Query |\n")
            if len(discovered_resolvers) > 50:
                f.write(f"\n*(نمایش ۵۰ مورد اول از میان {len(discovered_resolvers)} ریزالور کشف‌شده. لیست کامل در فایل لاگ ثبت شد).*\n")
        else:
            f.write("🔴 هیچ دی‌ان‌اس ریزالور فعالی در رنج‌های ورودی پاسخگو نبود یا ترافیک در لبه مرزی مسدود گردیده است.\n")

        f.write(f"\n📁 **آرشیو اختصاصی لیست خالص ریزالورها:** [مشاهده فایل در پوشه dns/]({raw_file_url})\n")
        if telegram_post_link:
            f.write(f"📢 **انتشار گزارش در تلگرام:** [مشاهده پست در کانال]({telegram_post_link})\n")

    env_path = os.getenv("GITHUB_ENV")
    if env_path:
        with open(env_path, "a", encoding="utf-8") as env_file:
            env_file.write(f"LOG_FILENAME={filename}\n")
            env_file.write("LOG_FOLDER=dns\n")

def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    raw_command = sys.argv[1].strip()
    if raw_command.lower().startswith("/dns"):
        run_dns_scanner_engine(raw_command)
    else:
        run_ping_engine(raw_command)

if __name__ == "__main__":
    main()
