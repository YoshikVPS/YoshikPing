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
