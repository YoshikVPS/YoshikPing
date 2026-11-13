import os
import re
import sys
import time
import json
import html
import socket
import struct
import random
import datetime
import urllib.request
import urllib.error
import urllib.parse
import ssl
from concurrent.futures import ThreadPoolExecutor
import jdatetime

IRAN_TZ = datetime.timezone(datetime.timedelta(hours=3, minutes=30))


def get_tehran_shamsi(dt_utc=None):
    if dt_utc is None:
        dt_utc = datetime.datetime.now(datetime.timezone.utc)
    now_tehran = dt_utc.astimezone(IRAN_TZ)
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
                return resp.read().decode("utf-8").strip()
        except Exception:
            continue
    return "نامشخص"


def resolve_host_ip(host: str) -> str:
    try:
        return socket.gethostbyname(host)
    except Exception:
        return "عدم کشف IP"


# --- ارتباط با GitHub Issue API ---

def gh_api_request(method, endpoint, token, payload=None):
    url = f"https://api.github.com{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "YoshikPing-v4"
    }
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"GitHub API Error ({endpoint}): {e}")
        return None


def post_issue_comment(repo, issue_number, token, body):
    if not (repo and issue_number and token):
        return None
    return gh_api_request("POST", f"/repos/{repo}/issues/{issue_number}/comments", token, {"body": body})


# --- ارسال گزارش به تلگرام (HTML + Expandable Blockquote + SendDocument) ---

def send_telegram_post(bot_token, channel_id, message_html):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": channel_id,
        "text": message_html,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                msg_id = data["result"]["message_id"]
                ch_clean = channel_id.replace("@", "")
                return f"https://t.me/{ch_clean}/{msg_id}"
    except Exception as e:
        print(f"Error publishing to Telegram: {e}")
    return None


def send_telegram_document(bot_token, channel_id, filepath, caption_html=""):
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    boundary = f"----YoshikBoundary{random.randint(100000, 999999)}"
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        file_data = f.read()

    parts = []
    for name, val in [("chat_id", channel_id), ("caption", caption_html), ("parse_mode", "HTML")]:
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{val}\r\n".encode("utf-8"))
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"document\"; filename=\"{filename}\"\r\nContent-Type: text/plain\r\n\r\n".encode("utf-8")
        + file_data + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                msg_id = data["result"]["message_id"]
                ch_clean = channel_id.replace("@", "")
                return f"https://t.me/{ch_clean}/{msg_id}"
    except Exception as e:
        print(f"Error sending document to Telegram: {e}")
    return None


# ==============================================================================
# ۱. کاوشگرهای لایه ۴ و ۷ شبکه (/ping)
# ==============================================================================

def probe_http1(host, port, is_ssl=True):
    proto = "https" if is_ssl else "http"
    url = f"{proto}://{host}:{port}/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) YoshikPing/4.0"})
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
    ctx.set_alpn_protocols(["h2", "http/1.1"])
    try:
        sock = socket.create_connection((host, port), timeout=3.0)
        ssock = ctx.wrap_socket(sock, server_hostname=host)
        negotiated = ssock.selected_alpn_protocol()
        latency = round((time.time() - start) * 1000, 2)
        ssock.close()
        if negotiated == "h2":
            return True, "مذاکره مالتی‌پلکس ALPN (HTTP/2) موفق", latency, "UP"
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


