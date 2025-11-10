import pandas as pd
import requests
import random
import time
from tqdm import tqdm  # pip install tqdm

# ===== CONFIG =====
PEXELS_API_KEY = "h3iHA5nUQPNISfVqnLPM5UQmKRCcly3wNzKl87cASlf8DIlLfDaryXR1"
INPUT_CSV = "products.csv"
OUTPUT_CSV = "products_with_unique_images.csv"
SLEEP_TIME = 0.6  # giãn cách giữa các request (API free giới hạn 200 req/h)
# ==================

headers = {"Authorization": PEXELS_API_KEY}

def search_image(query):
    """Tìm ảnh theo tên + màu sản phẩm."""
    url = "https://api.pexels.com/v1/search"
    params = {"query": query, "per_page": 30}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json().get("photos", [])
            if data:
                return [photo["src"]["medium"] for photo in data]
    except Exception as e:
        print(f"Lỗi tìm ảnh cho '{query}': {e}")
    return []

def main():
    df = pd.read_csv(INPUT_CSV)
    used_links = set()

    print(f"🔍 Tổng sản phẩm: {len(df)}\n")

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Đang xử lý"):
        title = str(row.get("name", "product"))
        color = str(row.get("color", ""))
        query = f"{title} {color} fashion clothing"
        
        # Tìm ảnh từ Pexels
        results = search_image(query)
        img_link = None
        if results:
            random.shuffle(results)
            for link in results:
                if link not in used_links:
                    img_link = link
                    break

        # Nếu không có kết quả hợp lệ → fallback
        if not img_link:
            img_link = "https://via.placeholder.com/400x400?text=No+Image"

        used_links.add(img_link)
        df.at[idx, "image"] = img_link

        # nghỉ 0.6s giữa các request để tránh bị limit
        time.sleep(SLEEP_TIME)

    # Lưu file
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n✅ Hoàn tất! File lưu tại: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
