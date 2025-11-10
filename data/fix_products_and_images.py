# fix_products_and_images.py
import pandas as pd
import requests
import time
import random
from tqdm import tqdm
import os

# ====== CONFIG ======
INPUT = "products.csv"                    # input (gốc)
OUTPUT = "products_fixed_images.csv"      # output sau xử lý
LOG_BAD = "failed_images_log.csv"         # log các sản phẩm không fix được ảnh
PEXELS_KEY = "h3iHA5nUQPNISfVqnLPM5UQmKRCcly3wNzKl87cASlf8DIlLfDaryXR1"  # bạn có thể thay
CHECK_TIMEOUT = 8
SLEEP_BETWEEN = 0.6    # tránh limit API
MAX_RETRIES = 4        # tries cho mỗi tìm + kiểm tra
# ====================

headers = {"Authorization": PEXELS_KEY}

def normalize_name_from_row(row):
    """Tìm / điền tên sản phẩm từ các cột phổ biến."""
    # Các cột khả dĩ chứa tên: name, title, product_name, product_title, Name, Title
    candidates = ['name','title','product_name','product_title','Name','Title']
    for c in candidates:
        if c in row.index:
            v = str(row.get(c) or "").strip()
            if v and v.lower() not in ["nan","none","null",""]:
                return v
    # fallback: kết hợp brand + category + id
    brand = str(row.get('brand') or "").strip()
    cat = str(row.get('category') or "").strip()
    pid = str(row.get('id') or "")
    built = " ".join([x for x in [brand, cat] if x])
    if built:
        return (built + (" - "+pid if pid else "")).strip()
    return ""


def is_url_ok(url):
    try:
        # HEAD may be blocked, try GET with stream
        r = requests.get(url, timeout=CHECK_TIMEOUT, stream=True)
        return r.status_code == 200
    except Exception:
        return False

def pexels_search_for_image(query):
    url = "https://api.pexels.com/v1/search"
    params = {"query": query, "per_page": 30}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json().get("photos", [])
            # prefer 'src' keys: large, medium, original ...
            links = []
            for p in data:
                src = p.get("src", {})
                # pick largest sensible
                link = src.get("large") or src.get("original") or src.get("medium")
                if link:
                    links.append(link)
            return links
        else:
            # handle rate limit or errors gracefully
            # print("Pexels status:", r.status_code, r.text[:120])
            return []
    except Exception:
        return []

def main():
    if not os.path.exists(INPUT):
        print("File not found:", INPUT)
        return

    df = pd.read_csv(INPUT, dtype=str).fillna("")
    n = len(df)
    print("Tổng sản phẩm:", n)

    bad_rows = []
    used_links = set()

    # load existing image links into used set (to avoid duplicates)
    for i,row in df.iterrows():
        url = str(row.get("image") or "").strip()
        if url:
            used_links.add(url)

    for idx, row in tqdm(df.iterrows(), total=n, desc="Processing"):
        # 1) ensure name present
        name_val = str(row.get('name') or "").strip()
        if not name_val:
            new_name = normalize_name_from_row(row)
            df.at[idx,'name'] = new_name

        # 2) validate image URL
        img = str(row.get('image') or "").strip()
        ok = False
        if img:
            ok = is_url_ok(img)

        if not ok:
            # Try up to MAX_RETRIES to get a working unique image from Pexels
            title = df.at[idx,'name'] or str(row.get('title') or "")
            color = str(row.get('color') or "")
            query = f"{title} {color} fashion clothing".strip()
            found = None
            tries = 0
            while tries < MAX_RETRIES:
                results = pexels_search_for_image(query)
                # shuffle and pick first not used and working
                random.shuffle(results)
                for link in results:
                    if link in used_links:
                        continue
                    if is_url_ok(link):
                        found = link
                        break
                if found:
                    break
                tries += 1
                time.sleep(SLEEP_BETWEEN * 2)  # backoff a bit

            if found:
                df.at[idx,'image'] = found
                used_links.add(found)
            else:
                # fallback options: try simple color+product type short query
                fallback_queries = []
                # try using words from name (top 3)
                words = [w for w in (title.split() if title else []) if len(w)>2]
                if words:
                    fallback_queries.append(" ".join(words[:3]) + " fashion")
                if color:
                    fallback_queries.append(f"{color} clothing")
                # try fallback queries
                for fq in fallback_queries:
                    results = pexels_search_for_image(fq)
                    random.shuffle(results)
                    for link in results:
                        if link in used_links:
                            continue
                        if is_url_ok(link):
                            found = link
                            break
                    if found:
                        break
                    time.sleep(0.4)

                if found:
                    df.at[idx,'image'] = found
                    used_links.add(found)
                else:
                    # final fallback -> placeholder and log
                    placeholder = "https://via.placeholder.com/400x400?text=No+Image"
                    df.at[idx,'image'] = placeholder
                    bad_rows.append({
                        "index": idx,
                        "id": row.get("id",""),
                        "name": df.at[idx,'name'],
                        "original_image": img,
                        "final_image": placeholder
                    })

        # small sleep to be gentle with API
        time.sleep(SLEEP_BETWEEN)

    # save results
    df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print("Saved fixed CSV:", OUTPUT)

    if bad_rows:
        pd.DataFrame(bad_rows).to_csv(LOG_BAD, index=False, encoding="utf-8-sig")
        print("Logged failed images to:", LOG_BAD)
    else:
        print("All images fixed (or replaced). No failures logged.")

if __name__ == "__main__":
    main()
