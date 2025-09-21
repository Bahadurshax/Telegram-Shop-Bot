"""
Простой скрипт для добавления тестовых товаров
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import db
from app.services.product_service import ProductService
from app.models.product import ProductCreate


async def add_test_products():
    """Добавить тестовые товары"""
    print("🚀 Подключение к базе данных...")
    await db.connect()
    
    product_service = ProductService()
    
    # Очищаем старые товары
    collection = db.database.products
    deleted = await collection.delete_many({})
    print(f"🗑 Удалено старых товаров: {deleted.deleted_count}")
    
    # Тестовые товары для демонстрации
    products = [
        # IP КАМЕРЫ (для офисов и организаций)
        {
            "name": "Hikvision DS-2CD1043G0-I 4MP",
            "description": "4Мп IP камера с ИК подсветкой до 30м, объектив 2.8мм, H.265+, металлический корпус",
            "price_uzs": 850000,
            "price_usd": 75,
            "usd_rate": 11333,
            "category": "ip_cameras"
        },
        {
            "name": "Dahua IPC-HFW1230S-S4 2MP",
            "description": "2Мп IP камера с ИК подсветкой до 30м, объектив 3.6мм, H.264+, поддержка PoE",
            "price_uzs": 650000,
            "price_usd": 57,
            "usd_rate": 11404,
            "category": "ip_cameras"
        },
        {
            "name": "Uniview IPC2122SR3-PF28 2MP",
            "description": "2Мп IP камера с ИК подсветкой до 30м, PoE, H.265, Smart IR технология",
            "price_uzs": 720000,
            "price_usd": 63,
            "usd_rate": 11429,
            "category": "ip_cameras"
        },
        {
            "name": "Hikvision DS-2CD2043G0-I 4MP Premium",
            "description": "4Мп IP камера с ИК подсветкой до 30м, WDR 120дБ, аудио вход/выход, H.265+",
            "price_uzs": 1200000,
            "price_usd": 105,
            "usd_rate": 11429,
            "category": "ip_cameras"
        },
        {
            "name": "Hikvision DS-2CD1023G0-I 2MP",
            "description": "2Мп IP камера с ИК подсветкой до 30м, объектив 2.8мм, H.265+, металлический корпус",
            "price_uzs": 650000,
            "price_usd": 57,
            "usd_rate": 11333,
            "category": "ip_cameras"
        },
        {
          "name": "Dahua IPC-HFW1230SP 2MP",
          "description": "2Мп IP камера с ночным видением до 30м, объектив 3.6мм, H.265, влагозащита IP67",
          "price_uzs": 670000,
          "price_usd": 59,
          "usd_rate": 11333,
          "category": "ip_cameras"
        },
        {
          "name": "Hikvision DS-2CD2043G2-I 4MP",
          "description": "4Мп IP камера с EXIR подсветкой до 40м, объектив 2.8мм, H.265+, Smart Detection",
          "price_uzs": 980000,
          "price_usd": 86,
          "usd_rate": 11333,
          "category": "ip_cameras"
        },
        {
          "name": "HiLook IPC-T240H 4MP",
          "description": "4Мп купольная IP камера, объектив 2.8мм, ИК до 30м, поддержка PoE",
          "price_uzs": 770000,
          "price_usd": 68,
          "usd_rate": 11333,
          "category": "ip_cameras"
        },
        {
          "name": "Dahua IPC-HDW1431S 4MP",
          "description": "4Мп купольная IP камера, объектив 2.8мм, ИК до 30м, H.265+",
          "price_uzs": 810000,
          "price_usd": 71,
          "usd_rate": 11333,
          "category": "ip_cameras"
        },
        {
          "name": "Hikvision DS-2CD1323G0-IUF 2MP",
          "description": "2Мп IP камера с встроенным микрофоном, объектив 2.8мм, ИК до 30м",
          "price_uzs": 720000,
          "price_usd": 63,
          "usd_rate": 11333,
          "category": "ip_cameras"
        },
        {
          "name": "Ezviz C3WN 2MP Wi-Fi",
          "description": "2Мп Wi-Fi IP камера, объектив 2.8мм, ИК до 30м, влагозащита IP66",
          "price_uzs": 690000,
          "price_usd": 61,
          "usd_rate": 11333,
          "category": "ip_cameras"
        },
        {
          "name": "Imou Bullet Lite 4MP",
          "description": "4Мп IP камера, Wi-Fi, объектив 2.8мм, ночное видение до 30м, H.265",
          "price_uzs": 750000,
          "price_usd": 66,
          "usd_rate": 11333,
          "category": "ip_cameras"
        },
        {
          "name": "Dahua IPC-HFW2431S-S 4MP",
          "description": "4Мп IP камера, объектив 3.6мм, ИК до 30м, поддержка PoE, корпус металл",
          "price_uzs": 920000,
          "price_usd": 81,
          "usd_rate": 11333,
          "category": "ip_cameras"
        },
        {
          "name": "Hikvision DS-2CD1043G0-IUF 4MP",
          "description": "4Мп IP камера с микрофоном, объектив 2.8мм, ИК до 30м, металлический корпус",
          "price_uzs": 870000,
          "price_usd": 77,
          "usd_rate": 11333,
          "category": "ip_cameras"
        },
        
        # АНАЛОГОВЫЕ КАМЕРЫ (для дома)
        {
            "name": "Hikvision DS-2CE16D0T-IR 2MP",
            "description": "2Мп AHD камера с ИК подсветкой до 20м, объектив 2.8мм, пластиковый корпус",
            "price_uzs": 450000,
            "price_usd": 40,
            "usd_rate": 11250,
            "category": "analog"
        },
        {
            "name": "Dahua HAC-HFW1200TP-S3 2MP",
            "description": "2Мп HDCVI камера с ИК подсветкой до 40м, объектив 3.6мм, Smart IR",
            "price_uzs": 380000,
            "price_usd": 33,
            "usd_rate": 11515,
            "category": "analog"
        },
        {
            "name": "Hikvision DS-2CE16H0T-IT3F 5MP ColorVu",
            "description": "5Мп TurboHD камера с ИК подсветкой до 40м, ColorVu технология, цветное изображение ночью",
            "price_uzs": 680000,
            "price_usd": 60,
            "usd_rate": 11333,
            "category": "analog"
        },
        
        # РЕГИСТРАТОРЫ
        {
            "name": "Hikvision DS-7104HGHI-F1 4-канальный DVR",
            "description": "4-канальный гибридный видеорегистратор, поддержка 1080p, HDD до 6ТБ",
            "price_uzs": 1200000,
            "price_usd": 105,
            "usd_rate": 11429,
            "category": "dvr"
        },
        {
            "name": "Dahua XVR5108HS-4KL-X 8-канальный",
            "description": "8-канальный пентабридный видеорегистратор, поддержка 4K, HDD до 10ТБ",
            "price_uzs": 1850000,
            "price_usd": 162,
            "usd_rate": 11420,
            "category": "dvr"
        },
        {
            "name": "Hikvision DS-7616NI-K2 16-канальный NVR",
            "description": "16-канальный сетевой видеорегистратор с PoE, поддержка 4K, до 20ТБ",
            "price_uzs": 3200000,
            "price_usd": 280,
            "usd_rate": 11429,
            "category": "dvr"
        },
        
        # АКСЕССУАРЫ
        {
            "name": "Блок питания 12V 5A",
            "description": "Импульсный блок питания 12В 5А для камер видеонаблюдения, металлический корпус",
            "price_uzs": 150000,
            "price_usd": 13,
            "usd_rate": 11538,
            "category": "accessories"
        },
        {
            "name": "Кабель UTP Cat5e 305м",
            "description": "Кабель UTP категории 5e, 4 пары, 305 метров, медь, для наружной прокладки",
            "price_uzs": 850000,
            "price_usd": 75,
            "usd_rate": 11333,
            "category": "accessories"
        },
        {
            "name": "Коммутатор PoE 8 портов",
            "description": "8-портовый коммутатор PoE+ 10/100 Мбит/с, бюджет PoE 120Вт, металлический корпус",
            "price_uzs": 950000,
            "price_usd": 83,
            "usd_rate": 11446,
            "category": "accessories"
        },
        {
            "name": "Жесткий диск WD Purple 1TB",
            "description": "Жесткий диск 1ТБ для систем видеонаблюдения, 24/7 работа, SATA III",
            "price_uzs": 1200000,
            "price_usd": 105,
            "usd_rate": 11429,
            "category": "accessories"
        },
        {
            "name": "Крепление настенное поворотное",
            "description": "Универсальное настенное крепление для камер, металл, поворотное, до 3кг",
            "price_uzs": 85000,
            "price_usd": 7,
            "usd_rate": 12143,
            "category": "accessories"
        }
    ]
    
    print(f"📦 Добавление {len(products)} товаров...")
    
    added_count = 0
    for i, product_data in enumerate(products, 1):
        try:
            product = ProductCreate(**product_data)
            created_product = await product_service.create_product(product)
            print(f"✅ {i:2d}. {created_product.name}")
            added_count += 1
        except Exception as e:
            print(f"❌ {i:2d}. Ошибка: {product_data['name']} - {e}")
    
    # Статистика
    total_count = await product_service.count_products()
    ip_count = await product_service.count_products(category="ip_cameras")
    analog_count = await product_service.count_products(category="analog")
    dvr_count = await product_service.count_products(category="dvr")
    accessories_count = await product_service.count_products(category="accessories")
    
    print(f"\n📊 ИТОГО ДОБАВЛЕНО:")
    print(f"✅ Всего товаров: {total_count}")
    print(f"📱 IP камеры: {ip_count}")
    print(f"📹 Аналоговые: {analog_count}")
    print(f"💾 Регистраторы: {dvr_count}")
    print(f"🔌 Аксессуары: {accessories_count}")
    
    await db.disconnect()
    print(f"\n🎉 База данных готова! Можно тестировать бота.")


if __name__ == "__main__":
    asyncio.run(add_test_products())