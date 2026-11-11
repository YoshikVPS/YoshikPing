import os
import re
import sys
import time
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

def probe_http_https(host, port, proto):
    url = f"{proto}://{host}:{port}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=3.0) as response:
            latency = round((time.time() - start) * 1000, 2)
            return True, f"پاسخ لایه ۷ (کد {response.status})", latency, "UP"
    except urllib.error.HTTPError as e:
        latency = round((time.time() - start) * 1000, 2)
        return True, f"پاسخ وب (کد {e.code})", latency, "UP"
    except Exception as e:
        latency = round((time.time() - start) * 1000, 2)
        err = str(e).lower()
        if "timed out" in err or "timeout" in err:
            return False, "تایم‌اوت (بلاک در لبه مرزی/فیلتر)", latency, "TIMEOUT"
        if "refused" in err:
            return False, "مسیر باز است اما وب‌سرور غیرفعال است", latency, "REFUSED"
        if "ssl" in err:
            return False, "عدم تطابق پروتکل SSL/TLS روی پورت", latency, "SSL_ERR"
        return False, f"خطا: {str(e)[:25]}", latency, "FAIL"

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

def probe_udp(host, port):
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
            return True, f"پاسخ سوکت UDP فعال ({len(data)}B)", latency, "UP"
        except socket.timeout:
            sock.close()
            latency = round((time.time() - start) * 1000, 2)
            return False, "تایم‌اوت UDP (پاسخی دریافت نشد)", latency, "TIMEOUT"
    except Exception as e:
        sock.close()
        latency = round((time.time() - start) * 1000, 2)
        return False, f"خطای ارسال UDP: {str(e)[:25]}", latency, "FAIL"

def parse_input_command(raw_text):
    text = normalize_digits(raw_text)
    duration_min = 1
    
    time_match = re.search(r"\(تایم\)\s*-\s*(\d+)", text)
    if time_match:
        duration_min = int(time_match.group(1))
        text = text[:time_match.start()] + text[time_match.end():]
        
    duration_min = max(1, min(duration_min, 59))
    text = re.sub(r"^/ping\s*", "", text, flags=re.IGNORECASE).strip()

    # استخراج دامنه‌ها با چند پورت و فاصله آزاد
    item_pattern = re.compile(r"([a-zA-Z0-9\.\_\-]+):([0-9\,]+)(?:\(([^)]+)\))?")
    matches = item_pattern.findall(text)

    hosts_data = {}
    for host, ports_raw, protos_raw in matches:
        host = host.strip()
        ports = [int(p.strip()) for p in ports_raw.split(",") if p.strip().isdigit()]
        if protos_raw:
            protos = [p.strip().lower() for p in protos_raw.split(",") if p.strip().lower() in ["http", "https", "tcp", "udp"]]
        else:
            protos = ["tcp"]

        if host not in hosts_data:
            hosts_data[host] = {
                "host": host,
                "ip": resolve_host_ip(host),
                "ports_map": {}
            }

        for port in ports:
            for proto in protos:
                k = f"{port} [{proto.upper()}]"
                if k not in hosts_data[host]["ports_map"]:
                    hosts_data[host]["ports_map"][k] = {
                        "port": port,
                        "proto": proto,
                        "success": 0,
                        "fail": 0,
                        "latencies": [],
                        "last_msg": "",
                        "last_code": ""
                    }

    return hosts_data, duration_min

def worker_task(task):
    host, port, proto, target_key = task["host"], task["port"], task["proto"], task["target_key"]
    if proto in ["http", "https"]:
        ok, msg, lat, code = probe_http_https(host, port, proto)
    elif proto == "tcp":
        ok, msg, lat, code = probe_tcp(host, port)
    elif proto == "udp":
        ok, msg, lat, code = probe_udp(host, port)
    else:
        ok, msg, lat, code = False, "پروتکل نامعتبر", 0, "ERR"
    return host, target_key, ok, msg, lat, code

