import re
import json

with open('server.py', 'r', encoding='utf-8') as f:
    code = f.read()

endpoints = set(re.findall(r'[\'"](/api/[a-zA-Z0-9_\/-]+)', code))
print("Endpoints in server.py:", endpoints)

# Look for functions handling routes or requests
routes = re.findall(r'def\s+do_[A-Z]+\(.*?\):|def\s+handle_[a-zA-Z0-9_]+\(.*?\):|@app\.[a-z]+\([\'"].*?[\'"]\)', code)
print("Route handlers:", routes)

# Look for trending or refresh logic
trending_matches = [line.strip() for line in code.splitlines() if 'trending' in line.lower() or 'refresh' in line.lower() or 'cache' in line.lower()]
print("\nTrending/refresh lines count:", len(trending_matches))
for l in trending_matches[:15]:
    print(" ", l)
