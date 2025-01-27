import os


try:
        base_path = os.path.dirname(os.path.abspath(__file__))  # مسیر فایل main.py
        css_path = os.path.normpath(os.path.join(base_path, "../styles.css"))  # مسیر نسبی نرمال‌سازی شده
        print(f"در حال جستجو برای فایل CSS در مسیر: {css_path}")
        with open(css_path, "r") as f:
            print(f"فایل styles.css یافت شد. مسیر: {css_path}")
            css = f.read()
            print(css)
except FileNotFoundError:
        print(f"فایل styles.css پیدا نشد. مسیر بررسی‌شده: {css_path}")
