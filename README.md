<div align="center">

<img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="230" style="border-radius: 22px; box-shadow: 0 12px 35px rgba(0,0,0,0.65);" alt="Yoshik Ping Official Logo" />

<br/><br/>

# <img src="https://raw.githubusercontent.com/YoshikVPS/YoshikPing/main/photo_2026-02-07_07-40-29.jpg" width="36" style="vertical-align: middle; border-radius: 6px;" /> یوشیک پینگ نسخه ۳.۰ &nbsp;|&nbsp; 🇬🇧 Yoshik Ping Engine `v3.0`
### سامانه ابری پایش عمیق ترافیک مرزی، لایه‌های وب (HTTP/3 QUIC) و رادار تحریم
**Serverless Cross-Border Deep Telemetry, Web Layer Matrix (H1/H2/H3) & Anti-Filter Sentinel**

[![Engine Status](https://img.shields.io/badge/Engine-Active%20%7C%20v3.0%20Titanium-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://github.com/YoshikVPS/YoshikPing/actions)
[![Language](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![QUIC Ready](https://img.shields.io/badge/HTTP%2F3-QUIC%20Enabled-8A2BE2?style=for-the-badge&logo=cloudflare&logoColor=white)](#technical-matrix)
[![Telegram Alerts](https://img.shields.io/badge/Telegram-Broadcast%20Ready-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/YoshikVPS)
[![AUP Policy](https://img.shields.io/badge/GitHub%20Policy-100%25%20AUP%20Safe-success?style=for-the-badge&logo=checkmarx&logoColor=white)](#compliance)

<br/>

[![1-Click Fork](https://img.shields.io/badge/⚡️_1--Click_Deploy-Fork_Repository-orange?style=for-the-badge&logo=git&logoColor=white)](https://github.com/YoshikVPS/YoshikPing/fork)
[![Open Issue](https://img.shields.io/badge/💬_ChatOps-Run_Diagnostics-blueviolet?style=for-the-badge&logo=github)](https://github.com/YoshikVPS/YoshikPing/issues/new)

<br/>

**<a href="#persian-docs">📖 مطالعه مستندات جامع مهندسی فارسی (سناریوی اینترنت ملی)</a>** &nbsp; | &nbsp; **<a href="#english-docs">🇬🇧 Jump to English Documentation</a>**

</div>

---

<a id="english-docs"></a>

# 🇬🇧 English Technical Documentation

An enterprise-grade, on-demand network telemetry and censorship detection engine powered by Microsoft Azure runner nodes via GitHub Actions ChatOps. Designed to diagnose real-world connectivity, L4-L7 packet degradation, ALPN handshakes, and UDP/QUIC accessibility into isolated regions without a dedicated server.

---

### 🚀 Breakthrough Features in Version 3.0

* **Web Protocol Matrix (HTTP/1.1, HTTP/2, HTTP/3 QUIC):** Evaluate modern web protocols natively. Probes QUIC initial packets over UDP alongside TLS 1.3 ALPN negotiations.
* **Smart Auto-Correction:** Intelligently corrects contradictory syntax (e.g., auto-elevating `http:h3` to encrypted `https:h3`).
* **Zero-Trace Telegram NOC Dispatch:** Publishes high-density NOC telemetry to Telegram channels (`@YoshikVPS`) while cleanly extracting message IDs back into GitHub Issue comments without polluting repository logs.
* **Smart Self-Snapshotted Release Engine (`بایگانی`):** Automatically packages core sources into GitHub Releases. Prevents redundant releases if codebase commit hashes remain identical.
* **Instant Action Cleaner (`اکشنز-پاک`):** One-shot pruning API that flushes past workflow execution history to keep your repository dashboard pristine.

---

### 🕹 ChatOps Command Reference (v3.0)

Submit commands inside repository **Issues**:

#### 1. Advanced Multi-Layer Telemetry
```text
/ping arvancloud.ir:443(https) cloudflare.com:443(https:h3,udp) parspack.com:443,80(https:h1,tcp) (تایم)-2 @YoshikVPSBOT

  - (https): Defaults to concurrently probing all 3 web layers (HTTP/1.1,
    HTTP/2, HTTP/3).
  - (https:h3): Exclusively tests HTTP/3 QUIC Initial over UDP.
  - (تایم)-<N>: Sets duration loop from 1 to 59 minutes.
  - @YoshikVPSBOT: Triggers Telegram NOC dispatch and captures direct post links
    into the Issue.

2. Source Code Snapshot & Release

بایگانی-@YoshikVPSBOT

  - Packages source files into a ZIP release, creates a tag, and broadcasts
    download links to Telegram.

3. Actions History Pruning

اکشنز-پاک

  - Purges previous workflow execution runs through GitHub API to maintain zero
    clutter.

4. Disk Log Purge

پاکسازی

  - Interactive 2-step purge of the physical ping/ archive directory.

🔬 Technical Inspection Matrix

| Protocol       | OSI Layer | Socket Verification Method                            | Success State (UP)               | Failure Signature (DOWN)            |
| :------------: | :-------: | :---------------------------------------------------- | :------------------------------- | :---------------------------------- |
| **`TCP`**      | L4        | OS Full 3-Way Handshake (`SYN ➔ SYN/ACK ➔ ACK`)       | Established connection `< 2.8s`  | Connection Refused / Dropped        |
| **`UDP`**      | L4        | Interactive Datagram socket + DNS / Unreachable Probe | Datagram echo or Open Unfiltered | Datagram socket timeout / Filtered  |
| **`HTTP/1.1`** | L7        | Clear-text or TLS GET Request                         | Status 200-499 processed         | Protocol mismatch / Connection Drop |
| **`HTTP/2`**   | L7        | TLS 1.3 Handshake + ALPN Negotiation (`h2`)           | ALPN successfully negotiated     | ALPN fallback / SSL Handshake Error |
| **`HTTP/3`**   | L7/QUIC   | UDP QUIC Initial Packet Injection                     | Active QUIC Handshake return     | Datagram timeout (QUIC blocked)     |

🛡 Security & GitHub Policy Compliance

[!NOTE] Notice for GitHub Trust & Safety and Policy Automation:

  - Zero-Abuse Architecture: Strictly an authorized uptime telemetry engine. It
    does NOT conduct mass port scanning or denial-of-service traffic.
  - Targeted Diagnostics: Probes are triggered solely against endpoints provided
    by the authenticated administrator (ADMIN_USERNAME).
  - Rate Limiting: Enforces strict intervals (time.sleep 1.8s to 4.0s) to
    safeguard runner network cards.
  - Resource Throttling: Operates strictly on-demand via comment webhooks and
    terminates immediately after execution. Fully compliant with GitHub
    Acceptable Use Policies.

 مستندات مهندسی فارسی | یوشیک پینگ نسخه ۳.۰

 فلسفه مهندسی: دیده‌بان ترافیک در شرایط اختلال اینترنت ملی و مسدودی‌های نوین

در سناریوهای بحرانی که دسترسی ترافیک بین‌الملل به داخل کشور محدود شده یا وضعیت
شبکه به سمت سیاه‌چاله اینترنت ملی (National Intranet Isolation) سوق پیدا می‌کند،
بزرگ‌ترین دغدغه مهندسین زیرساخت این است:

«آیا ترافیک UDP و QUIC از مرز عبور می‌کند؟ آیا وب‌سرور روی HTTP/2 و HTTP/3
پاسخگوست یا پروتکل‌های مدرن در لبه مرزی دراپ می‌شوند؟ آیا کل آی‌پی بلک‌هول شده
یا صرفاً پورت وب فیلتر است؟»

از آنجا که دسترسی به GitHub برای توسعه‌دهندگان حفظ می‌شود، سامانه یوشیک پینگ
(Yoshik Ping v3.0) با هویت پرچم شیر و خورشید، به عنوان یک رادار برون‌مرزی عمل
می‌کند:

1.  بدون نیاز به سرور واسط یا ابزار تحریم‌شکن، از طریق بخش کامنت Issue دستور
    /ping ارسال می‌شود.
2.  نودهای قدرتمند Azure مایکروسافت در خارج کشور بیدار می‌شوند.
3.  پرتوهای تست همزمان در لایه‌های ۴ و ۷ (TCP, UDP, H1, H2, H3 QUIC) به سمت سرور
    پرتاب می‌گردد.
4.  تحلیل مهندسی در همان Issue پاسخ داده شده و در صورت درخواست، به کانال تلگرام
    نیز ارسال می‌گردد.

 فلوچارت توپولوژی ترافیک مرزی نسخه ۳.۰

flowchart TB
    classDef edgeCloud fill:#1e1e2e,stroke:#89b4fa,stroke-width:2px,color:#cdd6f4;
    classDef azure fill:#003865,stroke:#0078d4,stroke-width:2px,color:#ffffff;
    classDef borderGate fill:#451a03,stroke:#f59e0b,stroke-width:2px,color:#fde68a;
    classDef iranNet fill:#14532d,stroke:#22c55e,stroke-width:2px,color:#dcfce7;
    classDef dropNode fill:#7f1d1d,stroke:#ef4444,stroke-width:2px,color:#fee2e2;

    subgraph GLOBAL_PLANE [🌐 گره‌های ابری خارج از کشور - مایکروسافت Azure]
        User[👤 مدیر زیرساخت]:::edgeCloud -->|دستور ChatOps در Issue| GHIssue[💬 وب‌هوک Issue گیت‌هاب]:::edgeCloud
        GHIssue --> AzureRunner[⚡️ رانر لینوکس ابری]:::azure
        
        AzureRunner --> EngineCore{🔬 هسته ارزیابی v3.0}:::azure
        EngineCore -->|لایه 4| T1[📡 TCP SYN 3-Way Handshake]:::azure
        EngineCore -->|لایه 4| T2[🔌 سوکت دیتگرام UDP خام]:::azure
        EngineCore -->|لایه 7| T3[🌐 وب سنتی HTTP/1.1]:::azure
        EngineCore -->|لایه 7| T4[🔒 مذاکره ALPN در HTTP/2]:::azure
        EngineCore -->|لایه 7| T5[⚡️ هندشیک QUIC Initial در HTTP/3]:::azure
    end

    subgraph BORDER_FIREWALL [🚧 گیت‌وی لبه مرزی و فیلترینگ هوشمند]
        T1 & T2 & T3 & T4 & T5 --> BorderCheck{تحلیل عمیق بسته / DPI}:::borderGate
    end

    BorderCheck -->|دراپ پکت / بلک‌هول مرزی| BlockDrop[🔴 مسدودی کامل آی‌پی / IP Blackhole]:::dropNode
    BorderCheck -->|پورت باز / عبور ترافیک| AllowPass[🟢 اتصال پایدار / ثبت Latency]:::iranNet

    subgraph IRAN_INFRASTRUCTURE [🏢 زیرساخت مقصد در ایران]
        AllowPass --> DC1[🏢 دیتاسنترهای داخلی پارس‌پک / آروان / آسیاتک]:::iranNet
        AllowPass --> DC2[☁️ سرورهای لبه و سرور اختصاصی]:::iranNet
    end

    BlockDrop -.-> ResultReport[📊 تحلیل داده و ساخت گزارش]:::edgeCloud
    DC1 & DC2 -.-> ResultReport
    ResultReport -->|پست در کانال تلگرام| TGChan[📢 کانال @YoshikVPS]:::edgeCloud
    ResultReport -->|ریپلای در کامنت ایشیو| GHIssue

 دستورات اجرایی در ایشیو (ChatOps v3.0)

۱. پایش عمیق چندلایه و انتشار در تلگرام

/ping arvancloud.ir:443(https) cloudflare.com:443(https:h3,udp) parspack.com:443,80(https:h1,tcp) (تایم)-1 @YoshikVPSBOT

  - تست خودکار ۳ لایه: ذکر https به تنهایی هر ۳ نسخه HTTP/1.1، HTTP/2 و HTTP/3
    را همزمان می‌سنجد.
  - تست اختصاصی QUIC: عبارت (https:h3) فقط لایه ۳ وب را روی بستر UDP بررسی
    می‌کند.
  - انتشار خودکار تلگرام: با افزودن @YoshikVPSBOT گزارش به کانال ارسال شده و
    لینک پیام در کامنت قرار می‌گیرد.

۲. بایگانی و نسخه جدید سورس

بایگانی-@YoshikVPSBOT

  - سورس کامل را در بخش Releases فشرده و منتشر می‌کند. اگر تغییری نکرده باشد،
    هوشمندانه مانع ایجاد ریلیز تکراری می‌شود.

۳. پاکسازی فوری تب Actions

اکشنز-پاک

  - با یک فرمان، تمامی سوابق و تاریخچه ران‌های قبلی در تب Actions را پاک می‌کند
    تا پنل همیشه خلوت باشد.

۴. پاکسازی فایل‌های لاگ فیزیکی

پاکسازی

  - پوشه لاگ متنی ping/ را با پرسش تاییدیه دو مرحله‌ای (بله/خیر) تخلیه می‌کند.

 راه‌اندازی سریع در ۲ دقیقه

Fork Immediately

1.  پروژه را به اکانت خود Fork کنید.
2.  به مسیر Settings ➔ Actions ➔ General رفته و دسترسی Workflow permissions را
    روی Read and write permissions ذخیره کنید.
3.  در مسیر Settings ➔ Secrets and variables ➔ Actions این ۳ مورد را ثبت کنید:
      - ADMIN_USERNAME: نام کاربری گیت‌هاب شما (مثلاً YoshikVPS)
      - TELEGRAM_BOT_TOKEN: توکن بات تلگرام (اختیاری جهت ارسال به کانال)
      - TELEGRAM_CHANNEL_ID: آیدی کانال شما با علامت @ (مثلاً @YoshikVPS)
4.  وارد تب Issues شوید و دستورات بالا را ارسال کنید!

================================================================================
           📡 YOSHIK VPS NETWORK ENGINEERING & CLOUD TELEMETRY LAB
================================================================================

| 👨‍💻 System Architect                          | 🌐 Organization             | 🛡 Core License      | ⚡️ Engine Status        |
| :-------------------------------------------: | :------------------------: | :-----------------: | :---------------------: |
| [**YoshikVPS**](https://github.com/YoshikVPS) | **Yoshik VPS Network Lab** | **MIT Open Source** | **v3.0 Titanium Ready** |

Follow YoshikVPS Star this Repo

Engineered with precision • Serverless GitHub Actions Core • Tehran Time Synced

این متن کاملاً منطبق بر پروژه، با ظاهری بسیار پیشرفته، پشتیبانی کامل از
قابلیت‌های نسخه ۳.۰ و تزیین‌شده با آیکون اختصاصی شیر و خورشید برای بخش‌های فارسی
است. می‌توانید مستقیماً داخل README.md قرار دهید.
