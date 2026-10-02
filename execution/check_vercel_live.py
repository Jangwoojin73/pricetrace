import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import urllib.request
import json
import hashlib

urls = [
    'https://pricetrace-nu.vercel.app/manifest.json',
    'https://pricetrace-nu.vercel.app/icons/icon-192x192.png',
    'https://pricetrace-nu.vercel.app/icons/icon-512x512.png',
    'https://pricetrace-nu.vercel.app/logo_jwj.svg',
    'https://pricetrace-nu.vercel.app/favicon.ico'
]

print("=" * 60)
print("🌐 [Vercel Live Check] 실제 Vercel 배포 자산 실측 검사")
print("=" * 60)

for u in urls:
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            md5 = hashlib.md5(data).hexdigest()
            print(f"{u}")
            print(f"  - Status: {resp.status}, Size: {len(data)} bytes, MD5: {md5}")
            if 'manifest.json' in u:
                print("  - Content:")
                print(data.decode('utf-8'))
    except Exception as e:
        print(f"{u} -> ERROR: {e}")

print("=" * 60)