def run_ping_mode(raw_text: str):
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
    elif text.lower().endswith("-txt"):
        raw_ip_only = True
        text = text[:-4].strip()

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
                for sp in token.split(":")[1].split(","):
                    if sp in ["h1", "h2", "h3"]:
                        expanded_tasks.append(f"https/{sp}")
            elif token.startswith("http:"):
                for sp in token.split(":")[1].split(","):
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
    safe_workers = min(64, max(1, len(flat_tasks)))

    def worker_task(task):
        h, p, pr, tk = task["host"], task["port"], task["proto"], task["target_key"]
        if pr == "https/h1": ok, msg, lat, code = probe_http1(h, p, True)
        elif pr == "http/h1": ok, msg, lat, code = probe_http1(h, p, False)
        elif pr == "https/h2": ok, msg, lat, code = probe_http2(h, p)
        elif pr == "https/h3": ok, msg, lat, code = probe_http3_quic(h, p)
        elif pr == "tcp": ok, msg, lat, code = probe_tcp(h, p)
        elif pr == "udp": ok, msg, lat, code = probe_udp_raw(h, p)
        else: ok, msg, lat, code = False, "نامعتبر", 0, "ERR"
        return h, tk, ok, msg, lat, code

    while True:
        rounds += 1
        with ThreadPoolExecutor(max_workers=safe_workers) as executor:
            results = list(executor.map(worker_task, flat_tasks))
            for h, tk, ok, msg, lat, code in results:
                td = hosts_data[h]["ports_map"][tk]
                if ok:
                    td["success"] += 1
                    td["latencies"].append(lat)
                else:
                    td["fail"] += 1
                td["last_msg"] = msg
                td["last_code"] = code
        if (time.time() - start_monotonic) >= total_seconds:
            break
        time.sleep(min(2.5, max(1.0, len(flat_tasks) * 0.01)))

    elapsed = int(time.time() - start_monotonic)
    duration_str = f"{elapsed // 60} دقیقه و {elapsed % 60} ثانیه" if (elapsed // 60) > 0 else f"{elapsed % 60} ثانیه"
    end_shamsi, _ = get_tehran_shamsi()
    end_time_str = end_shamsi.strftime("%H:%M:%S")
    display_date = end_shamsi.strftime("%Y/%m/%d")

    filename = f"ping_{end_shamsi.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    filepath = os.path.join("ping", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        if raw_ip_only:
            written_ips = set()
            for host, hinfo in hosts_data.items():
                if any(p["success"] > 0 for p in hinfo["ports_map"].values()):
                    target_ip = hinfo["ip"]
                    if target_ip not in written_ips and target_ip != "عدم کشف IP":
                        f.write(f"{target_ip}\n")
                        written_ips.add(target_ip)
        else:
            f.write(f"گزارش عمیق پایش شبکه v4.0 - سرور اختصاصی رانر: {runner_ip}\n")
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
            header_html = (
                f"📊 <b>گزارش تحلیلی پایش ترافیک و پروتکل‌های لبه مرزی</b>\n"
                f"🚀 <b>سامانه مانیتورینگ:</b> Yoshik Ping v4.0 [Edge Core]\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🖥 <b>گره مبدأ:</b> Azure Cloud Network\n"
                f"🌐 <b>آی‌پی پایشگر:</b> <code>{html.escape(runner_ip)}</code>\n"
                f"📅 <b>تاریخ:</b> <code>{display_date}</code>\n"
                f"🕒 <b>بازه زمانی:</b> <code>{start_time_str}</code> ➔ <code>{end_time_str}</code> (تهران)\n"
                f"⏱ <b>زمان‌سنجی آزمون:</b> <code>{duration_str}</code> ({rounds} دور)\n"
                f"🎯 <b>تعداد تارگت:</b> <code>{len(hosts_data)}</code>\n"
            )
            details_lines = []
            for host, hinfo in hosts_data.items():
                details_lines.append(f"🌐 <b>{html.escape(host)}</b> (<code>{html.escape(hinfo['ip'])}</code>)")
                for tkey, pdata in hinfo["ports_map"].items():
                    tot = pdata["success"] + pdata["fail"]
                    pct = round((pdata["success"] / tot) * 100, 1) if tot > 0 else 0
                    avg_lat = f"{round(sum(pdata['latencies'])/len(pdata['latencies']), 2)}ms" if pdata["latencies"] else "ناموفق"
                    badge = "🟢" if pct == 100 else ("🟡" if pct > 0 else "🔴")
                    details_lines.append(f"  └ <code>{html.escape(tkey)}</code> ➔ {badge} <code>{pct}%</code> ({avg_lat})")

            footer_html = (
                f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📁 <a href=\"{raw_file_url}\">مشاهده فایل لاگ در مخزن</a>\n"
                f"📢 کانال تخصصی: {html.escape(channel_id)}"
            )
            full_details = "\n".join(details_lines)
            candidate_msg = f"{header_html}\n<blockquote expandable>{full_details}</blockquote>{footer_html}"

            if len(candidate_msg) <= 4000:
                telegram_post_link = send_telegram_post(bot_token, channel_id, candidate_msg)
            else:
                preview_lines = "\n".join(details_lines[:25]) + f"\n... و {max(0, len(details_lines) - 25)} مورد دیگر در فایل پیوست"
                short_msg = f"{header_html}\n<blockquote expandable>{preview_lines}</blockquote>{footer_html}"
                telegram_post_link = send_telegram_post(bot_token, channel_id, short_msg)
                send_telegram_document(bot_token, channel_id, filepath, f"📎 فایل کامل گزارش ({len(hosts_data)} تارگت) | تاریخ: {display_date}")

    with open("summary_comment.md", "w", encoding="utf-8") as f:
        f.write("### ⚡️ داشبورد پایش عمیق ترافیک مرزی | **Yoshik Ping v4.0**\n\n")
        f.write(f"> 🖥 **سرور مبدأ (مایکروسافت Azure):** `{runner_ip}`  \n")
        f.write(f"> 📅 **تاریخ ارزیابی (ایران):** `{display_date}`  \n")
        f.write(f"> 🕒 **بازه زمانی:** `{start_time_str}` ➔ `{end_time_str}` (رسمی تهران)  \n")
        f.write(f"> ⏱ **مدت دقیق پایش:** `{duration_str}` (`{rounds}` مرحله دوره‌ای)\n\n")
        f.write("---\n\n")

        written_chars = 0
        truncated = False
        for host, hinfo in hosts_data.items():
            block = f"#### 🌐 تارگت: `{host}` &nbsp; | &nbsp; آی‌پی: `{hinfo['ip']}`\n\n"
            block += "| پورت و پروتکل | نرخ اتصال | پایداری خط | میانگین تاخیر | وضعیت ارتباط |\n"
            block += "| :--- | :---: | :---: | :---: | :--- |\n"
            for tkey, pdata in hinfo["ports_map"].items():
                tot = pdata["success"] + pdata["fail"]
                pct = round((pdata["success"] / tot) * 100, 1) if tot > 0 else 0
                avg_lat = f"`{round(sum(pdata['latencies'])/len(pdata['latencies']), 2)} ms`" if pdata["latencies"] else "`ناموفق`"
                badge = f"🟢 `{pct}%`" if pct == 100 else (f"🟡 `{pct}%`" if pct > 0 else f"🔴 `{pct}%`")
                block += f"| `{tkey}` | `{pdata['success']}/{tot}` | {badge} | {avg_lat} | {pdata['last_msg']} |\n"
            block += "\n---\n"
            if written_chars + len(block) > 55000:
                truncated = True
                break
            f.write(block)
            written_chars += len(block)

        if truncated:
            f.write(f"\n⚠️ *به دلیل محدودیت حجم کامنت گیت‌هاب، ادامه جدول در فایل مخزن قابل مشاهده است.*\n\n")
        f.write(f"📁 **آرشیو خام متنی:** [مشاهده فایل در مخزن]({raw_file_url})\n")
        if telegram_post_link:
            f.write(f"📢 **انتشار عمومی در تلگرام:** [مشاهده گزارش رسمی در کانال]({telegram_post_link})\n")

    env_path = os.getenv("GITHUB_ENV")
    if env_path:
        with open(env_path, "a", encoding="utf-8") as env_file:
            env_file.write(f"LOG_FILENAME={filename}\n")


# ==============================================================================
# ۲. موتور تست ریزالور و تانل DNS (/dns) - الهام از WhiteDNS / CottenDNS
# ==============================================================================

def build_dns_query(qname: str, qtype: int = 1) -> tuple:
    tx_id = random.randint(1000, 65000)
    header = struct.pack(">HHHHHH", tx_id, 0x0100, 1, 0, 0, 0)
    labels = b"".join(bytes([len(p)]) + p.encode("ascii") for p in qname.split(".") if p) + b"\x00"
    question = labels + struct.pack(">HH", qtype, 1)
    return tx_id, header + question


def parse_dns_response(data: bytes, expected_tx_id: int) -> tuple:
    if len(data) < 12:
        return False, "پاسخ ناقص"
    tx_id, flags, qdcount, ancount, nscount, arcount = struct.unpack(">HHHHHH", data[:12])
    if tx_id != expected_tx_id:
        return False, "عدم تطابق TXID"
    qr = (flags >> 15) & 1
    rcode = flags & 0x0F
    if qr != 1:
        return False, "پکت پاسخ نیست"
    if rcode != 0:
        return False, f"خطای RCODE={rcode}"
    return True, f"سالم (AN:{ancount})"


def probe_dns_resolver(ip: str, port: int, proto: str) -> tuple:
    start = time.time()
    tx_id1, q1 = build_dns_query("example.com", 1)
    rand_sub = f"y{random.randint(10000,99999)}.t{random.randint(100,999)}.cloudflare.com"
    tx_id2, q2 = build_dns_query(rand_sub, 1)

    try:
        if proto == "udp":
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2.5)
            sock.sendto(q1, (ip, port))
            d1, _ = sock.recvfrom(1024)
            ok1, msg1 = parse_dns_response(d1, tx_id1)
            if not ok1:
                sock.close()
                return False, msg1, 0

            sock.sendto(q2, (ip, port))
            d2, _ = sock.recvfrom(1024)
            sock.close()
            ok2, _ = parse_dns_response(d2, tx_id2)
            lat = round((time.time() - start) * 1000, 2)
            if ok2:
                return True, "ریزالور فعال + عبور پکت تانل", lat
            return True, "ریزالور فعال (محدودیت ساب‌دامین)", lat
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.8)
            sock.connect((ip, port))
            sock.sendall(struct.pack(">H", len(q1)) + q1)
            len_buf = sock.recv(2)
            if len(len_buf) < 2:
                sock.close()
                return False, "پاسخ TCP ناقص", 0
            resp_len = struct.unpack(">H", len_buf)[0]
            d1 = sock.recv(resp_len)
            sock.close()
            ok1, msg1 = parse_dns_response(d1, tx_id1)
            lat = round((time.time() - start) * 1000, 2)
            return ok1, "ریزالور TCP فعال" if ok1 else msg1, lat
    except socket.timeout:
        return False, "تایم‌اوت", 0
    except Exception as e:
        return False, f"خطا: {str(e)[:20]}", 0


