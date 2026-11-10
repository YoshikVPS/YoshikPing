<div align="center">

# 🌐 Yoshik Ping Engine `v1.0`
### Serverless Network Telemetry & Multi-Protocol Audit Sentinel

[![Engine Status](https://img.shields.io/badge/Engine-Active%20%7C%20Serverless-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://github.com/YoshikVPS/ping/actions)
[![Language](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![AUP Policy](https://img.shields.io/badge/GitHub%20Policy-100%25%20AUP%20Safe-success?style=for-the-badge&logo=checkmarx&logoColor=white)](#-security--github-policy-compliance)
[![Creator](https://img.shields.io/badge/Author-YoshikVPS-black?style=for-the-badge&logo=github)](https://github.com/YoshikVPS)

<br/>

[![1-Click Fork](https://img.shields.io/badge/⚡️_1--Click_Deploy-Fork_Repository-orange?style=for-the-badge&logo=git&logoColor=white)](https://github.com/YoshikVPS/ping/fork)
[![Open Issue](https://img.shields.io/badge/💬_ChatOps-Run_Diagnostics-blueviolet?style=for-the-badge&logo=github)](https://github.com/YoshikVPS/ping/issues/new)

<br/>

**[🇬🇧 Read in English](#-english-documentation)** &nbsp; | &nbsp; **[🇮🇷 مطالعه راهنمای فارسی](#-مستندات-جامع-فارسی)**

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

### 👥 How to Deploy on Your Account (Fork Guide)

<div align="center">

[![Fork Immediately](https://img.shields.io/badge/Clone%20Now-Click%20Here%20to%20Fork-2ea44f?style=for-the-badge&logo=github)](https://github.com/YoshikVPS/ping/fork)

</div>

1. Click the button above to fork the repository instantly.
2. In your forked repository, navigate to **Settings ➔ Actions ➔ General**.
3. Under **Workflow permissions**, select **Read and write permissions** and click **Save**.
4. Go to **Settings ➔ Secrets and variables ➔ Actions** and create a **New repository secret**:
   * **Name:** `ADMIN_USERNAME`
   * **Secret:** Your GitHub username (e.g. `YoshikVPS`)
5. Open an Issue and comment `/ping` to run your first diagnostic.

---
<br/>

<div align="center">
  <h2>════════════════════════════════════════════</h2>
</div>

<br/>

---

# 🇮🇷 مستندات جامع فارسی

سامانه هوشمند و سبک مانیتورینگ وضعیت سلامت شبکه، پایش پورت‌ها و رادار تحریم مبتنی بر زیرساخت پردازشی مایکروسافت/گیت‌هاب با معماری تعاملی **ChatOps**.

---

### 🚀 نحوه ارسال دستورات در Issues

برای شروع تست شبکه، وارد بخش **Issues** مخزن شوید و در کادر کامنت دستور خود را ارسال کنید:

#### ۱. دستور تست جامع پروتکل‌ها
```text
/ping parspack.com:443(https,http,tcp,udp),arvancloud.ir:443(https,tcp),217.218.155.155:53(udp,tcp) (تایم)-1
```
* **مدت زمان تست:** با قرار دادن `(تایم)-1` مدت تست را از ۱ تا ۵۹ دقیقه مشخص کنید.
* **انتخاب پروتکل:** برای هر پورت می‌توانید یک یا چند پروتکل از بین `http`, `https`, `tcp`, `udp` را انتخاب کنید.

#### ۲. پاکسازی آرشیو لاگ‌ها
برای حذف گزارش‌های متنی و تمیز ماندن مخزن، کافی است در کامنت بنویسید:
```text
پاکسازی
```
* ربات از شما تاییدیه می‌خواهد. ظرف مدت ۶۰ ثانیه بنویسید **`بله`** تا پوشه لاگ‌ها حذف شود یا بنویسید **`خیر`** تا لغو گردد.

---

### 📋 نمونه گزارش تحلیلی ربات در ایشو

> 🖥 **آی‌پی سرور مایکروسافت:** `20.163.133.232`  
> 📅 **تاریخ ارزیابی (شمسی):** `1405/08/19`  
> 🕒 **بازه پایش:** `22:10:02` ➔ `22:11:04` (به وقت رسمی ایران)  
> ⏱ **طول پایش دقیق:** `1 دقیقه و 2 ثانیه` (`10` مرحله ارزیابی)

| هدف ارزیابی | آی‌پی مقصد (Resolved IP) | پروتکل | نرخ موفقیت | میانگین Latency | وضعیت پورت |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `parspack.com:443` | `194.26.195.206` | `HTTPS` | `10/10` | `667.16 ms` | 🟢 پایدار (موفق (کد 200)) |
| `parspack.com:443` | `194.26.195.206` | `TCP` | `10/10` | `163.05 ms` | 🟢 پایدار (پورت TCP باز است) |
| `217.218.155.155:53` | `217.218.155.155` | `UDP` | `10/10` | `196.69 ms` | 🟢 پایدار (پاسخ UDP دریافت شد) |
| `217.218.155.155:53` | `217.218.155.155` | `TCP` | `0/10` | `ناموفق` | 🔴 قطع (Connection refused) |

---

### ⚙️ راه‌اندازی با یک کلیک (پورْت سریع روی اکانت شما)

<div align="center">

[![Fork Yoshik Ping](https://img.shields.io/badge/برای_پورت_کردن_پروژه_کلیک_کنید-Fork_Now-238636?style=for-the-badge&logo=github&logoColor=white)](https://github.com/YoshikVPS/ping/fork)

</div>

برای اینکه کل سیستم روی مخزن شخصی خودتان کپی و فعال شود:

1. **انتقال به اکانت شما:** روی دکمه سبز رنگ بالا کلیک کنید تا مخزن مستقیماً برای شما فورک شود.
2. **فعال‌سازی دسترسی رایت:** به مسیر `Settings` ➔ `Actions` ➔ `General` رفته و در بخش *Workflow permissions* گزینه **Read and write permissions** را انتخاب کنید.
3. **تنظیم هویت مدیر مخزن:**
   - به مسیر `Settings` ➔ `Secrets and variables` ➔ `Actions` بروید.
   - یک سکرت جدید با مشخصات زیر بسازید:
   ```yaml
   Name: ADMIN_USERNAME
   Secret: نام‌کاربری گیت‌هاب شما (مثلاً YoshikVPS)
   ```
4. **شروع پایش:** وارد تب **Issues** شوید، دستور پینگ را کامنت کنید و نتیجه را ببینید!

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
