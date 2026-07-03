from ..database import get_users_collection
from datetime import datetime, timezone
from ..models.user import User, UserCreate, ConsultationData, CartItem
from ..config import settings

class UserRepository:
  """
  A repository class for managing user-related database operations.
  """
  def __init__(self):
    self.collection = get_users_collection()
  
  #todo error handling
  async def create_or_update_user(self, telegram_user_id: int, username: str, first_name: str, last_name: str) -> User:
    existing_user = await self.collection.find_one({"telegram_user_id": telegram_user_id})

    if existing_user:
      await self.collection.update_one(
        {"telegram_user_id": telegram_user_id}, 
        {"$set": {
          "username": username,
          "first_name": first_name,
          "last_name": last_name,
          "updated_at": datetime.now(timezone.utc)
        }}
      )

      updated_user = await self.collection.find_one({ # fetches the updated user object
        "telegram_user_id": telegram_user_id
      })
      # converts the mongodb _id which is bson.ObjectId(not JSON-serializable) to string
      updated_user["_id"] = str(updated_user["_id"])
      # User - Pydantic model instance
      return User(**updated_user) # **updated_user unpacks the object into keyword arguments
    else:
      user_data = UserCreate(
        telegram_user_id=telegram_user_id,
        username=username,
        first_name=first_name,
        last_name=last_name
      )

      user_dict = user_data.model_dump() # generates a dictionary representation of the pydantic model
      user_dict["created_at"] = datetime.now(timezone.utc)
      user_dict["updated_at"] = datetime.now(timezone.utc)
      user_dict["cart"] = []
      user_dict["consultation_data"] = ConsultationData().model_dump()
      user_dict["consultations_count"] = 0
      user_dict["is_active"] = True

      result = await self.collection.insert_one(user_dict)
      user_dict["_id"] = str(result.inserted_id)

      return User(**user_dict)
    
  async def get_user(self, telegram_user_id: int) -> User:
    """Get user by Telegram ID"""
    user_data = await self.collection.find_one({"telegram_user_id": telegram_user_id})
    
    if user_data:
      user_data["_id"] = str(user_data["_id"])
      return User(**user_data)
    return None
  
  async def add_to_cart(self, telegram_user_id: int, product_id: str, quantity: int = 1) -> bool:
        """Добавить товар в корзину"""
        
        user = await self.get_user(telegram_user_id)
        if not user:
            return False
        
        # Проверяем лимит товаров в корзине
        total_items = sum(item.quantity for item in user.cart)
        if total_items >= settings.MAX_CART_ITEMS:
            return False
        
        # Ищем товар в корзине
        cart_updated = False
        for item in user.cart:
            if item.product_id == product_id:
                item.quantity += quantity
                cart_updated = True
                break
        
        # Если товара нет в корзине, добавляем
        if not cart_updated:
            user.cart.append(CartItem(product_id=product_id, quantity=quantity))
        
        # Сохраняем в базу
        cart_data = [item.model_dump() for item in user.cart]
        
        result = await self.collection.update_one(
            {"telegram_user_id": telegram_user_id},
            {"$set": {"cart": cart_data, "updated_at": datetime.now(timezone.utc)}}
        )
        
        return result.modified_count > 0
  
  async def remove_from_cart(self, telegram_user_id: int, product_id: str, quantity: int = 1) -> bool:
    """Убрать товар из корзины"""
    user = await self.get_user(telegram_user_id)
    if not user:
       return False

    updated_cart = []
    for item in user.cart:
      if item.product_id == product_id:
        if item.quantity > quantity:
          item.quantity -= quantity
          updated_cart.append(item)
      else:
        updated_cart.append(item)
    
    cart_data = [item.model_dump() for item in updated_cart]
    result = await self.collection.update_one(
       {"telegram_user_id": telegram_user_id},
       {"$set": {"cart": cart_data, "updated_at": datetime.now(timezone.utc)}}
    )
    return result.modified_count > 0
  

  async def clear_cart(self, telegram_user_id: int) -> bool:
    """Очистить корзину"""
    result = await self.collection.update_one(
       {"telegram_user_id": telegram_user_id},
       {"$set": {"cart": [], "updated_at": datetime.now(timezone.utc)}}
    )
    return result.modified_count > 0
  

  async def update_consultation_data(self, telegram_user_id: int, consultation_data: dict) -> bool:
     """Обновить данные консультации"""
     result = await self.collection.update_one(
        {"telegram_user_id": telegram_user_id},
        {"$set": {"consultation_data": consultation_data, "updated_at": datetime.now(timezone.utc)}}
     )
     return result.modified_count > 0
  

  async def complete_consultation(self, telegram_user_id: int) -> bool:
        """Завершить консультацию"""
        
        result = await self.collection.update_one(
            {"telegram_user_id": telegram_user_id},
            {
               "$inc": {"consultations_count": 1},
                "$set": {
                    "last_consultation": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }}
        )
        
        return result.modified_count > 0
  
  async def save_consultation_report(
      self,
      telegram_user_id: int,
      consultation_data: dict,
      recommendations: dict
  ) -> bool:
      
      report = {
          "date": datetime.now(timezone.utc),
          "consultation_data": consultation_data,
          "recommendations": {
              "product_ids": recommendations.get("product_ids", []),
              "explanation": recommendations.get("explanation", ""),
              "total_uzs": recommendations.get("total_uzs", 0),
              "total_usd": recommendations.get("total_usd", 0),
              "ai_response": recommendations.get("ai_response", ""),
              # Развёрнутое решение — контекст для диалогового консультанта
              "zones": recommendations.get("zones", []),
              "equipment": recommendations.get("equipment", []),
              "unmatched": recommendations.get("unmatched", []),
              "storage_summary": (recommendations.get("storage") or {}).get("summary", ""),
              "items": [
                  {
                      "product_id": item["product"].id,
                      "name": item["product"].name,
                      "quantity": item.get("quantity", 1),
                      "reason": item.get("reason", ""),
                  }
                  for item in recommendations.get("items", [])
              ],
          }
      }

      result = await self.collection.update_one(
          {"telegram_user_id": telegram_user_id},
          {
              "$push": {"consultation_reports": report},
              "$inc": {"consultations_count": 1},
              "$set": {
                  "last_consultation": datetime.now(timezone.utc),
                  "updated_at": datetime.now(timezone.utc)
              }
          }
      )

      return result.modified_count > 0

  # ------------------------------------------------------------------
  # Диалог с AI-консультантом (этап 2)
  # ------------------------------------------------------------------

  async def get_consultant_dialog(self, telegram_user_id: int) -> dict:
      """Получить текущий диалог с консультантом (context + messages)"""
      doc = await self.collection.find_one(
          {"telegram_user_id": telegram_user_id},
          {"consultant_dialog": 1},
      )
      return (doc or {}).get("consultant_dialog") or {}

  async def start_consultant_dialog(self, telegram_user_id: int, context: str) -> bool:
      """Начать новый диалог: сохранить контекст, очистить историю"""
      result = await self.collection.update_one(
          {"telegram_user_id": telegram_user_id},
          {"$set": {
              "consultant_dialog": {
                  "context": context,
                  "messages": [],
                  "started_at": datetime.now(timezone.utc),
              },
              "updated_at": datetime.now(timezone.utc),
          }}
      )
      return result.matched_count > 0

  async def append_consultant_dialog(
      self,
      telegram_user_id: int,
      user_text: str,
      assistant_text: str,
      limit: int = 30,
  ) -> bool:
      """Дописать пару сообщений в историю диалога (с обрезкой до limit)"""
      result = await self.collection.update_one(
          {"telegram_user_id": telegram_user_id},
          {
              "$push": {
                  "consultant_dialog.messages": {
                      "$each": [
                          {"role": "user", "text": user_text},
                          {"role": "assistant", "text": assistant_text},
                      ],
                      "$slice": -limit,
                  }
              },
              "$set": {"updated_at": datetime.now(timezone.utc)},
          }
      )
      return result.modified_count > 0
