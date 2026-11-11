<div align="center">

<img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="230" style="border-radius: 22px; box-shadow: 0 12px 35px rgba(0,0,0,0.65);" alt="Yoshik Ping Official Logo" />

<br/><br/>

# <img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="36" style="vertical-align: middle; border-radius: 6px;" /> یوشیک پینگ نسخه ۳.۰ &nbsp;|&nbsp; 🇬🇧 Yoshik Ping Engine `v3.0`

### سامانه ابری پایش عمیق ترافیک مرزی، ماتریس لایه‌های وب (HTTP/3 QUIC) و دیده‌بان اختلالات

**Serverless Cross-Border Deep Telemetry, Modern Web Matrix (H1/H2/H3) & Anti-Filter Sentinel**

[![Engine Status](https://img.shields.io/badge/Engine-Active%20%7C%20v3.0%20Titanium-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://github.com/YoshikVPS/YoshikPing/actions)
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

# <img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="32" style="vertical-align: middle; border-radius: 5px;" /> مستندات تخصصی فارسی | سامانه یوشیک پینگ ۳.۰

### <img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="22" style="vertical-align: middle;" /> این پروژه دقیقاً چطور کار می‌کند؟ (نمای سه‌بعدی)

```text
                                   ☁️  GitHub Cloud (Microsoft Azure Runner)
                                   ┌──────────────────────────────────────┐
                                   │  🤖  Yoshik Ping Engine  v3.0        │
                                   │  ┌────────────┐  ┌────────────────┐  │
                                   │  │ L4 Probe   │  │ L7 Web Matrix  │  │
                                   │  │ TCP / UDP  │  │ H1 / H2 / H3   │  │
                                   │  └─────┬──────┘  └───────┬────────┘  │
                                   └────────┼─────────────────┼───────────┘
                                            │                 │
                      ┌─────────────────────┘                 └─────────────────────┐
                      │                                                             │
                      ▼                                                             ▼
        ┌───────────────────────────┐                             ┌───────────────────────────┐
        │  🛰  خروجی به سمت مقصد     │                             │  📡  گزارش تحلیلی          │
        │  (سرور / دامنه / IP شما)   │                             │  📲 کانال تلگرام           │
        │  TCP · UDP · HTTPS H1/H2/H3│                             │  💬 کامنت همان Issue      │
        └───────────────────────────┘                             └───────────────────────────┘

        ┌─────────────────────────────────────────────────────────────────────────────────┐
        │  ۱. شما یک کامنت در Issue می‌نویسید  →  ۲. ورک‌فلو GitHub Actions فعال می‌شود     │
        │  ۳. رانر ابری (خارج از کشور) تست L4/L7 را انجام می‌دهد  →  ۴. نتیجه تحلیل می‌شود  │
        │  ۵. خروجی در Issue و تلگرام تحویل داده می‌شود                                     │
        └─────────────────────────────────────────────────────────────────────────────────┘
```

**به زبان ساده:** شما از داخل ایران فقط یک کامنت در Issue مخزن می‌گذارید. این کامنت، یک ربات را روی سرورهای ابری مایکروسافت (خارج از کشور) بیدار می‌کند. آن ربات از آن‌جا به دامنه/سرور/IP شما وصل می‌شود و می‌سنجد که آیا ترافیک از مرز رد می‌شود یا نه — روی پورت‌های TCP، بسته‌های UDP، و لایه‌های وب HTTP/1.1، HTTP/2 و HTTP/3 (QUIC). نتیجه را هم همان‌جا در Issue و هم در کانال تلگرام تحویل می‌گیرید. یعنی **بدون نیاز به سرور شخصی**، از بیرون مرزها وضعیت شبکه‌تان را می‌بینید.

---

### <img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="22" style="vertical-align: middle;" /> فلسفه فنی و رسالت پروژه در شرایط اختلال اینترنت بین‌الملل

در شرایطی که دسترسی آزاد به شبکه دچار اختلالات عمیق می‌شود یا پدیده‌هایی نظیر **سیاه‌چاله ترافیک بین‌الملل (IP Blackhole)**، فیلترینگ هوشمند لایه پروتکل (DPI)، یا اختلال عمدی بر روی بسته‌های **UDP و پروتکل QUIC** اعمال می‌گردد، مدیران شبکه و توسعه‌دهندگان همواره با این سوالات حیاتی روبرو هستند:

1. **آیا سرور و دیتاسنتر داخلی هنوز از مرزهای بین‌المللی ترافیک زنده دریافت می‌کند؟**
2. **آیا کل آی‌پی در لبه ورودی کشور دراپ شده یا تنها پورت‌های وب مسدود هستند؟**
3. **آیا وب‌سرور روی HTTP/2 و پروتکل مدرن HTTP/3 (QUIC) پاسخگوست یا ارتباط روی پروتکل‌های مدرن دراپ می‌شود؟**

از آنجا که دسترسی به بستر **GitHub** معمولاً پایدار می‌ماند، سامانه **یوشیک پینگ ۳.۰ (Yoshik Ping v3.0)** به صورت بدون سرور (Serverless) بر بستر رانرهای ابری مایکروسافت خارج از کشور اجرا می‌شود. شما از طریق ثبت یک کامنت ساده در بخش Issues مخزن، آزمون‌های همزمان لایه ۴ و ۷ را شلیک کرده و خروجی تحلیلی را در همان صفحه یا در کانال تلگرام تحویل می‌گیرید.

---

### <img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="22" style="vertical-align: middle;" /> پنج حالت عملیاتی و دستورات کاربردی در ایشیو (ChatOps v3.0)

تمامی دستورات در بخش کامنت‌های **Issue** مخزن ثبت می‌شوند:

#### حالت ۱: ارزیابی کامل ۳ لایه وب + UDP + انتشار رسمی در کانال تلگرام

پایش خودکار هر ۳ لایه وب (HTTP/1.1, HTTP/2, HTTP/3 QUIC) روی پورت ۴۴۳، بررسی سوکت UDP، ارسال تحلیل با کلاس مهندسی به کانال تلگرام و دریافت لینک مستقیم پست در کامنت ایشیو:

```text
/ping arvancloud.ir:443(https) cloudflare.com:443(https:h3,udp) 1.1.1.1:53(udp) (تایم)-1 @YoshikVPSBOT
```

#### حالت ۲: ارزیابی تفکیکی نسخه‌های وب با تبدیل خودکار خطا

آزمون همزمان چند پورت و تفکیک لایه‌ها (سیستم به طور خودکار اشتباه نگارشی `http:h3` را به ارتباط امن `https:h3` ارتقا می‌دهد):

```text
/ping parspack.com:443,80(https:h1,tcp) google.com:443(http:h3,tcp) (تایم)-2
```

#### حالت ۳: تست سریع و برخط لایه ۴ و پروتکل QUIC (بدون تگ زمان)

اجرای آزمون در مدت زمان پیش‌فرض ۱ دقیقه برای ارزیابی پایداری پورت‌های امن بدون انتشار عمومی:

```text
/ping 1.1.1.1:53(udp) cloudflare.com:443(https:h3,tcp)
```

#### حالت ۴: بایگانی هوشمند سورس پروژه و ساخت Release رسمی

بسته‌بندی فایل‌های اصلی سورس در قالب فایل ZIP، ثبت در بخش Releases، جلوگیری هوشمند از ایجاد نسخه تکراری در صورت عدم تغییر سورس، و ارسال اطلاعیه به تلگرام:

```text
بایگانی-@YoshikVPSBOT
```

(برای بایگانی بدون ارسال پیام به تلگرام، فقط کلمه `بایگانی` را ارسال کنید).

#### حالت ۵: پاک‌سازی آنی و صفر کردن سوابق تب Actions

تخلیه کامل تاریخچه اجراهای قبلی در تب Actions از طریق API گیت‌هاب جهت حفظ نظم و تمیزی داشبورد مخزن:

```text
اکشنز-پاک
```

(برای تخلیه فایل‌های لاگ فیزیکی داخل پوشه `ping/` از کلمه `پاکسازی` استفاده کنید).

---

### <img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="22" style="vertical-align: middle;" /> ماتریس فنی تحلیل پروتکل‌ها و سوکت‌ها

| پروتکل         | لایه شبکه | شیوه راستی‌آزمایی سوکت                                       | وضعیت سالم (UP)                                | ماهیت خطا و مسدودی (DOWN)                 |
| :------------: | :-------: | :----------------------------------------------------------- | :--------------------------------------------- | :---------------------------------------- |
| **`TCP`**      | لایه ۴    | هندشیک کامل سیستم‌عامل (`SYN ➔ SYN/ACK ➔ ACK`)               | برقراری سوکت زیر ۲.۸ ثانیه                     | بسته بودن پورت / دراپ پکت در فایروال مرزی |
| **`UDP`**      | لایه ۴    | ارسال پکت تعاملی دیتگرام و تحلیل پاسخ / عدم دریافت خطای پورت | دریافت دیتگرام بازگشتی یا عدم وجود Unreachable | تایم‌اوت سوکت / مسدودی کامل پروتکل UDP    |
| **`HTTP/1.1`** | لایه ۷    | درخواست وب استاندارد با متد GET به همراه هدر                 | دریافت پاسخ معتبر با کدهای استاندارد           | دراپ اتصال در لبه / خطای سرور             |
| **`HTTP/2`**   | لایه ۷    | هندشیک TLS 1.3 به همراه مذاکره ALPN پروتکل `h2`              | موفقیت مذاکره مالتی‌پلکسینگ                    | عدم پشتیبانی از H2 / فیلتر هندشیک امن     |
| **`HTTP/3`**   | لایه ۷    | ارسال پکت اولیه QUIC Initial بر بستر UDP دیتگرام             | دریافت ریسپانس معتبر پروتکل QUIC               | دراپ ترافیک QUIC در فایروال لبه مرزی      |

> **📌 نکته:** برای تعیین لایه در دستور، از علامت دونقطه (`:`) بعد از نام پروتکل وب استفاده می‌کنی:
>
> ```text
> https:h1
> https:h2
> https:h3
> ```

---

### <img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="22" style="vertical-align: middle;" /> آموزش گام‌به‌گام راه‌اندازی روی مخزن شخصی

برای پیاده‌سازی این سیستم روی اکانت گیت‌هاب شخصی خودتان مراحل زیر را طی کنید:

1. **پورت (Fork) کردن مخزن:** روی گزینه Fork در بالای صفحه کلیک کنید تا یک کپی از مخزن در اکانت شما ایجاد شود.
2. **فعال‌سازی دسترسی‌های ورک‌فلو:** در مخزن شخصی خود وارد مسیر **Settings ➔ Actions ➔ General** شوید. به انتهای صفحه بروید و در بخش **Workflow permissions** گزینه **Read and write permissions** را انتخاب کرده و دکمه **Save** را بزنید.
3. **ثبت متغیرهای محرمانه (Secrets):** به مسیر **Settings ➔ Secrets and variables ➔ Actions** رفته و با زدن دکمه **New repository secret** متغیرهای زیر را ثبت کنید:
   - `ADMIN_USERNAME`: نام کاربری گیت‌هاب شما (جهت جلوگیری از اجرای دستورات توسط غریبه‌ها).
   - `TELEGRAM_BOT_TOKEN`: توکن بات تلگرام دریافت شده از BotFather (اختیاری - جهت ارسال گزارش به کانال).
   - `TELEGRAM_CHANNEL_ID`: آیدی عمومی یا عددی کانال تلگرام به همراه علامت @ (مثال: `@YoshikVPS`).
4. **شروع کار:** وارد تب Issues مخزن خود شوید، یک Issue جدید باز کنید یا داخل ایشیو قبلی یکی از دستورات ۵ گانه بالا را ارسال نمایید.

---

### <img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="22" style="vertical-align: middle;" /> دسترسی به فایل‌های زیپ، سورس‌ها و نسخه‌ها

تمامی پکیج‌ها و کدهای کامپایل‌شده پروژه به طور مستقیم از طریق گیت‌هاب قابل دریافت هستند:

- 📦 [دانلود مستقیم آخرین فایل زیپ سورس پروژه (Latest ZIP)](https://github.com/YoshikVPS/YoshikPing/releases/latest)
- 📑 [مشاهده لیست تمام نسخه‌ها، تگ‌ها و لاگ تغییرات (Releases Archive)](https://github.com/YoshikVPS/YoshikPing/releases)
- 🗂 [پوشه آرشیو لاگ‌های متنی خام در مخزن](https://github.com/YoshikVPS/YoshikPing/tree/main/ping)

---

<a id="english-docs"></a>

# 🇬🇧 English Technical Documentation

An enterprise-grade, serverless cross-border network telemetry sentinel deployed on Microsoft Azure runner infrastructure via GitHub Actions ChatOps. Built to provide precise Layer 4 to Layer 7 diagnostic telemetry, packet reachability validation, ALPN handshakes, and UDP/QUIC availability metrics.

## 🚀 Key Capabilities in Version 3.0

- **Unified Web Matrix:** Native validation for HTTP/1.1, HTTP/2 ALPN negotiation, and HTTP/3 QUIC Initial over UDP.
- **Telegram NOC Telemetry Integration:** Dispatches structured, engineering-grade NOC performance logs directly to Telegram with link callbacks inside Issues.
- **Smart Release Archiver (بایگانی):** Self-executing source packaging into GitHub Releases with deduplication mechanics.
- **Instant Action Cleaner (اکشنز-پاک):** High-speed GitHub Actions history purger via Octokit API.

## 🛡 Security & GitHub Policy Compliance

> [!NOTE]
> **Notice for GitHub Trust & Safety and Policy Automation:**

- **Zero-Abuse Architecture:** Strictly an authorized uptime telemetry engine. It does NOT conduct mass port scanning or denial-of-service traffic.
- **Targeted Diagnostics:** Probes are triggered solely against endpoints provided by the authenticated administrator (`ADMIN_USERNAME`).
- **Rate Limiting:** Enforces strict intervals (`time.sleep 1.8s to 4.0s`) to safeguard runner network cards.
- **Resource Throttling:** Operates strictly on-demand via comment webhooks and terminates immediately after execution. Fully compliant with GitHub Acceptable Use Policies.

---

```text
================================================================================
           📡 YOSHIK VPS NETWORK ENGINEERING & CLOUD TELEMETRY LAB
================================================================================
```

| 👨‍💻 System Architect                          | 🌐 Organization             | 🛡 Core License      | ⚡️ Engine Status        |
| :-------------------------------------------: | :------------------------: | :-----------------: | :---------------------: |
| [**YoshikVPS**](https://github.com/YoshikVPS) | **Yoshik VPS Network Lab** | **MIT Open Source** | **v3.0 Titanium Ready** |

**Follow [YoshikVPS](https://github.com/YoshikVPS)** • **Star this Repo**

*Engineered with precision • Serverless GitHub Actions Core • Tehran Time Synced*
