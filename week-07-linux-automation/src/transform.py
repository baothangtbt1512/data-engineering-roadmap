import os
import sys
import json

def transform_data():
    input_file = "data/raw_extracted.json"
    output_file = "data/transformed_data.json"
    
    if not os.path.exists(input_file):
        print(f"[TRANSFORM ERROR] Source file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            raw_items = json.load(f)

        cleaned_items = []
        for item in raw_items:
            # Data cleansing & Validation
            prod_id = int(item["id"])
            title = str(item.get("title", "")).strip()
            category = str(item.get("category", "General")).strip().lower()
            price = round(float(item.get("price", 0.0)), 2)
            discount_pct = round(float(item.get("discountPercentage", 0.0)), 2)
            
            # Tính giá thực tế sau chiết khấu
            net_price = round(price * (1 - discount_pct / 100), 2)
            stock = int(item.get("stock", 0))

            cleaned_items.append({
                "product_id": prod_id,
                "title": title,
                "category": category,
                "original_price": price,
                "discount_percentage": discount_pct,
                "net_price": net_price,
                "stock": stock
            })

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(cleaned_items, f, ensure_ascii=False, indent=2)

        print(f"[TRANSFORM] Transformed {len(cleaned_items)} records successfully.")
        sys.exit(0)
    except Exception as e:
        print(f"[TRANSFORM ERROR] Data transformation failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    transform_data()