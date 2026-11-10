import os
import re
import sys
import time
import socket
import datetime
import urllib.request
import urllib.error
import jdatetime

# تنظیم منطقه زمانی رسمی ایران (UTC + 03:30)
IRAN_TZ = datetime.timezone(datetime.timedelta(hours=3, minutes=30))

def get_tehran_shamsi():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_tehran = now_utc.astimezone(IRAN_TZ)
    shamsi = jdatetime.datetime.fromgregorian(datetime=now_tehran)
    return shamsi, now_tehran

def normalize_digits(text: str) -> str:
    persian_arabic = "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩"
    english = "01234567890123456789"
    return text.translate(str.maketrans(persian_arabic, english))

def get_public_ip():
    services = ["https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com"]
    for url in services:
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
        with urllib.request.urlopen(req, timeout=4) as response:
            latency = round((time.time() - start) * 1000, 2)
            return True, f"موفق (کد {response.status})", latency
    except urllib.error.HTTPError as e:
        latency = round((time.time() - start) * 1000, 2)
        return True, f"پاسخ وب (کد {e.code})", latency
    except Exception as e:
        latency = round((time.time() - start) * 1000, 2)
        err = str(e).split("]")[-1] if "]" in str(e) else str(e)
        return False, f"خطا: {err.strip()[:20]}", latency

def test_tcp(host, port):
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3.5)
    try:
        sock.connect((host, port))
        sock.close()
        latency = round((time.time() - start) * 1000, 2)
        return True, "پورت TCP باز است", latency
    except Exception as e:
        latency = round((time.time() - start) * 1000, 2)
        err = str(e).split("]")[-1] if "]" in str(e) else str(e)
        return False, f"خطا TCP: {err.strip()[:20]}", latency

def test_udp(host, port):
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3.0)
    try:
        payload = b"\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01"
        sock.sendto(payload, (host, port))
        try:
            data, _ = sock.recvfrom(512)
            sock.close()
            latency = round((time.time() - start) * 1000, 2)
            return True, f"پاسخ UDP ({len(data)} بایت)", latency
        except socket.timeout:
            sock.close()
            latency = round((time.time() - start) * 1000, 2)
            return False, "تایم‌اوت UDP (بدون پاسخ)", latency
    except Exception as e:
        sock.close()
        latency = round((time.time() - start) * 1000, 2)
        return False, f"خطا UDP: {str(e)[:20]}", latency

def parse_command(raw_text):
    text = normalize_digits(raw_text)
    duration_min = 1
    time_match = re.search(r"\(تایم\)\s*-\s*(\d+)", text)
    if time_match:
        duration_min = int(time_match.group(1))
        text = text[:time_match.start()] + text[time_match.end():]
    
    duration_min = max(1, min(duration_min, 59))
    text = re.sub(r"^/ping\s*", "", text, flags=re.IGNORECASE).strip()

    item_pattern = re.compile(r"([a-zA-Z0-9\.\_\-]+):(\d+)(?:\(([^)]+)\))?")
    matches = item_pattern.findall(text)

    targets = []
    for host, port, protos_raw in matches:
        if protos_raw:
            protos = [p.strip().lower() for p in protos_raw.split(",") if p.strip().lower() in ["http", "https", "tcp", "udp"]]
        else:
            protos = ["tcp"]
            
        if protos:
            targets.append({
                "host": host.strip(),
                "resolved_ip": resolve_host_ip(host.strip()),
                "port": int(port),
                "protocols": protos
            })

    return targets, duration_min

