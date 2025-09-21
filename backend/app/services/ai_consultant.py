from typing import List, Dict, Any
from anthropic import AsyncAnthropic

from ..config import settings
from ..models.product import Product
from .product_service import ProductService


class AIConsultantService:
    """Сервис AI-консультанта"""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.CLAUDE_API_KEY) if settings.CLAUDE_API_KEY else None
        self.product_service = ProductService()
    
    async def generate_recommendations(
        self,
        consultation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Генерация рекомендаций на основе ответов пользователя"""
        
        # Получаем все активные товары
        products = await self.product_service.get_products(limit=100)
        
        if not self.client:
            # Fallback без API - простые рекомендации
            return await self._generate_fallback_recommendations(consultation_data, products)
        
        try:
            # Формируем промпт для Claude
            prompt = self._build_consultation_prompt(consultation_data, products)
            
            # Запрос к Claude API
            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Парсим ответ и формируем рекомендации
            recommendations = await self._parse_ai_response(
                response.content[0].text,
                products,
                consultation_data
            )
            
            return recommendations
            
        except Exception as e:
            print(f"Ошибка AI консультанта: {e}")
            # Fallback на простые рекомендации
            return await self._generate_fallback_recommendations(consultation_data, products)
    
    def _build_consultation_prompt(
        self, 
        consultation_data: Dict[str, Any], 
        products: List[Product]
    ) -> str:
        """Построение промпта для Claude"""
        
        # Данные консультации
        location = consultation_data.get('location_type', 'не указано')
        cameras_count = consultation_data.get('cameras_count', 'не указано')
        need_audio = consultation_data.get('need_audio', False)
        distance = consultation_data.get('distance', 'не указано')
        budget = consultation_data.get('budget', 'не указано')
        
        # Список товаров
        products_info = ""
        for product in products:
            products_info += f"""
            ID: {product.id}
            Название: {product.name}
            Описание: {product.description}
            Цена: {product.price_uzs:,.0f} сум ({product.price_usd:.0f} $)
            Категория: {product.category}
            ---
            """
        
        prompt = f"""
Ты - эксперт по системам видеонаблюдения. Нужно подобрать оптимальное решение для клиента.

ПОТРЕБНОСТИ КЛИЕНТА:
- Место установки: {location}
- Количество камер: {cameras_count}
- Нужна запись звука: {'Да' if need_audio else 'Нет'}
- Дальность обзора: {distance}
- Бюджет: {budget}

ДОСТУПНЫЕ ТОВАРЫ:
{products_info}

ЗАДАЧА:
1. Проанализируй потребности клиента
2. Выбери 2-4 наиболее подходящих товара по ID
3. Объясни почему именно эти товары подходят
4. Рассчитай общую стоимость

ФОРМАТ ОТВЕТА:
РЕКОМЕНДАЦИИ:
[ID товара] - [краткое обоснование]
[ID товара] - [краткое обоснование]

ОБОСНОВАНИЕ:
[Подробное объяснение выбора с учетом потребностей клиента]

ИТОГОВАЯ_СТОИМОСТЬ:
[сумма в сумах] сум ([сумма в долларах] $)

Отвечай на русском языке, будь кратким но информативным.
"""
        return prompt
    
    async def _parse_ai_response(
        self,
        ai_response: str,
        products: List[Product],
        consultation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Парсинг ответа AI и формирование рекомендаций"""
        
        # Создаем словарь продуктов для быстрого поиска
        products_dict = {product.id: product for product in products}
        
        recommended_products = []
        explanation = ""
        total_uzs = 0
        total_usd = 0
        
        try:
            lines = ai_response.strip().split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if 'РЕКОМЕНДАЦИИ:' in line:
                    current_section = 'recommendations'
                    continue
                elif 'ОБОСНОВАНИЕ:' in line:
                    current_section = 'explanation'
                    continue
                elif 'ИТОГОВАЯ_СТОИМОСТЬ:' in line:
                    current_section = 'total'
                    continue
                
                if current_section == 'recommendations' and line and not line.startswith('['):
                    # Пытаемся извлечь ID товара из строки
                    for product_id in products_dict.keys():
                        if product_id in line:
                            product = products_dict[product_id]
                            if product not in recommended_products:
                                recommended_products.append(product)
                                total_uzs += product.price_uzs
                                total_usd += product.price_usd
                            break
                
                elif current_section == 'explanation' and line:
                    explanation += line + " "
            
        except Exception as e:
            print(f"Ошибка парсинга AI ответа: {e}")
            # Fallback
            recommended_products = products[:2]
            total_uzs = sum(p.price_uzs for p in recommended_products)
            total_usd = sum(p.price_usd for p in recommended_products)
            explanation = "Подобраны товары согласно вашим требованиям."
        
        return {
            "products": recommended_products,
            "explanation": explanation.strip(),
            "total_uzs": total_uzs,
            "total_usd": total_usd,
            "consultation_summary": self._generate_consultation_summary(consultation_data),
            "ai_response": ai_response
        }
    
    async def _generate_fallback_recommendations(
        self,
        consultation_data: Dict[str, Any],
        products: List[Product]
    ) -> Dict[str, Any]:
        """Простые рекомендации без AI"""
        
        # Логика подбора товаров на основе правил
        recommended_products = []
        
        # Фильтруем по категориям
        cameras_count = consultation_data.get('cameras_count', 0)
        location = consultation_data.get('location_type', '')
        
        # IP камеры для офиса/организации, аналоговые для дома
        if location == 'organization':
            ip_cameras = [p for p in products if p.category == 'ip_cameras']
            recommended_products.extend(ip_cameras[:2])
        else:
            analog_cameras = [p for p in products if p.category == 'analog']
            if analog_cameras:
                recommended_products.extend(analog_cameras[:2])
            else:
                ip_cameras = [p for p in products if p.category == 'ip_cameras']
                recommended_products.extend(ip_cameras[:2])
        
        # Добавляем регистратор
        dvr_products = [p for p in products if p.category == 'dvr']
        if dvr_products:
            recommended_products.append(dvr_products[0])
        
        # Ограничиваем количество
        recommended_products = recommended_products[:3]
        
        total_uzs = sum(p.price_uzs for p in recommended_products)
        total_usd = sum(p.price_usd for p in recommended_products)
        
        explanation = f"Подобраны товары для {location or 'вашего объекта'}. "
        if cameras_count:
            explanation += f"Учтено количество камер: {cameras_count}. "
        
        return {
            "products": recommended_products,
            "explanation": explanation,
            "total_uzs": total_uzs,
            "total_usd": total_usd,
            "consultation_summary": self._generate_consultation_summary(consultation_data),
            "ai_response": "Рекомендации сгенерированы автоматически"
        }
    
    def _generate_consultation_summary(self, consultation_data: Dict[str, Any]) -> str:
        """Генерация сводки консультации"""
        
        location_map = {
            'home': 'Дом',
            'office': 'Офис', 
            'organization': 'Организация'
        }
        
        cameras_map = {
            '1_4': '1-4 камеры',
            '5_8': '5-8 камер',
            '9_16': '9-16 камер',
            'more': 'Более 16 камер'
        }
        
        distance_map = {
            '10m': 'До 10 метров',
            '30m': 'До 30 метров',
            '50m': 'До 50 метров',
            '100m': 'Более 50 метров'
        }
        
        budget_map = {
            '500k': 'До 500 тыс сум',
            '1m': '500 тыс - 1 млн',
            '2m': '1-2 млн',
            'more': 'Более 2 млн'
        }
        
        location = location_map.get(consultation_data.get('location_type', ''), 'Не указано')
        cameras = cameras_map.get(consultation_data.get('cameras_count', ''), 'Не указано')
        audio = 'Да' if consultation_data.get('need_audio') else 'Нет'
        distance = distance_map.get(consultation_data.get('distance', ''), 'Не указано')
        budget = budget_map.get(consultation_data.get('budget', ''), 'Не указано')
        
        return f"""Место установки: {location}
Количество камер: {cameras}
Запись звука: {audio}
Дальность обзора: {distance}
Бюджет: {budget}"""
