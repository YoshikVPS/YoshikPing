<div align="center">

<img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="230" style="border-radius: 22px; box-shadow: 0 12px 35px rgba(0,0,0,0.65);" alt="Yoshik Ping Official Logo" />

<br/><br/>

# <img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="36" style="vertical-align: middle; border-radius: 6px;" /> یوشیک پینگ نسخه ۴.۰ &nbsp;|&nbsp; 🇬🇧 Yoshik Ping Engine `v4.0`

### سامانه ابری پایش عمیق ترافیک مرزی، اسکنر ریزالور و تانل DNS، و ماتریس لایه‌های وب

**Serverless Cross-Border Deep Telemetry, DNS Tunnel Sentinel & Modern Web Matrix (H1/H2/H3)**

[![Engine Status](https://img.shields.io/badge/Engine-Active%20%7C%20v4.0%20Quantum-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://github.com/YoshikVPS/YoshikPing/actions)
[![Language](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![QUIC Ready](https://img.shields.io/badge/HTTP%2F3-QUIC%20Enabled-8A2BE2?style=for-the-badge&logo=cloudflare&logoColor=white)](#-ماتریس-فنی-تحلیل-پروتکل‌ها-و-سوکت‌ها)
[![Telegram Channel](https://img.shields.io/badge/Telegram-YoshikVPS-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/YoshikVPS)
[![Releases Archive](https://img.shields.io/badge/Source-Download%20ZIP-2ea44f?style=for-the-badge&logo=github&logoColor=white)](https://github.com/YoshikVPS/YoshikPing/releases)

<br/>

[![1-Click Fork](https://img.shields.io/badge/⚡️_پورت_سریع_مخزن-Fork_Repository-orange?style=for-the-badge&logo=git&logoColor=white)](https://github.com/YoshikVPS/YoshikPing/fork)
[![Open Issue](https://img.shields.io/badge/💬_داشبورد_اجرایی-Run_Diagnostics-blueviolet?style=for-the-badge&logo=github)](https://github.com/YoshikVPS/YoshikPing/issues/new)
[![Download Latest ZIP](https://img.shields.io/badge/📦_دانلود_مستقیم_فایل_زیپ-Latest_ZIP-success?style=for-the-badge&logo=files&logoColor=white)](https://github.com/YoshikVPS/YoshikPing/releases/latest)

<br/>

**<a href="#persian-docs">📖 مطالعه مستندات جامع مهندسی فارسی و سناریوهای شبکه</a>** &nbsp; | &nbsp; **<a href="#english-docs">🇬🇧 Jump to English Documentation</a>**

</div>

---

<a id="persian-docs"></a>

# <img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="32" style="vertical-align: middle; border-radius: 5px;" /> مستندات تخصصی فارسی | سامانه یوشیک پینگ ۴.۰

### <img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="22" style="vertical-align: middle;" /> این پروژه دقیقاً چطور کار می‌کند؟ (نمای سه‌بعدی از بیرون مرز به داخل)

```mermaid
flowchart TD
    A["🧑‍💻 شما در ایران<br/>یک کامنت در Issue می‌نویسید"] -->|"GitHub Webhook"| B["⚙️ GitHub Actions<br/>Workflow فعال می‌شود"]
    B --> C["☁️ رانر ابری Microsoft Azure<br/>(خارج از کشور)<br/>Yoshik Ping Engine v4.0"]
    C --> D1["🔌 موتور /ping تا ۱۰۰۰ تارگت<br/>TCP - UDP - H1 - H2 - H3 QUIC"]
    C --> D2["🛡 موتور /dns اسکنر ریزالور<br/>تست پورت ۵۳ + عبور پکت تانل"]
    D1 --> E["🌍 مسیر بین‌المللی<br/>از رانر خارجی به سمت مرز ایران"]
    D2 --> E
    E --> F["🎯 مقصد شما<br/>سرور - دامنه - ریزالور - پورت"]
    F -->|"پاسخ یا تایم‌اوت"| G["📊 تحلیل و خروجی<br/>UP / DOWN / Tunnel Ready"]
    G --> H1["💬 کامنت همان Issue<br/>با لینک مستقیم و مشخصات"]
    G --> H2["📲 کانال تلگرام<br/>کادر بازشونده + فایل پیوست"]
    G --> H3["🗂 آرشیو در مخزن<br/>پوشه‌های ping و dns"]
    H1 --> I["✅ پایش کامل ترافیک مرزی<br/>بدون نیاز به سرور خارجی"]
    H2 --> I
    H3 --> I

    style A fill:#1f2937,stroke:#60a5fa,stroke-width:2px,color:#fff
    style B fill:#312e81,stroke:#818cf8,stroke-width:2px,color:#fff
    style C fill:#0c4a6e,stroke:#38bdf8,stroke-width:3px,color:#fff
    style D1 fill:#7c2d12,stroke:#fb923c,stroke-width:2px,color:#fff
    style D2 fill:#065f46,stroke:#34d399,stroke-width:2px,color:#fff
    style E fill:#78350f,stroke:#fbbf24,stroke-width:2px,color:#fff
    style F fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#fff
    style G fill:#1e3a8a,stroke:#60a5fa,stroke-width:2px,color:#fff
    style H1 fill:#134e4a,stroke:#2dd4bf,stroke-width:2px,color:#fff
    style H2 fill:#1e40af,stroke:#3b82f6,stroke-width:2px,color:#fff
    style H3 fill:#3730a3,stroke:#818cf8,stroke-width:2px,color:#fff
    style I fill:#14532d,stroke:#4ade80,stroke-width:3px,color:#fff
```

---

### <img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="22" style="vertical-align: middle;" /> قابلیت‌های جدید در نسخه ۴.۰

1. **موتور تست ریزالور و تانل DNS (`/dns`):**
   - تست موازی و ایمن لیست‌های طولانی آی‌پی روی پورت ۵۳ (`udp` و `tcp`) با الهام از ساختار **WhiteDNS / CottenDNS**.
   - بررسی واقعی بودن ریزالور و تست عبور پکت‌های ساب‌دامین/تانل.
   - تخمین زمان اتمام اسکن در شروع کار و ذخیره ریزالورهای سالم در پوشه جداگانه `dns/` با تاریخ شمسی.
2. **ارتقای موتور `/ping` به مقیاس ۱۰۰۰ تارگت:**
   - بهینه‌سازی همزمانی برای تست روان تا ۱۰۰۰ دامنه و آی‌پی همزمان.
   - استفاده از **نقل‌قول بازشونده تلگرام (`Expandable Blockquote`)** برای نمایش تمیز گزارش‌های طولانی و ارسال خودکار فایل `.txt` در صورت عبور از سقف ۴۰۹۶ کاراکتر.
   - نمایش ثابت IP عمومی رانر اکشنز در خروجی هر دو موتور.

---

### <img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="22" style="vertical-align: middle;" /> دستورات کاربردی در ایشیو (ChatOps v4.0)

تمامی دستورات در بخش کامنت‌های **Issue** مخزن ثبت می‌شوند:

#### حالت ۱: پایش عمیق لایه ۴ و ۷ شبکه (`/ping`)

پایش همزمان تا ۱۰۰۰ تارگت، نمایش IP رانر، ذخیره در `ping/` و ارسال گزارش فشرده به کانال تلگرام:

```text
/ping arvancloud.ir:443(https) cloudflare.com:443(https:h3,udp) 1.1.1.1:53(udp) (تایم)-1 @YoshikVPSBOT
```

*(برای خروجی خالص IPهای سالم، فلگ `-txt` را اضافه کنید: `(تایم)-1-txt`)*.

#### حالت ۲: اسکن ریزالور و تانل DNS (`/dns`)

تست موازی لیست ریزالورها روی پورت ۵۳ (`udp`، `tcp` یا هر دو) و ذخیره سالم‌ها در پوشه `dns/`:

```text
/dns 1.1.1.1:53(udp,tcp) 8.8.8.8:53(udp) -txt @YoshikVPSBOT
```

*(اگر `@YoshikVPSBOT` را نگذارید، اسکن انجام و در مخزن ذخیره می‌شود اما در کانال منتشر نمی‌شود).*

#### حالت ۳: بایگانی هوشمند سورس پروژه (`بایگانی`)

بسته‌بندی فایل‌های اصلی در قالب ZIP، ثبت در بخش Releases با تگ `v4.0`، جلوگیری از نسخه تکراری و اطلاع‌رسانی در تلگرام:

```text
بایگانی-@YoshikVPSBOT
```

#### حالت ۴: پاک‌سازی سوابق و پوشه‌های لاگ

- تخلیه تاریخچه تب Actions: **`اکشنز-پاک`**
- حذف دو مرحله‌ای پوشه‌های `ping/` و `dns/`: **`پاکسازی`**

---

### <img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="22" style="vertical-align: middle;" /> ماتریس فنی تحلیل پروتکل‌ها و سوکت‌ها

| پروتکل         | لایه شبکه | شیوه راستی‌آزمایی سوکت                                       | وضعیت سالم (UP)                                | ماهیت خطا و مسدودی (DOWN)                 |
| :------------: | :-------: | :----------------------------------------------------------- | :--------------------------------------------- | :---------------------------------------- |
| **`TCP`**      | لایه ۴    | هندشیک کامل سیستم‌عامل (`SYN ➔ SYN/ACK ➔ ACK`)               | برقراری سوکت زیر ۲.۸ ثانیه                     | بسته بودن پورت / دراپ پکت در فایروال مرزی |
| **`UDP`**      | لایه ۴    | ارسال پکت تعاملی دیتگرام و تحلیل پاسخ / عدم دریافت خطای پورت | دریافت دیتاگرام بازگشتی یا عدم وجود Unreachable | تایم‌اوت سوکت / مسدودی کامل پروتکل UDP    |
| **`DNS`**      | لایه ۷/۴  | ارسال کوئری استاندارد + کوئری تصادفی ساب‌دامین تانل          | پاسخ معتبر `RCODE=0` و عبور پکت تانل           | تایم‌اوت / هایجک / مسدودی ساب‌دامین       |
| **`HTTP/1.1`** | لایه ۷    | درخواست وب استاندارد با متد GET به همراه هدر                 | دریافت پاسخ معتبر با کدهای استاندارد           | دراپ اتصال در لبه / خطای سرور             |
| **`HTTP/2`**   | لایه ۷    | هندشیک TLS 1.3 به همراه مذاکره ALPN پروتکل `h2`              | موفقیت مذاکره مالتی‌پلکسینگ                    | عدم پشتیبانی از H2 / فیلتر هندشیک امن     |
| **`HTTP/3`**   | لایه ۷    | ارسال پکت اولیه QUIC Initial بر بستر UDP دیتگرام             | دریافت ریسپانس معتبر پروتکل QUIC               | دراپ ترافیک QUIC در فایروال لبه مرزی      |

---

### <img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="22" style="vertical-align: middle;" /> آموزش گام‌به‌گام راه‌اندازی روی مخزن شخصی

1. **Fork کردن مخزن:** روی گزینه Fork در بالای صفحه کلیک کنید.
2. **فعال‌سازی دسترسی‌های ورک‌فلو:** در مسیر **Settings ➔ Actions ➔ General** بخش **Workflow permissions** گزینه **Read and write permissions** را انتخاب و **Save** کنید.
3. **ثبت متغیرهای محرمانه (Secrets):** در مسیر **Settings ➔ Secrets and variables ➔ Actions** موارد زیر را ثبت کنید:
   - `ADMIN_USERNAME`: نام کاربری گیت‌هاب شما.
   - `TELEGRAM_BOT_TOKEN`: توکن بات تلگرام (اختیاری).
   - `TELEGRAM_CHANNEL_ID`: آیدی کانال تلگرام همراه با `@` (مثال: `@YoshikVPS`).
4. **شروع کار:** در تب **Issues** یک Issue باز کرده و دستورات بالا را ارسال کنید.

---

<a id="english-docs"></a>

# 🇬🇧 English Technical Documentation

An enterprise-grade, serverless cross-border network telemetry sentinel deployed on Microsoft Azure runner infrastructure via GitHub Actions ChatOps.

## 🚀 Key Capabilities in Version 4.0

- **High-Scale Web & L4 Matrix (`/ping`):** Supports up to 1000+ concurrent targets across TCP, UDP, HTTP/1.1, HTTP/2 ALPN, and HTTP/3 QUIC.
- **DNS Resolver & Tunneling Sentinel (`/dns`):** Parallel UDP/TCP port 53 validation and tunneling packet reachability checks (inspired by WhiteDNS/CottenDNS), archived in `dns/`.
- **Telegram HTML & Expandable Blockquotes:** Clean collapsible reports with automatic `.txt` document attachment for large outputs.
- **Smart Release Archiver (`بایگانی`) & History Purger (`اکشنز-پاک`).**

---

```text
================================================================================
           📡 YOSHIK VPS NETWORK ENGINEERING & CLOUD TELEMETRY LAB
================================================================================
```

| 👨‍💻 System Architect                          | 🌐 Organization             | 🛡 Core License      | ⚡️ Engine Status       |
| :-------------------------------------------: | :------------------------: | :-----------------: | :--------------------: |
| [**YoshikVPS**](https://github.com/YoshikVPS) | **Yoshik VPS Network Lab** | **MIT Open Source** | **v4.0 Quantum Ready** |
