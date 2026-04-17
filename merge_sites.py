#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import requests

SOURCES_JSON_PATH = "sources.json"
TARGET_JSON_PATH = "青龙.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TVBoxMerge/1.0)"
}

def get_sites_from_url(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and "sites" in data:
                return data["sites"]
            elif isinstance(data, list):
                return data
    except Exception as e:
        print(f"[拉取失败] {url} | {e}")
    return []

def fix_site_paths(site, base):
    if not base:
        return site
    base = base.rstrip("/")
    for k, v in site.items():
        if isinstance(v, str) and v.startswith("./"):
            site[k] = base + "/" + v[2:]
    return site

def main():
    print("== TVBox 站点合并开始 ==")

    if not os.path.exists(SOURCES_JSON_PATH):
        print(f"[错误] 找不到 {SOURCES_JSON_PATH}")
        exit(1)

    with open(SOURCES_JSON_PATH, "r", encoding="utf-8") as f:
        sources = json.load(f)

    sites = []
    keys = set()

    if os.path.exists(TARGET_JSON_PATH):
        with open(TARGET_JSON_PATH, "r", encoding="utf-8") as f:
            old = json.load(f)
            sites = old.get("sites", [])
            keys = {s.get("key") for s in sites if s.get("key")}

    for src in sources:
        url = src.get("url")
        base = src.get("base", "")
        if not url:
            continue

        print(f"[拉取] {url}")
        for s in get_sites_from_url(url):
            key = s.get("key")
            if key and key not in keys:
                sites.append(fix_site_paths(s, base))
                keys.add(key)

    result = {
        "sites": sites,
        "updateTime": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(sites)
    }

    with open(TARGET_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[完成] 共 {len(sites)} 个站点，已生成 {TARGET_JSON_PATH}")

if __name__ == "__main__":
    main()
