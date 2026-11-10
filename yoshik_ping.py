import os
import re
import sys
import time
import socket
import urllib.request
import urllib.error
import jdatetime

def get_public_ip():
    """دریافت آی‌پی خروجی سرور رانر مایکروسافت/گیت‌هاب"""
    services = [
        "https://api.ipify.org",
        "https://ifconfig.me/ip",
        "https://icanhazip.com"
    ]
    for url in services:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "YoshikPing/1.0"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                return resp.read().decode('utf-8').strip()
        except Exception:
            continue
    return "نامشخص (عدم دسترسی به سرویس آی‌پی)"

def test_http_https(host, port, proto):
    """تست اختصاصی HTTP و HTTPS به همراه کدهای پاسخ و زمان تاخیر"""
    url = f"{proto}://{host}:{port}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (YoshikPing Engine 1.0)"}
    )
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            latency = round((time.time() - start) * 1000, 2)
            return True, f"پاسخ دریافت شد (کد {response.status})", latency
    except urllib.error.HTTPError as e:
        latency = round((time.time() - start) * 1000, 2)
        # حتی خطاهای ۴۰۳/۴۰۴ نشان‌دهنده باز بودن پورت و برقراری ارتباط هستند
        return True, f"ارتباط برقرار شد (کد وضعیت: {e.code})", latency
    except Exception as e:
        latency = round((time.time() - start) * 1000, 2)
        err_msg = str(e).split("] ")[-1] if "]" in str(e) else str(e)
        return False, f"خطا: {err_msg[:30]}", latency

def test_tcp(host, port):
    """تست اتصال سوکت TCP (Handshake واقعی)"""
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5.0)
    try:
        sock.connect((host, port))
        sock.close()
        latency = round((time.time() - start) * 1000, 2)
        return True, "پورت TCP باز است (اتصال موفق)", latency
    except Exception as e:
        latency = round((time.time() - start) * 1000, 2)
        err_msg = str(e).split("] ")[-1] if "]" in str(e) else str(e)
        return False, f"خطا در TCP: {err_msg[:30]}", latency

def test_udp(host, port):
    """
    تست سوکت UDP با ارسال پی‌لود DNS/پینگ و بررسی پاسخ واقعی
    """
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(4.0)
    try:
        # پی‌لود استاندارد بایت (سازگار با DNS و پینگ‌های عمومی)
        payload = b"\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01"
        sock.sendto(payload, (host, port))
        try:
            data, _ = sock.recvfrom(512)
            sock.close()
            latency = round((time.time() - start) * 1000, 2)
            return True, f"پاسخ UDP دریافت شد ({len(data)} بایت)", latency
        except socket.timeout:
            sock.close()
            latency = round((time.time() - start) * 1000, 2)
            return False, "پاسخی دریافت نشد (Timeout)", latency
    except Exception as e:
        sock.close()
        latency = round((time.time() - start) * 1000, 2)
        return False, f"خطا در ارسال UDP: {str(e)[:30]}", latency

def parse_command(raw_text):
    """
    پارس کردن کامند ورودی:
    /ping host:port(proto1,proto2) (تایم)-دقیقه
    """
    match = re.search(r"/ping\s+(.+)", raw_text, re.IGNORECASE)
    if not match:
        return None, 1

    content = match.group(1).strip()
    
    # استخراج دقیقه
    duration_min = 1
    time_match = re.search(r"\(تایم\)-(\d+)", content)
    if time_match:
        duration_min = int(time_match.group(1))
        content = re.sub(r"\(تایم\)-\d+", "", content).strip()
    
    # محدود کردن زمان بین ۱ تا ۵۹ دقیقه جهت حفظ سلامت رانر
    duration_min = max(1, min(duration_min, 59))

    # استخراج تارگت‌ها
    targets = []
    items = [x.strip() for x in content.split(",") if x.strip()]
    
    # فرمت: host:port(protocols)
    pattern = re.compile(r"^([^:]+):(\d+)(?:\(([^)]+)\))?$")
    for item in items:
        m = pattern.match(item)
        if m:
            host = m.group(1).strip()
            port = int(m.group(2).strip())
            protos_raw = m.group(3)
            if protos_raw:
                protos = [p.strip().lower() for p in protos_raw.split(",") if p.strip().lower() in ["http", "https", "tcp", "udp"]]
            else:
                protos = ["tcp"] # پیش‌فرض در صورت عدم ذکر
            targets.append({"host": host, "port": port, "protocols": protos})

    return targets, duration_min

