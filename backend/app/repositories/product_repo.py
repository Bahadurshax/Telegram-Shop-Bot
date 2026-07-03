from ..database import get_products_collection
from ..models.product import ProductCreate, Product, ProductUpdate
from datetime import datetime, timezone
from typing import Optional, List
from bson import ObjectId

def _compact_attrs(product_dict: dict) -> dict:
  """Убирает None-поля из attrs перед записью в MongoDB"""
  attrs = product_dict.get("attrs")
  if isinstance(attrs, dict):
    compacted = {k: v for k, v in attrs.items() if v is not None}
    product_dict["attrs"] = compacted or None
  return product_dict


class ProductRepository:
  def __init__(self):
    self.collection = get_products_collection()

  async def create_product(self, product_data: ProductCreate) -> Product:
    product_dict = _compact_attrs(product_data.model_dump())

    product_dict["created_at"] = datetime.now(timezone.utc)
    product_dict["updated_at"] = datetime.now(timezone.utc)

    result = await self.collection.insert_one(product_dict)
    product_dict["_id"] = str(result.inserted_id)

    return Product(**product_dict)


  async def get_product(self, product_id: str) -> Optional[Product]:
    try:
      product_data = await self.collection.find_one({"_id": ObjectId(product_id)})
      if product_data:
        product_data["_id"] = str(product_data["_id"])
        return Product(**product_data)
    except Exception:
      print("Error fetching product:", product_id)

    return None


  async def get_products(self, category: Optional[str]=None, is_active: Optional[bool] = None, skip: int = 0, limit: int = 10) -> List[Product]:
    filter_dict = {}

    if is_active is not None:
      filter_dict["is_active"] = is_active

    if category and category != "all":
      filter_dict["category"] = category

    # skip(skip) - skips the first skip results of the cursor
    # limit(limit) - limits the number of results returned by the cursor
    cursor = self.collection.find(filter_dict).skip(skip).limit(limit).sort("created_at", -1)
    products = []

    async for product_data in cursor:
      product_data["_id"] = str(product_data["_id"])
      products.append(Product(**product_data))
    
    return products


  async def count_products(self, category: Optional[str]=None, is_active: Optional[bool]=None) -> int:
    filter_dict = {}
    if is_active is not None:
      filter_dict["is_active"] = is_active
      
    if category and category != "all":
      filter_dict["category"] = category
    
    return await self.collection.count_documents(filter_dict)


  async def update_product(self, product_id: str, update_data: ProductUpdate) -> bool:
    try:
      update_dict = {
        k: v for k, v in _compact_attrs(update_data.model_dump()).items() if v is not None
      }

      if not update_dict:
        return False
      
      update_dict["updated_at"] = datetime.now(timezone.utc)
      result = await self.collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_dict}
      )
      return result.modified_count > 0
    except:
      print("Error updating product:", product_id)
      return False


  async def delete_product(self, product_id: str) -> bool:
    return await self.update_product(product_id, ProductUpdate(is_active=False))


  async def get_categories(self) -> List[str]:
    categories = await self.collection.distinct("category", {"is_active": True})
    return categories

  async def search_products(self, query: str, skip: int = 0, limit: int = 10, is_active: Optional[bool] = None) -> List[Product]:
    filter_dict = {
      "$or": [
        {"name": {"$regex": query, "$options": "i"}},
        {"description": {"$regex": query, "$options": "i"}}
      ]
    }
    
    if is_active is not None:
      filter_dict["is_active"] = is_active

    cursor = self.collection.find(filter_dict).skip(skip).limit(limit)
    products = []
    async for product_data in cursor:
      product_data["_id"] = str(product_data["_id"])
      products.append(Product(**product_data))

    return products

  async def create_products_bulk(self, products_data: List[ProductCreate]) -> List[Product]:
    """Массовое создание товаров"""
    if not products_data:
      return []

    try:
      products_dict = []
      now = datetime.now(timezone.utc)

      for product_data in products_data:
        product_dict = _compact_attrs(product_data.model_dump())
        product_dict["created_at"] = now
        product_dict["updated_at"] = now
        products_dict.append(product_dict)

      result = await self.collection.insert_many(products_dict)

      created_products = []
      for i, inserted_id in enumerate(result.inserted_ids):
        products_dict[i]["_id"] = str(inserted_id)
        created_products.append(Product(**products_dict[i]))

      return created_products

    except Exception as e:
      print(f"[ERROR] Ошибка массового создания товаров: {str(e)}")
      raise
