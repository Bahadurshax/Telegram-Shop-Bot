"""
Разовая миграция: пересчитывает category у товаров по уже сохранённому
attrs.device_type через актуальный DEVICE_TYPE_TO_CATEGORY.

Нужна после того, как hdd выделили в отдельную категорию (раньше жёсткие
диски попадали в accessories). AI не вызывается — берём device_type из базы,
поэтому запуск бесплатный.

Запуск из каталога backend:
    python -m scripts.resync_categories            # показать, что изменится (dry-run)
    python -m scripts.resync_categories --apply     # применить изменения
"""
import argparse
import asyncio

from app.database import db
from app.services.attrs_extractor import DEVICE_TYPE_TO_CATEGORY


async def main(apply: bool = False):
    await db.connect()
    try:
        collection = db.database.products
        products = [p async for p in collection.find({"attrs.device_type": {"$exists": True}})]
        print(f"Товаров с device_type: {len(products)}")

        changed = 0
        for product in products:
            device_type = (product.get("attrs") or {}).get("device_type")
            target = DEVICE_TYPE_TO_CATEGORY.get(device_type or "")
            if not target or product.get("category") == target:
                continue

            changed += 1
            print(f"  {product.get('name')}: {product.get('category')} -> {target}")
            if apply:
                await collection.update_one(
                    {"_id": product["_id"]},
                    {"$set": {"category": target}},
                )

        if apply:
            print(f"\nГотово: обновлено {changed} товаров")
        else:
            print(f"\nБудет обновлено {changed} товаров. Запусти с --apply, чтобы применить.")
    finally:
        await db.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Применить изменения (без флага — только показать)")
    args = parser.parse_args()
    asyncio.run(main(apply=args.apply))
