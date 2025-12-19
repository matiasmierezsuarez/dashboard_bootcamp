import os
from typing import List
import reflex as rx
import asyncpg
from asyncpg import Pool
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class SalesItem(BaseModel):
    """Item de ventas simplificado."""
    
    order_id: str
    order_item_id: int
    price: float
    freight_value: float
    total: float
    customer_city: str
    customer_state: str
    seller_city: str
    seller_state: str
    product_category_name: str
    product_weight_g: int
    status: str
    status_group: str
    purchase_date: str
    year: int
    month: int
    month_name: str


class TableState(rx.State):
    """Estado de la tabla con conexión a Neon PostgreSQL."""

    items: List[SalesItem] = []
    search_value: str = ""
    sort_value: str = ""
    sort_reverse: bool = False

    total_items: int = 0
    offset: int = 0
    limit: int = 12

    _db_pool: Pool = None
    error_message: str = ""

    async def get_db_pool(self) -> Pool:
        """Obtiene o crea el pool de conexiones a Neon."""
        if self._db_pool is None:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("DATABASE_URL no está configurada en el archivo .env")
            
            self._db_pool = await asyncpg.create_pool(
                database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
        return self._db_pool

    @rx.event
    async def load_entries(self):
        """Carga ventas con datos enriquecidos desde Neon."""
        try:
            pool = await self.get_db_pool()
            
            async with pool.acquire() as conn:
                print("🔍 Conectando a Neon y cargando datos...")
                
                # Reducido a 50 registros para evitar problemas de serialización
                query = """
                    SELECT 
                        f.order_id,
                        f.order_item_id,
                        f.price,
                        f.freight_value,
                        f.total,
                        c.customer_city,
                        c.customer_state,
                        s.seller_city,
                        s.seller_state,
                        p.product_category_name,
                        p.product_weight_g,
                        st.status,
                        st.status_group,
                        cal.date_ymd as purchase_date,
                        cal.date_year as year,
                        cal.date_month as month,
                        cal.month_name
                    FROM gold.fact_sales f
                    LEFT JOIN gold.dim_customers c ON f.customer_key = c.customer_key
                    LEFT JOIN gold.dim_sellers s ON f.seller_key = s.seller_key
                    LEFT JOIN gold.dim_products p ON f.product_key = p.product_key
                    LEFT JOIN gold.dim_status st ON f.status_key = st.status_key
                    LEFT JOIN gold.dim_calendar cal ON f.date_purchase_key = cal.date_key
                    ORDER BY cal.date_ymd DESC
                    LIMIT 20
                """
                
                rows = await conn.fetch(query)
                print(f"📊 Query ejecutada, {len(rows)} filas obtenidas")
                
                # Limpiar items existentes primero
                self.items = []
                
                # Crear lista temporal
                new_items = []
                for row in rows:
                    item = SalesItem(
                        order_id=str(row['order_id'] or 'N/A'),
                        order_item_id=int(row['order_item_id'] or 0),
                        price=float(row['price'] or 0.0),
                        freight_value=float(row['freight_value'] or 0.0),
                        total=float(row['total'] or 0.0),
                        customer_city=str(row['customer_city'] or 'N/A'),
                        customer_state=str(row['customer_state'] or 'N/A'),
                        seller_city=str(row['seller_city'] or 'N/A'),
                        seller_state=str(row['seller_state'] or 'N/A'),
                        product_category_name=str(row['product_category_name'] or 'Sin categoría'),
                        product_weight_g=int(row['product_weight_g'] or 0),
                        status=str(row['status'] or 'N/A'),
                        status_group=str(row['status_group'] or 'N/A'),
                        purchase_date=str(row['purchase_date'] or 'N/A'),
                        year=int(row['year'] or 0),
                        month=int(row['month'] or 0),
                        month_name=str(row['month_name'] or 'N/A')
                    )
                    new_items.append(item)
                
                # Asignar de una vez
                self.items = new_items
                self.total_items = len(self.items)
                self.error_message = ""
                print(f"✅ Cargados {self.total_items} registros desde Neon")
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error cargando datos: {error_msg}")
            self.error_message = error_msg
            self.items = []
            self.total_items = 0

    @rx.event
    def set_search_value(self, value: str):
        self.search_value = value
        self.offset = 0

    @rx.event
    def set_sort_value(self, value: str):
        self.sort_value = value
        self.offset = 0

    @rx.event
    def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse

    @rx.event  
    def prev_page(self):
        if self.page_number > 1:
            self.offset = max(0, self.offset - self.limit)

    @rx.event
    def next_page(self):
        if self.page_number < self.total_pages:
            self.offset = min(
                (self.total_pages - 1) * self.limit,
                self.offset + self.limit
            )

    @rx.event
    def first_page(self):
        self.offset = 0

    @rx.event
    def last_page(self):
        if self.total_pages > 1:
            self.offset = (self.total_pages - 1) * self.limit

    def _get_filtered_items(self) -> List[SalesItem]:
        """Método auxiliar para filtrar items."""
        if not self.search_value:
            return self.items
        
        search_value = self.search_value.lower()
        filtered = []
        
        for item in self.items:
            if (search_value in item.order_id.lower() or
                search_value in item.customer_city.lower() or
                search_value in item.customer_state.lower() or
                search_value in item.seller_city.lower() or
                search_value in item.seller_state.lower() or
                search_value in item.product_category_name.lower() or
                search_value in item.status.lower() or
                search_value in item.status_group.lower() or
                search_value in item.month_name.lower()):
                filtered.append(item)
        
        return filtered

    def _get_sorted_items(self, items: List[SalesItem]) -> List[SalesItem]:
        """Método auxiliar para ordenar items."""
        if not self.sort_value:
            return items
        
        numeric_fields = ["price", "freight_value", "total", "product_weight_g", "year", "month"]
        
        if self.sort_value in numeric_fields:
            return sorted(
                items,
                key=lambda x: getattr(x, self.sort_value),
                reverse=self.sort_reverse
            )
        else:
            return sorted(
                items,
                key=lambda x: getattr(x, self.sort_value).lower(),
                reverse=self.sort_reverse
            )

    @rx.var
    def get_current_page(self) -> List[SalesItem]:
        """Obtiene la página actual de items."""
        # Filtrar
        filtered = self._get_filtered_items()
        
        # Ordenar
        sorted_items = self._get_sorted_items(filtered)
        
        # Paginar
        start = self.offset
        end = start + self.limit
        return sorted_items[start:end]

    @rx.var
    def filtered_total(self) -> int:
        """Total de items filtrados."""
        return len(self._get_filtered_items())

    @rx.var
    def page_number(self) -> int:
        return (self.offset // self.limit) + 1

    @rx.var
    def total_pages(self) -> int:
        total = self.filtered_total
        if total == 0:
            return 1
        return (total + self.limit - 1) // self.limit
    
    