def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    raw_command = sys.argv[1]
    targets, duration_min = parse_command(raw_command)
    os.makedirs("ping", exist_ok=True)

    if not targets:
        with open("summary_comment.md", "w", encoding="utf-8") as f:
            f.write("⚠️ **خطای ورودی:** ساختار دستور شناخته نشد.\n\n"
                    "نمونه دستور استاندارد:\n"
                    "`/ping parspack.com:443(https,tcp),217.218.155.155:53(udp,tcp) (تایم)-1`")
        return

    runner_ip = get_public_ip()
    total_seconds = duration_min * 60
    start_time_monotonic = time.time()
    
    start_shamsi, _ = get_tehran_shamsi()
    start_time_display = start_shamsi.strftime("%H:%M:%S")

    summary = {}
    for t in targets:
        for proto in t["protocols"]:
            target_key = f"{t['host']}:{t['port']} [{proto.upper()}]"
            summary[target_key] = {
                "host": t["host"],
                "ip": t["resolved_ip"],
                "port": t["port"],
                "proto": proto.upper(),
                "success": 0,
                "fail": 0,
                "latencies": [],
                "last_msg": ""
            }

    rounds = 0
    while (time.time() - start_time_monotonic) < total_seconds:
        rounds += 1
        for t in targets:
            host = t["host"]
            port = t["port"]
            for proto in t["protocols"]:
                key = f"{host}:{port} [{proto.upper()}]"
                if proto in ["http", "https"]:
                    ok, msg, lat = test_http_https(host, port, proto)
                elif proto == "tcp":
                    ok, msg, lat = test_tcp(host, port)
                elif proto == "udp":
                    ok, msg, lat = test_udp(host, port)

                if ok:
                    summary[key]["success"] += 1
                    summary[key]["latencies"].append(lat)
                else:
                    summary[key]["fail"] += 1

                summary[key]["last_msg"] = msg

        time.sleep(max(2.0, min(5.0, len(targets) * 0.5)))

    end_time_monotonic = time.time()
    elapsed_total_seconds = int(end_time_monotonic - start_time_monotonic)
    elapsed_minutes = elapsed_total_seconds // 60
    elapsed_sec = elapsed_total_seconds % 60
    duration_str = f"{elapsed_minutes} دقیقه و {elapsed_sec} ثانیه" if elapsed_minutes > 0 else f"{elapsed_sec} ثانیه"

    end_shamsi, _ = get_tehran_shamsi()
    shamsi_timestamp = end_shamsi.strftime("%Y-%m-%d_%H-%M-%S")
    end_time_display = end_shamsi.strftime("%H:%M:%S")
    display_date = end_shamsi.strftime("%Y/%m/%d")

    filename = f"ping_{shamsi_timestamp}.txt"
    filepath = os.path.join("ping", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("╔══════════════════════════════════════════════════════════════════╗\n")
        f.write("║           📡 گزارش رسمی پایش شبکه | سامانه یوشیک پینگ            ║\n")
        f.write("╚══════════════════════════════════════════════════════════════════╝\n")
        f.write(f"🌐 آی‌پی سرور مایکروسافت: {runner_ip}\n")
        f.write(f"📅 تاریخ تست (ایران): {display_date}\n")
        f.write(f"⏱ زمان شروع: {start_time_display} | زمان پایان: {end_time_display}\n")
        f.write(f"⏳ مدت زمان دقیق کل پایش: {duration_str} ({rounds} دور کامل)\n")
        f.write("─" * 68 + "\n\n")

        for key, data in summary.items():
            total = data["success"] + data["fail"]
            avg_lat = round(sum(data["latencies"]) / len(data["latencies"]), 2) if data["latencies"] else 0
            f.write(f"🎯 هدف: {key}\n")
            f.write(f"   ├─ آی‌پی شناسایی‌شده: {data['ip']}\n")
            f.write(f"   ├─ نرخ اتصال: {data['success']}/{total} موفق\n")
            f.write(f"   ├─ میانگین تاخیر: {avg_lat} ms\n")
            f.write(f"   └─ آخرین وضعیت: {data['last_msg']}\n\n")

    repo_name = os.getenv("GITHUB_REPOSITORY", "")
    raw_file_url = f"https://github.com/{repo_name}/blob/main/{filepath}"

    with open("summary_comment.md", "w", encoding="utf-8") as f:
        f.write("### ⚡️ نتیجه ارزیابی دقیق شبکه | **Yoshik Ping v1.0**\n\n")
        f.write(f"> 🖥 **آی‌پی سرور مایکروسافت:** `{runner_ip}`  \n")
        f.write(f"> 📅 **تاریخ ارزیابی (شمسی):** `{display_date}`  \n")
        f.write(f"> 🕒 **زمان شروع:** `{start_time_display}` ➔ **زمان پایان:** `{end_time_display}` (به وقت رسمی ایران)  \n")
        f.write(f"> ⏱ **مدت زمان دقیق:** `{duration_str}` (`{rounds}` مرحله تست دوره‌ای)\n\n")
        f.write("| هدف ارزیابی | آی‌پی مقصد (Resolved IP) | پروتکل | نرخ موفقیت | میانگین Latency | وضعیت اتصال |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :--- |\n")
        
        for key, data in summary.items():
            total = data["success"] + data["fail"]
            avg_lat = f"`{round(sum(data['latencies'])/len(data['latencies']), 2)} ms`" if data["latencies"] else "`ناموفق`"
            status_badge = "🟢 پایدار" if data["success"] == total else ("🟡 نوسان" if data["success"] > 0 else "🔴 قطع")
            target_clean = f"`{data['host']}:{data['port']}`"
            ip_clean = f"`{data['ip']}`"
            f.write(f"| {target_clean} | {ip_clean} | `{data['proto']}` | `{data['success']}/{total}` | {avg_lat} | {status_badge} ({data['last_msg']}) |\n")

        f.write(f"\n---\n")
        f.write(f"📁 **آرشیو اختصاصی لاگ:** [مشاهده فایل گزارش متنی ذخیره شده]({raw_file_url})\n")

    env_file_path = os.getenv("GITHUB_ENV")
    if env_file_path:
        with open(env_file_path, "a", encoding="utf-8") as env_file:
            env_file.write(f"LOG_FILENAME={filename}\n")

if __name__ == "__main__":
    main()