def main():
    if len(sys.argv) < 2:
        print("❌ متن دستوری ارسال نشده است.")
        sys.exit(1)

    raw_command = sys.argv[1]
    targets, duration_min = parse_command(raw_command)

    if not targets:
        print("❌ دستور معتبر یافت نشد یا ساختار آن اشتباه است.")
        with open("summary_comment.md", "w", encoding="utf-8") as f:
            f.write("⚠️ **خطا در پارس دستور!** ساختار وارد شده معتبر نیست.\nمثال صحیح:\n`/ping www.google.com:443(tcp,udp),217.218.155.155:53(udp) (تایم)-1`")
        sys.exit(0)

    runner_ip = get_public_ip()
    total_seconds = duration_min * 60
    start_epoch = time.time()
    
    # آماده‌سازی آرشیو نتایج
    summary_results = {}
    for t in targets:
        for proto in t["protocols"]:
            key = f"{t['host']}:{t['port']} [{proto.upper()}]"
            summary_results[key] = {"success": 0, "fail": 0, "latencies": [], "last_msg": ""}

    rounds = 0
    print(f"🚀 شروع تست اختصاصی یوشیک پینگ به مدت {duration_min} دقیقه...")
    print(f"🌐 آی‌پی سرور اجرا کننده (مایکروسافت): {runner_ip}\n")

    # لوپ هوشمند تست در بازه زمانی درخواستی
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
                    summary_results[key]["success"] += 1
                    summary_results[key]["latencies"].append(lat)
                else:
                    summary_results[key]["fail"] += 1

                summary_results[key]["last_msg"] = msg

        # فاصله هوشمند بین دورها برای جلوگیری از اسپم فایروال و بن اکانت
        time.sleep(max(2.0, min(5.0, len(targets) * 0.8)))

    # زمان پایانی به وقت شمسی
    now_shamsi = jdatetime.datetime.now()
    shamsi_timestamp = now_shamsi.strftime("%Y-%m-%d_%H-%M-%S")
    display_time = now_shamsi.strftime("%Y/%m/%d ساعت %H:%M:%S")

    # ساخت پوشه ping در صورت عدم وجود
    os.makedirs("ping", exist_ok=True)
    filename = f"ping_{shamsi_timestamp}.txt"
    filepath = os.path.join("ping", filename)

    # ایجاد فایل متنی لاگ جامع
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=====================================================\n")
        f.write("📡 گزارش وضعیت شبکه - یوشیک پینگ (نسخه 1.0)\n")
        f.write(f"🌐 آی‌پی سرور تست مایکروسافت: {runner_ip}\n")
        f.write(f"⏱ زمان ثبت نهایی (شمسی): {display_time}\n")
        f.write(f"⏳ مدت زمان ارزیابی: {duration_min} دقیقه ({rounds} دور تست)\n")
        f.write("=====================================================\n\n")

        for key, data in summary_results.items():
            total = data["success"] + data["fail"]
            avg_lat = round(sum(data["latencies"]) / len(data["latencies"]), 2) if data["latencies"] else 0
            f.write(f"تارگت: {key}\n")
            f.write(f"  وضعیت: {data['success']}/{total} موفق | میانگین تاخیر: {avg_lat}ms\n")
            f.write(f"  آخرین پاسخ: {data['last_msg']}\n")
            f.write("-" * 50 + "\n")

    # ساخت پیام مارک‌داون برای ریپلای در ایشو
    repo_name = os.getenv("GITHUB_REPOSITORY", "")
    commit_sha = os.getenv("GITHUB_SHA", "main")
    raw_file_url = f"https://github.com/{repo_name}/blob/main/{filepath}"

    with open("summary_comment.md", "w", encoding="utf-8") as f:
        f.write(f"### 📊 نتایج ارزیابی شبکه | پروژه یوشیک پینگ (v1.0)\n\n")
        f.write(f"- 🌐 **آی‌پی سرور رانر مایکروسافت:** `{runner_ip}`\n")
        f.write(f"- 🕒 **زمان اتمام تست (شمسی):** `{display_time}`\n")
        f.write(f"- ⏱ **مدت زمان پایش:** `{duration_min}` دقیقه ({rounds} مرحله پایش کامل)\n\n")
        f.write("| هدف و پروتکل | نرخ موفقیت | میانگین تاخیر | آخرین وضعیت |\n")
        f.write("| :--- | :---: | :---: | :--- |\n")
        
        for key, data in summary_results.items():
            total = data["success"] + data["fail"]
            avg_lat = f"{round(sum(data['latencies'])/len(data['latencies']), 2)}ms" if data["latencies"] else "ناموفق"
            status_icon = "🟢" if data["success"] > data["fail"] else "🔴"
            f.write(f"| {key} | {status_icon} `{data['success']}/{total}` | `{avg_lat}` | {data['last_msg']} |\n")

        f.write(f"\n📂 **مشاهده فایل لاگ کامل در مخزن:**\n[🔗 دانلود لاگ {filename}]({raw_file_url})\n")

    # اکسپورت نام فایل برای استفاده در workflow
    with open(os.environ.get("GITHUB_ENV", "env.txt"), "a", encoding="utf-8") as env_file:
        env_file.write(f"LOG_FILENAME={filename}\n")

if __name__ == "__main__":
    main()
