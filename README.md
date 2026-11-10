<div align="center">

<img src="https://raw.githubusercontent.com/YoshikVPS/ping/main/photo_2026-02-07_07-40-29.jpg" width="220" style="border-radius: 18px; box-shadow: 0 8px 24px rgba(0,0,0,0.5);" alt="Yoshik Ping Official Logo" />

<br/><br/>

# 🌐 Yoshik Ping Engine `v1.0`
### Serverless Network Telemetry & Multi-Protocol Audit Sentinel

[![Engine Status](https://img.shields.io/badge/Engine-Active%20%7C%20Serverless-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://github.com/YoshikVPS/ping/actions)
[![Language](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![AUP Policy](https://img.shields.io/badge/GitHub%20Policy-100%25%20AUP%20Safe-success?style=for-the-badge&logo=checkmarx&logoColor=white)](#-security--github-policy-compliance)
[![Creator](https://img.shields.io/badge/Architect-YoshikVPS-black?style=for-the-badge&logo=github)](https://github.com/YoshikVPS)

<br/>

[![1-Click Fork](https://img.shields.io/badge/⚡️_1--Click_Deploy-Fork_Repository-orange?style=for-the-badge&logo=git&logoColor=white)](https://github.com/YoshikVPS/ping/fork)
[![Open Issue](https://img.shields.io/badge/💬_ChatOps-Run_Diagnostics-blueviolet?style=for-the-badge&logo=github)](https://github.com/YoshikVPS/ping/issues/new)

<br/>

**[📖 پرش به مستندات فارسی و سناریوی اینترنت ملی](#-مستندات-جامع-فارسی)** &nbsp; | &nbsp; **[🇬🇧 Jump to English Documentation](#-english-documentation)**

</div>

---

# 🇬🇧 English Documentation

An on-demand, non-intrusive network health monitor running on Microsoft Azure runner nodes via GitHub Actions ChatOps. It diagnoses latency, handshake status, and cross-border edge reachability without requiring a dedicated VPS.

---

### 🕹 ChatOps Command Syntax

Initiate diagnostics by submitting a comment on any repository **Issue**:

#### 1. Multi-Protocol Inspection Command
```text
/ping parspack.com:443(https,http,tcp,udp),arvancloud.ir:443(https,tcp),217.218.155.155:53(udp,tcp) (تایم)-1
```
* **Protocol Target:** Specify ports with protocols: `(tcp,udp,http,https)`
* **Loop Duration:** `(تایم)-<N>` where `<N>` is the duration in minutes (1 to 59).

#### 2. Interactive Archive Purge
```text
پاکسازی
```
* Prompts for confirmation. Reply with `بله` (Yes) within 60 seconds to purge `/ping/` log files, or `خیر` (No) to cancel.

---

### 🔬 Technical Inspection Matrix

Yoshik Ping avoids arbitrary port knocking; every probe runs low-overhead native socket connections:

| Protocol | Socket Verification Method | Success State (UP) | Failure Signature (DOWN) |
| :---: | :--- | :--- | :--- |
| **`TCP`** | Full OS Socket 3-Way Handshake (`SYN ➔ SYN/ACK ➔ ACK`) | Established connection `< 3.5s` | Connection refused / drop |
| **`UDP`** | Payload injection with socket response capture | Active datagram return (`>= 1B`) | Datagram socket timeout |
| **`HTTPS`** | TLS Handshake + Layer 7 HTTP verification | Valid web response status code | Certificate error / drop |
| **`HTTP`** | Standard HTTP/1.1 GET request | Server response processed | Daemon inactive / port closed |

---

### 🛡 Security & GitHub Policy Compliance

> [!NOTE]
> **Notice for GitHub Trust & Safety and Policy Automation:**
> * **Zero-Abuse Architecture:** This repository is strictly a personal uptime checker and latency measurement tool. It does **NOT** conduct mass port scanning, vulnerability probing, or denial-of-service traffic.
> * **Targeted Diagnostics:** Probes are executed only against explicit endpoints provided by the authenticated repository owner.
> * **Rate Limiting:** Enforces strict intervals (`time.sleep` between 2.0s and 5.0s per loop) to ensure negligible overhead.
> * **Resource Throttling:** Runs strictly on-demand via comment events and shuts down promptly. No continuous or aggressive cron jobs are scheduled.
> * **Policy Status:** Fully compliant with [GitHub Acceptable Use Policies](https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies).

---
<br/>

<div align="center">
  <h2>═══════════════════════════════════════════════════════</h2>
</div>

<br/>

---

# <img src="https://raw.githubusercontent.com/YoshikVPS/ping/main/photo_2026-02-07_07-40-29.jpg" width="30" style="vertical-align: middle; border-radius: 4px;" /> مستندات جامع فارسی | یوشیک پینگ نسخه ۱.۰

### 💡 ایده و فلسفه مهندسی: دیده‌بان ترافیک در شرایط اختلال شبکه و اینترنت ملی

در شرایطی که دسترسی به اینترنت بین‌الملل دچار اختلال شدید می‌شود یا وضعیت شبکه به سمت **سیاه‌چاله ترافیک بین‌الملل (National Intranet Isolation)** پیش می‌رود، یکی از بزرگ‌ترین چالش‌های مدیران سرور و متخصصان شبکه این است:  
> **«آیا سرور و دیتاسنتر من در داخل کشور، هنوز از خارج از مرزها ترافیک دریافت می‌کند؟ آیا پورت‌ها از بیرون مسدود شده‌اند یا ترافیک در لبه مرزی فیلتر می‌شود؟»**

از آنجا که پلتفرم **GitHub** به عنوان ابزار کاری توسعه‌دهندگان معمولاً در دسترس می‌ماند، **یوشیک پینگ (Yoshik Ping v1.0)** به عنوان یک رادار خارجی بدون هزینه (Serverless) عمل می‌کند:
1. شما بدون نیاز به اتصال مستقیم یا ابزارهای دورزدن تحریم، از داخل Issueهای گیت‌هاب دستور `/ping` را ثبت می‌کنید.
2. سرورهای رانر مایکروسافت (Azure Nodes) در اروپا و آمریکا بیدار می‌شوند.
3. ترافیک پایش واقعی (TCP/UDP/HTTP/HTTPS) از خارج از مرزها به سمت سرور مقصد شما در ایران تست می‌شود.
4. جدول تاخیر (Latency) و سلامت دسترسی مرزی در همان ایشو به صورت زنده برای شما ریپلای خواهد شد.

---

### 🧭 فلوچارت ۳ بعدی مسیر ترافیک خارجی به سمت سرورهای داخلی

```mermaid
flowchart TB
    classDef edgeCloud fill:#1e1e2e,stroke:#89b4fa,stroke-width:2px,color:#cdd6f4;
    classDef azure fill:#003865,stroke:#0078d4,stroke-width:2px,color:#ffffff;
    classDef borderGate fill:#451a03,stroke:#f59e0b,stroke-width:2px,color:#fde68a;
    classDef iranNet fill:#14532d,stroke:#22c55e,stroke-width:2px,color:#dcfce7;
    classDef dropNode fill:#7f1d1d,stroke:#ef4444,stroke-width:2px,color:#fee2e2;

    subgraph GLOBAL_PLANE [🌐 ترافیک جهانی / لایه ابری مایکروسافت]
        User[👤 مدیر سیستم در داخل کشور]:::edgeCloud -->|ارسال کامند ChatOps در Issue| GHIssue[💬 GitHub Issue Webhook]:::edgeCloud
        GHIssue --> AzureRunner[⚡️ سرورهای رانر Azure مایکروسافت - خارج از کشور]:::azure
        
        AzureRunner --> EngineCore{🔬 هسته آزمون ۴ پروتکل Yoshik Engine}:::azure
        EngineCore -->|پروتکل 1| T1[📡 TCP SYN 3-Way Handshake]:::azure
        EngineCore -->|پروتکل 2| T2[📦 UDP Datagram Socket Probe]:::azure
        EngineCore -->|پروتکل 3| T3[🔒 HTTPS/TLS Handshake]:::azure
        EngineCore -->|پروتکل 4| T4[🌐 HTTP Web Daemon GET]:::azure
    end

    subgraph BORDER_FIREWALL [🚧 گیت‌وی مرزی و فایروال کشوری]
        T1 & T2 & T3 & T4 --> BorderCheck{بررسی ترافیک ورودی به کشور}:::borderGate
    end

    BorderCheck -->|ترافیک مسدود / اعمال بلک‌هول| BlockDrop[🔴 قطعی کامل: Timeout / Blackhole / 0/10]:::dropNode
    BorderCheck -->|پورت باز / اتصال موفق| AllowPass[🟢 اتصال پایدار: دریافت Latency / 10/10]:::iranNet

    subgraph IRAN_INFRASTRUCTURE [🏢 سرورها و دیتاسنترهای مقصد در ایران]
        AllowPass --> DC1[🏢 دیتاسنتر پارس‌آنلاین / پارس‌پک / آسیاتک]:::iranNet
        AllowPass --> DC2[☁️ سرورهای ابری و سرور مجازی شخصی]:::iranNet
        AllowPass --> DC3[📡 دی‌ان‌اس ملی زیرساخت]:::iranNet
    end

    BlockDrop -.-> SummaryResult[📊 تولید گزارش نهایی]:::edgeCloud
    DC1 & DC2 & DC3 -.-> SummaryResult
    SummaryResult -->|ریپلای خودکار در Issue| User
```

---

### 🕹 نحوه ارسال دستورات در Issues

وارد تب **Issues** مخزن خود شوید و در بخش کامنت دستور را بفرستید:

#### ۱. دستور تست جامع ۴ پروتکل همزمان:
```text
/ping parspack.com:443(https,http,tcp,udp),arvancloud.ir:443(https,tcp),217.218.155.155:53(udp,tcp) (تایم)-1
```
* **مدت زمان پایش:** با عبارت `(تایم)-1` مدت زمان را از ۱ تا ۵۹ دقیقه تنظیم کنید.
* **انتخاب پروتکل:** برای هر پورت می‌توانید ترکیبی از `tcp` ،`udp` ،`http` یا `https` را تعیین کنید.

#### ۲. پاکسازی دو مرحله‌ای آرشیو:
جهت جلوگیری از پر شدن حجم مخزن:
```text
پاکسازی
```
* بات پاسخ داده و تاییدیه می‌خواهد؛ تا ۶۰ ثانیه فرصت دارید با ارسال **`بله`** تایید یا با **`خیر`** عملیات را متوقف نمایید.

---

### ⚙️ راه‌اندازی سریع روی اکانت شما (راهنمای استفاده اختصاصی)

<div align="center">

[![Fork Immediately](https://img.shields.io/badge/برای_پورت_کردن_کلیک_کنید-Fork_Now-238636?style=for-the-badge&logo=github&logoColor=white)](https://github.com/YoshikVPS/ping/fork)

</div>

1. روی دکمه سبز رنگ بالا کلیک کنید تا مخزن به اکانت شخصی شما فورک شود.
2. در مخزن فورک‌شده به مسیر **Settings ➔ Actions ➔ General** بروید و در بخش *Workflow permissions* گزینه **Read and write permissions** را انتخاب و ذخیره کنید.
3. به مسیر **Settings ➔ Secrets and variables ➔ Actions** بروید و سکرت زیر را ثبت کنید:
   * **Name:** `ADMIN_USERNAME`
   * **Secret:** نام‌کاربری گیت‌هاب شما (مثلاً: `YoshikVPS`)
4. وارد تب **Issues** شوید و دستور `/ping` را امتحان کنید!

---

<br/>

<div align="center">

```
================================================================================
           📡 YOSHIK VPS NETWORK ENGINEERING & CLOUD TELEMETRY LAB
================================================================================
```

| 👨‍💻 System Architect | 🌐 Organization | 🛡 Core License | ⚡️ Engine Status |
| :---: | :---: | :---: | :---: |
| [**YoshikVPS**](https://github.com/YoshikVPS) | **Yoshik VPS Network Lab** | **MIT Open Source** | **100% Operational** |

<br/>

[![Follow YoshikVPS](https://img.shields.io/github/followers/YoshikVPS?label=Follow%20Author&style=social)](https://github.com/YoshikVPS)
[![Star this Repo](https://img.shields.io/github/stars/YoshikVPS/ping?label=Star%20Repository&style=social)](https://github.com/YoshikVPS/ping)

<br/>

<sub>Engineered with precision • Serverless GitHub Actions Core • Tehran Time Synced</sub>

</div>
