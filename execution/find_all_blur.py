import re

with open('public/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

for line_no, line in enumerate(css.splitlines(), 1):
    if 'blur' in line.lower() or 'filter' in line.lower():
        print(f"style.css:{line_no}: {line.strip()}")

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

for line_no, line in enumerate(html.splitlines(), 1):
    if 'blur' in line.lower() or 'filter' in line.lower():
        print(f"index.html:{line_no}: {line.strip()[:100]}")