def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    hosts_data, duration_min = parse_input_command(sys.argv[1])
    os.makedirs("ping", exist_ok=True)

    if not hosts_data:
        with open("summary_comment.md", "w", encoding="utf-8") as f:
            f.write("⚠️ **خطا در پارس ورودی!** ساختار دستور شناسایی نشد.\n\n"
                    "مثال استاندارد نسخه ۲.۰:\n"
                    "`/ping parspack.com:443,80(https,tcp) 217.218.155.155:53(udp,tcp) (تایم)-1`")
        return

    runner_ip = get_public_ip()
    total_seconds = duration_min * 60
    start_monotonic = time.time()
    start_shamsi, _ = get_tehran_shamsi()
    start_time_str = start_shamsi.strftime("%H:%M:%S")

    # ساخت صف کارهای موازی
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
    # سقف همزمانی محافظت‌شده برای جلوگیری از مصرف نامتعارف رانر
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

        # وقفه تطبیق‌پذیر پویا برای جلوگیری از پر شدن کارت شبکه و بلاک شدن رانر
        time.sleep(max(1.8, min(4.0, len(flat_tasks) * 0.35)))

    elapsed = int(time.time() - start_monotonic)
    duration_str = f"{elapsed // 60} دقیقه و {elapsed % 60} ثانیه" if (elapsed // 60) > 0 else f"{elapsed % 60} ثانیه"
    end_shamsi, _ = get_tehran_shamsi()
    end_time_str = end_shamsi.strftime("%H:%M:%S")
    display_date = end_shamsi.strftime("%Y/%m/%d")

    filename = f"ping_{end_shamsi.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    filepath = os.path.join("ping", filename)

    # ایجاد فایل گزارش آرشیو در مخزن
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"گزارش عمیق پایش شبکه v2.0 - آی‌پی سرور مایکروسافت: {runner_ip}\n")
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

    repo_name = os.getenv("GITHUB_REPOSITORY", "")
    raw_file_url = f"https://github.com/{repo_name}/blob/main/{filepath}"

    # ساخت داشبورد تحلیلی Host-Centric برای کامنت ایشو
    with open("summary_comment.md", "w", encoding="utf-8") as f:
        f.write("### ⚡️ داشبورد پایش عمیق ترافیک مرزی | **Yoshik Ping v2.0**\n\n")
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

            # تحلیل عمیق مسدودسازی IP
            all_timeout = all(p["last_code"] == "TIMEOUT" for p in ports_list if p["fail"] > 0) and total_success == 0
            has_refused = any(p["last_code"] == "REFUSED" for p in ports_list)

            if total_success == total_probes:
                ip_health_badge = "🟢 ارتباط کاملاً پایدار (مسیر ترافیک بین‌الملل بدون اختلال)"
            elif total_success > 0:
                ip_health_badge = f"🟡 دسترسی نیمه‌پایدار (پایداری کلی: {overall_pct}% | نوسان یا محدودیت پورت)"
            elif has_refused:
                ip_health_badge = "🟡 آی‌پی مسدود نیست (مسیر اینترنت به سرور رسیده اما سرویس‌ها خاموش‌اند)"
            elif all_timeout:
                ip_health_badge = "🔴 **هشدار مسدودی کامل آی‌پی (IP Blackhole / فیلتر در لبه مرزی یا روتینگ قطع است)**"
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

                if pct == 100:
                    badge = f"🟢 `{pct}%`"
                elif pct > 0:
                    badge = f"🟡 `{pct}%`"
                else:
                    badge = f"🔴 `{pct}%`"

                f.write(f"| `{tkey}` | `{pdata['success']}/{tot}` | {badge} | {avg_lat} | {pdata['last_msg']} |\n")

            f.write("\n---\n")

        f.write(f"📁 **آرشیو اختصاصی لاگ:** [مشاهده گزارش متنی در مخزن]({raw_file_url})\n")

    env_path = os.getenv("GITHUB_ENV")
    if env_path:
        with open(env_path, "a", encoding="utf-8") as env_file:
            env_file.write(f"LOG_FILENAME={filename}\n")

if __name__ == "__main__":
    main()
