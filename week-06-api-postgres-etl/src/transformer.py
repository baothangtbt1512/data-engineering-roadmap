from typing import List, Dict, Any, Tuple
from src.config import logger

class DataTransformer:
    @staticmethod
    def transform_users(raw_users: List[Dict[str, Any]]) -> List[Tuple]:
        transformed = []
        for u in raw_users:
            try:
                user_id = int(u["id"])
                full_name = f"{u.get('firstName', '')} {u.get('lastName', '')}".strip()
                email = str(u.get("email", "")).strip().lower()
                gender = u.get("gender", "unknown")
                city = u.get("address", {}).get("city", "Unknown")

                if not email or "@" not in email:
                    continue

                transformed.append((user_id, full_name, email, gender, city))
            except (KeyError, ValueError) as err:
                logger.warning(f"Skipping malformed user record {u.get('id')}: {err}")
        return transformed

    @staticmethod
    def transform_products(raw_products: List[Dict[str, Any]]) -> List[Tuple]:
        transformed = []
        for p in raw_products:
            try:
                product_id = int(p["id"])
                title = str(p.get("title", "")).strip()
                category = str(p.get("category", "General"))
                price = round(float(p.get("price", 0.0)), 2)
                stock = int(p.get("stock", 0))

                transformed.append((product_id, title, category, price, stock))
            except (KeyError, ValueError) as err:
                logger.warning(f"Skipping malformed product record {p.get('id')}: {err}")
        return transformed

    @staticmethod
    def transform_orders(raw_orders: List[Dict[str, Any]]) -> List[Tuple]:
        transformed = []
        for o in raw_orders:
            try:
                order_id = int(o["id"])
                user_id = int(o["userId"])
                total_products = int(o.get("totalProducts", 0))
                total_quantity = int(o.get("totalQuantity", 0))
                total_amount = round(float(o.get("total", 0.0)), 2)
                discounted_total = round(float(o.get("discountedTotal", 0.0)), 2)

                transformed.append((order_id, user_id, total_products, total_quantity, total_amount, discounted_total))
            except (KeyError, ValueError) as err:
                logger.warning(f"Skipping malformed order record {o.get('id')}: {err}")
        return transformed