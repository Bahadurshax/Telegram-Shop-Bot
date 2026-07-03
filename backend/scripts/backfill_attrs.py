"""
Разовый бэкфилл: извлекает структурированные атрибуты (attrs) для товаров,
у которых их ещё нет, и обновляет категорию по типу устройства.

Запуск из каталога backend:
    python -m scripts.backfill_attrs           # только товары без attrs
    python -m scripts.backfill_attrs --force   # переизвлечь у всех товаров
"""
import argparse
import asyncio
import sys

from app.database import db
from app.repositories.product_repo import _compact_attrs
from app.services.attrs_extractor import AttrsExtractor, DEVICE_TYPE_TO_CATEGORY


async def main(force: bool = False):
    extractor = AttrsExtractor()
    if not extractor.available:
        print("CLAUDE_API_KEY не настроен — бэкфилл невозможен")
        sys.exit(1)

    await db.connect()
    try:
        collection = db.database.products
        query = {} if force else {"$or": [{"attrs": None}, {"attrs": {"$exists": False}}]}
        products = [p async for p in collection.find(query)]
        print(f"Товаров к обогащению: {len(products)}")

        if not products:
            return

        attrs_list = await extractor.extract_many(
            [(p.get("name", ""), p.get("description", "")) for p in products]
        )

        updated = 0
        failed = 0
        for product, attrs in zip(products, attrs_list):
            if attrs is None:
                failed += 1
                print(f"  [пропуск] {product.get('name')}")
                continue

            update = {"attrs": attrs.model_dump()}
            category = DEVICE_TYPE_TO_CATEGORY.get(attrs.device_type or "")
            if category:
                update["category"] = category

            await collection.update_one(
                {"_id": product["_id"]},
                {"$set": _compact_attrs(update)},
            )
            updated += 1
            print(f"  [ok] {product.get('name')} -> {attrs.human_summary()}")

        print(f"\nГотово: обновлено {updated}, ошибок {failed}")
    finally:
        await db.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Переизвлечь атрибуты у всех товаров")
    args = parser.parse_args()
    asyncio.run(main(force=args.force))
