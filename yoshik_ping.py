import os
import re
import sys
import time
import socket
import urllib.request
import urllib.error
import jdatetime

def normalize_digits(text: str) -> str:
    """تبدیل اعداد فارسی و عربی به انگلیسی جهت جلوگیری از خطای پارس"""
    persian_arabic = "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩"
    english = "01234567890123456789"
    tbl = str.maketrans(persian_arabic, english)
    return text.translate(tbl)

def get_public_ip():
    """استخراج آی‌پی عمومی سرور مایکروسافت/گیت‌هاب"""
    services = ["https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com"]
    for url in services:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "YoshikPing/1.0"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                return resp.read().decode('utf-8').strip()
        except Exception:
            continue
    return "نامشخص (سرور اختصاصی)"

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
        return False, f"خطا: {err.strip()[:25]}", latency

def test_tcp(host, port):
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(4.0)
    try:
        sock.connect((host, port))
        sock.close()
        latency = round((time.time() - start) * 1000, 2)
        return True, "پورت TCP باز است", latency
    except Exception as e:
        latency = round((time.time() - start) * 1000, 2)
        err = str(e).split("]")[-1] if "]" in str(e) else str(e)
        return False, f"خطا TCP: {err.strip()[:25]}", latency

def test_udp(host, port):
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3.5)
    try:
        # پی‌لود استاندارد درخواست DNS برای تست پورت ۵۳ و عمومی
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
            return False, "تایم‌اوت UDP (پاسخی نیامد)", latency
    except Exception as e:
        sock.close()
        latency = round((time.time() - start) * 1000, 2)
        return False, f"خطا UDP: {str(e)[:25]}", latency

def parse_command(raw_text):
    text = normalize_digits(raw_text)
    
    # استخراج مدت زمان تست
    duration_min = 1
    time_match = re.search(r"\(تایم\)\s*-\s*(\d+)", text)
    if time_match:
        duration_min = int(time_match.group(1))
        text = text[:time_match.start()] + text[time_match.end():]
    
    duration_min = max(1, min(duration_min, 59))

    # حذف پیشوند /ping
    text = re.sub(r"^/ping\s*", "", text, flags=re.IGNORECASE).strip()

    # استخراج تمام آیتم‌ها با الگوی: host:port یا host:port(proto1,proto2)
    # با پشتیبانی از دامنه‌ها و آی‌پی‌ها
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
                "port": int(port),
                "protocols": protos
            })

    return targets, duration_min

def main():
    if len(sys.argv) < 2:
        print("❌ متن دستوری یافت نشد.")
        sys.exit(1)

    raw_command = sys.argv[1]
    targets, duration_min = parse_command(raw_command)

    # همیشه پوشه ping را بسازید تا خطای Git رخ ندهد
    os.makedirs("ping", exist_ok=True)

    if not targets:
        print("❌ دستور معتبر یافت نشد یا ساختار آن اشتباه است.")
        with open("summary_comment.md", "w", encoding="utf-8") as f:
            f.write("⚠️ **خطا در پارس ورودی!** هیچ تارگتی شناسایی نشد.\n\n"
                    "فرمت صحیح:\n"
                    "`/ping parspack.com:443(https,tcp),arvancloud.ir:443(tcp) (تایم)-1`")
        
        # ذخیره یک فایل خالی جهت جلوگیری از ارور اکشنز
        dummy_file = os.path.join("ping", ".gitkeep")
        with open(dummy_file, "w") as f:
            f.write("")
        return

    runner_ip = get_public_ip()
    total_seconds = duration_min * 60
    start_epoch = time.time()
    
    summary = {}
    for t in targets:
        for proto in t["protocols"]:
            key = f"{t['host']}:{t['port']} [{proto.upper()}]"
            summary[key] = {"success": 0, "fail": 0, "latencies": [], "last_msg": ""}

    rounds = 0
    print(f"🚀 آغاز تست یوشیک پینگ به مدت {duration_min} دقیقه...")
    print(f"🌐 آی‌پی رانر: {runner_ip}\n")

    while (time.time() - start_epoch) < total_seconds:
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

        time.sleep(max(2.5, min(6.0, len(targets) * 0.7)))

    now_shamsi = jdatetime.datetime.now()
    shamsi_timestamp = now_shamsi.strftime("%Y-%m-%d_%H-%M-%S")
    display_time = now_shamsi.strftime("%Y/%m/%d - %H:%M:%S")

    filename = f"ping_{shamsi_timestamp}.txt"
    filepath = os.path.join("ping", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=====================================================\n")
        f.write("📡 گزارش وضعیت شبکه - یوشیک پینگ (نسخه 1.0 بهینه)\n")
        f.write(f"🌐 آی‌پی سرور مایکروسافت: {runner_ip}\n")
        f.write(f"⏱ زمان ثبت پایانی (شمسی): {display_time}\n")
        f.write(f"⏳ مدت زمان پایش: {duration_min} دقیقه ({rounds} دور ارزیابی)\n")
        f.write("=====================================================\n\n")

        for key, data in summary.items():
            total = data["success"] + data["fail"]
            avg_lat = round(sum(data["latencies"]) / len(data["latencies"]), 2) if data["latencies"] else 0
            f.write(f"تارگت: {key}\n")
            f.write(f"  نتیجه: {data['success']}/{total} موفق | تاخیر میانگین: {avg_lat}ms\n")
            f.write(f"  آخرین پاسخ: {data['last_msg']}\n")
            f.write("-" * 50 + "\n")

    repo_name = os.getenv("GITHUB_REPOSITORY", "")
    raw_file_url = f"https://github.com/{repo_name}/blob/main/{filepath}"

    with open("summary_comment.md", "w", encoding="utf-8") as f:
        f.write("### 📊 نتایج ارزیابی شبکه | پروژه یوشیک پینگ (v1.0)\n\n")
        f.write(f"- 🌐 **آی‌پی سرور رانر مایکروسافت:** `{runner_ip}`\n")
        f.write(f"- 🕒 **زمان اتمام تست (شمسی):** `{display_time}`\n")
        f.write(f"- ⏱ **مدت زمان ارزیابی:** `{duration_min}` دقیقه ({rounds} مرحله پایش)\n\n")
        f.write("| هدف و پروتکل | نرخ موفقیت | میانگین تاخیر | آخرین وضعیت |\n")
        f.write("| :--- | :---: | :---: | :--- |\n")
        
        for key, data in summary.items():
            total = data["success"] + data["fail"]
            avg_lat = f"{round(sum(data['latencies'])/len(data['latencies']), 2)}ms" if data["latencies"] else "ناموفق"
            status_icon = "🟢" if data["success"] > data["fail"] else "🔴"
            f.write(f"| {key} | {status_icon} `{data['success']}/{total}` | `{avg_lat}` | {data['last_msg']} |\n")

        f.write(f"\n📂 **لینک مشاهده لاگ اختصاصی در مخزن:**\n[🔗 مشاهده و دانلود فایل {filename}]({raw_file_url})\n")

    # ثبت نام فایل در محیط گیت‌هاب
    env_file_path = os.getenv("GITHUB_ENV")
    if env_file_path:
        with open(env_file_path, "a", encoding="utf-8") as env_file:
            env_file.write(f"LOG_FILENAME={filename}\n")

if __name__ == "__main__":
    main()