def parse_dns_targets(raw_text: str):
    text = normalize_digits(raw_text)
    publish_telegram = "@YoshikVPSBOT" in text
    text = text.replace("@YoshikVPSBOT", "").strip()
    raw_ip_only = "-txt" in text.lower()
    text = re.sub(r"\(تایم\)\s*-\s*\d+(?:-txt)?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"-txt", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^/dns\s*", "", text, flags=re.IGNORECASE).strip()

    tasks = []
    seen = set()
    tokens = re.split(r"[\s\n,]+", text)
    for tok in tokens:
        tok = tok.strip()
        if not tok:
            continue
        m = re.match(r"^([a-zA-Z0-9\.\-]+)(?::(\d+))?(?:\(([^)]+)\))?$", tok)
        if not m:
            continue
        ip = m.group(1)
        port = int(m.group(2)) if m.group(2) else 53
        protos = [p.strip().lower() for p in m.group(3).split(",")] if m.group(3) else ["udp"]
        for pr in protos:
            if pr in ["udp", "tcp"] and (ip, port, pr) not in seen:
                seen.add((ip, port, pr))
                tasks.append((ip, port, pr))
    return tasks, raw_ip_only, publish_telegram


def run_dns_mode(raw_text: str, estimate_only: bool = False):
    tasks, raw_ip_only, publish_telegram = parse_dns_targets(raw_text)
    runner_ip = get_public_ip()
    workers = min(40, max(1, len(tasks)))

    if estimate_only:
        est_sec = max(5, int((len(tasks) / workers) * 2.5) + 5)
        est_str = f"{est_sec // 60} دقیقه و {est_sec % 60} ثانیه" if est_sec >= 60 else f"{est_sec} ثانیه"
        msg = (
            f"🔬 **موتور تست ریزالور و تانل DNS (نسخه ۴.۰) آغاز به کار کرد!**\n\n"
            f"🌐 **آی‌پی رانر اکشنز:** `{runner_ip}`\n"
            f"🎯 **تعداد کل تست‌ها:** `{len(tasks)}` مورد\n"
            f"⏱ **زمان تخمینی اتمام:** حدود `{est_str}`\n\n"
            f"⏳ *لطفاً تا پایان اسکن و دریافت گزارش نهایی منتظر بمانید...*"
        )
        repo = os.getenv("GITHUB_REPOSITORY")
        issue_num = os.getenv("ISSUE_NUMBER")
        gh_token = os.getenv("GITHUB_TOKEN")
        post_issue_comment(repo, issue_num, gh_token, msg)
        return

    os.makedirs("dns", exist_ok=True)
    if not tasks:
        with open("summary_comment.md", "w", encoding="utf-8") as f:
            f.write("⚠️ **خطا در ورودی `/dns`!** هیچ آی‌پی معتبری یافت نشد.")
        return

    start_shamsi, _ = get_tehran_shamsi()
    start_time_str = start_shamsi.strftime("%H:%M:%S")
    start_mono = time.time()

    def dns_worker(item):
        ip, port, pr = item
        ok, msg, lat = probe_dns_resolver(ip, port, pr)
        return ip, port, pr, ok, msg, lat

    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(dns_worker, tasks))

    healthy = [r for r in results if r[3]]
    elapsed = int(time.time() - start_mono)
    duration_str = f"{elapsed // 60} دقیقه و {elapsed % 60} ثانیه" if elapsed >= 60 else f"{elapsed} ثانیه"
    end_shamsi, _ = get_tehran_shamsi()
    end_time_str = end_shamsi.strftime("%H:%M:%S")
    display_date = end_shamsi.strftime("%Y/%m/%d")

    filename = f"dns_{end_shamsi.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    filepath = os.path.join("dns", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        if raw_ip_only:
            written = set()
            for ip, port, pr, ok, msg, lat in healthy:
                if ip not in written:
                    f.write(f"{ip}\n")
                    written.add(ip)
        else:
            f.write(f"گزارش تست ریزالور و تانل DNS v4.0 - آی‌پی رانر: {runner_ip}\n")
            f.write(f"تاریخ: {display_date} | بازه: {start_time_str} تا {end_time_str} ({duration_str})\n")
            f.write(f"کل تست‌شده: {len(results)} | سالم: {len(healthy)}\n")
            f.write("=" * 60 + "\n")
            for ip, port, pr, ok, msg, lat in healthy:
                f.write(f"{ip}:{port} [{pr.upper()}] | {lat}ms | {msg}\n")

    repo_name = os.getenv("GITHUB_REPOSITORY", "YoshikVPS/YoshikPing")
    raw_file_url = f"https://github.com/{repo_name}/blob/main/{filepath}"

    telegram_post_link = None
    if publish_telegram:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        channel_id = os.getenv("TELEGRAM_CHANNEL_ID", "@YoshikVPS")
        if bot_token:
            tg_html = (
                f"🛡 <b>گزارش اسکن ریزالورهای سالم و تانل DNS</b>\n"
                f"🚀 <b>موتور:</b> Yoshik DNS Sentinel v4.0\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🌐 <b>آی‌پی رانر:</b> <code>{html.escape(runner_ip)}</code>\n"
                f"📅 <b>تاریخ شمسی:</b> <code>{display_date}</code>\n"
                f"🕒 <b>ساعت اتمام:</b> <code>{end_time_str}</code> (تهران)\n"
                f"✅ <b>تعداد سالم:</b> <code>{len(healthy)}</code> از <code>{len(results)}</code>\n"
                f"⏱ <b>مدت اسکن:</b> <code>{duration_str}</code>\n\n"
                f"📁 <a href=\"{raw_file_url}\">دریافت مستقیم فایل ریزالورها از مخزن</a>\n"
                f"📢 کانال: {html.escape(channel_id)}"
            )
            telegram_post_link = send_telegram_post(bot_token, channel_id, tg_html)
            if len(healthy) > 0:
                send_telegram_document(bot_token, channel_id, filepath, f"📎 لیست ریزالورهای سالم ({len(healthy)} عدد) | {display_date} - {end_time_str}")

    with open("summary_comment.md", "w", encoding="utf-8") as f:
        f.write("### 🛡 گزارش نهایی تست ریزالور و تانل DNS | **Yoshik Ping v4.0**\n\n")
        f.write(f"> 🌐 **آی‌پی رانر اکشنز:** `{runner_ip}`  \n")
        f.write(f"> 📅 **تاریخ:** `{display_date}` | 🕒 **بازه:** `{start_time_str}` ➔ `{end_time_str}`  \n")
        f.write(f"> ✅ **نتیجه:** `{len(healthy)}` ریزالور سالم از `{len(results)}` مورد تست‌شده (`{duration_str}`)\n\n")
        f.write(f"📁 **فایل خروجی در مخزن:** [مشاهده و دانلود {filename}]({raw_file_url})\n")
        if telegram_post_link:
            f.write(f"📢 **پست کانال تلگرام:** [مشاهده در کانال]({telegram_post_link})\n")

    env_path = os.getenv("GITHUB_ENV")
    if env_path:
        with open(env_path, "a", encoding="utf-8") as env_file:
            env_file.write(f"LOG_FILENAME={filename}\n")


# ==============================================================================
# نقطه ورود اصلی
# ==============================================================================

def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    if sys.argv[1] == "--dns-estimate" and len(sys.argv) >= 3:
        run_dns_mode(sys.argv[2].strip(), estimate_only=True)
        return

    raw_text = sys.argv[1].strip()
    if raw_text.startswith("/dns"):
        run_dns_mode(raw_text, estimate_only=False)
    else:
        run_ping_mode(raw_text)


if __name__ == "__main__":
    main()
