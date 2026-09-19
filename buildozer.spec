[app]

# نام برنامه
title = سیستم حسابگر پیشرفته طلا

# نام پکیج برنامه
package.name = farhadgold

# دامنه پکیج
package.domain = org.farhad

# مسیر سورس
source.dir = .

# پسوندهای فایل‌های Python
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,ttf

# نسخه برنامه
version = 1.0

# وابستگی‌های Python
requirements = python3,kivy

# جهت صفحه
orientation = portrait

# نمایش تمام صفحه
fullscreen = 0


# ------------------------------------------------------------
# تنظیمات Android
# ------------------------------------------------------------

android.api = 35

android.minapi = 21

android.ndk = 27c

android.accept_sdk_license = True

# معماری‌های Android
android.archs = arm64-v8a, armeabi-v7a


# ------------------------------------------------------------
# مجوزها
# ------------------------------------------------------------

android.permissions = INTERNET


# ------------------------------------------------------------
# تنظیمات Buildozer
# ------------------------------------------------------------

[buildozer]

# خروجی Buildozer
log_level = 2

warn_on_root = 1