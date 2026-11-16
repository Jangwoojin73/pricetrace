#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
collect_daily_price_snapshot.py
매일 1회 32대 핵심 품목의 실시간 최저가를 수집하여 data/history.db 및 data/history_cache.json에 스냅샷을 영구 적재합니다.
"""

import os
import sys
import json
import sqlite3
import re
from datetime import datetime
from typing import Dict, Any, List

# 상위 디렉토리 모듈 임포트
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pricetrace_bot
except ImportError:
    pricetrace_bot = None

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "history.db")
JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "history_cache.json")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS price_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT NOT NULL,
        date TEXT NOT NULL,
        lowest_price INTEGER NOT NULL,
        mall_name TEXT DEFAULT '네이버 최저가',
        unit_price INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(keyword, date)
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_kw_date ON price_snapshots(keyword, date);")
    conn.commit()
    conn.close()

def record_price_snapshot(keyword: str, lowest_price: int, mall_name: str = "네이버 최저가", unit_price: int = 0, target_date: str = None) -> bool:
    """단일 품목의 일일 최저가 스냅샷을 DB에 기록 (UPSERT)"""
    if lowest_price <= 0:
        return False
    
    if not target_date:
        target_date = datetime.now().strftime("%Y-%m-%d")
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO price_snapshots (keyword, date, lowest_price, mall_name, unit_price)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(keyword, date) DO UPDATE SET
            lowest_price = excluded.lowest_price,
            mall_name = excluded.mall_name,
            unit_price = excluded.unit_price,
            created_at = CURRENT_TIMESTAMP;
        """, (keyword, target_date, lowest_price, mall_name, unit_price))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Error recording snapshot] {keyword}: {e}", file=sys.stderr)
        return False

def sync_db_to_json():
    """SQLite의 최신 시계열 데이터를 data/history_cache.json 파일로 동기화"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT keyword, date, lowest_price, mall_name, unit_price FROM price_snapshots ORDER BY keyword, date ASC")
        rows = cur.fetchall()
        conn.close()

        data = {}
        for kw, date, price, mall, unit_p in rows:
            if kw not in data:
                data[kw] = []
            data[kw].append({
                "date": date,
                "price": price,
                "mall_name": mall,
                "unit_price": unit_p
            })

        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[Sync] Saved {len(data)} keywords to {JSON_PATH}")
    except Exception as e:
        print(f"[Sync Error] {e}", file=sys.stderr)

if __name__ == "__main__":
    init_db()
    print("Snapshot collector initialized.")
