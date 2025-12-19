"""
Módulo de acceso a datos y análisis estadístico
"""

import pandas as pd
from sqlalchemy import create_engine, text
from typing import Dict, List, Optional, Tuple
import numpy as np
from .config import DATABASE_URL, DB_CONFIG

# ⚠️ IMPORTANTE: Cambia 'gold' por el schema correcto de tu base de datos
# Ejecuta check_schema.py para ver los schemas disponibles
SCHEMA = "gold"  # Cambia esto según tu configuración


class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(
            DATABASE_URL,
            pool_size=DB_CONFIG["pool_size"],
            max_overflow=DB_CONFIG["max_overflow"],
            pool_timeout=DB_CONFIG["pool_timeout"],
            pool_recycle=DB_CONFIG["pool_recycle"],
        )
    
    def execute_query(self, query: str, params: Dict = None) -> pd.DataFrame:
        """Ejecuta una query y retorna un DataFrame"""
        with self.engine.connect() as conn:
            return pd.read_sql(text(query), conn, params=params)
    
    # ==================== QUERIES PRINCIPALES ====================
    
    def get_top_states_by_sales(self, start_date: str = None, end_date: str = None, limit: int = 10) -> pd.DataFrame:
        """Estados con más ventas"""
        query = f"""
        SELECT 
            c.customer_state as estado,
            COUNT(DISTINCT f.order_id) as total_ordenes,
            SUM(f.total) as ventas_totales,
            AVG(f.total) as promedio_venta
        FROM {SCHEMA}.fact_sales f
        JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
        JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
        WHERE 1=1
        """
        
        if start_date:
            query += f" AND cal.date_ymd >= '{start_date}'"
        if end_date:
            query += f" AND cal.date_ymd <= '{end_date}'"
        
        query += """
        GROUP BY c.customer_state
        ORDER BY ventas_totales DESC
        LIMIT :limit
        """
        
        return self.execute_query(query, {"limit": limit})
    
    def get_bottom_states_by_sales(self, start_date: str = None, end_date: str = None, limit: int = 10) -> pd.DataFrame:
        """Estados con menos ventas"""
        query = f"""
        SELECT 
            c.customer_state as estado,
            COUNT(DISTINCT f.order_id) as total_ordenes,
            SUM(f.total) as ventas_totales,
            AVG(f.total) as promedio_venta
        FROM {SCHEMA}.fact_sales f
        JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
        JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
        WHERE 1=1
        """
        
        if start_date:
            query += f" AND cal.date_ymd >= '{start_date}'"
        if end_date:
            query += f" AND cal.date_ymd <= '{end_date}'"
        
        query += """
        GROUP BY c.customer_state
        ORDER BY ventas_totales ASC
        LIMIT :limit
        """
        
        return self.execute_query(query, {"limit": limit})
    
    def get_top_product(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Producto más vendido"""
        query = f"""
        SELECT 
            p.product_id,
            p.product_category_name as categoria,
            COUNT(*) as unidades_vendidas,
            SUM(f.total) as ventas_totales,
            AVG(f.price) as precio_promedio
        FROM {SCHEMA}.fact_sales f
        JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
        JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
        WHERE 1=1
        """
        
        if start_date:
            query += f" AND cal.date_ymd >= '{start_date}'"
        if end_date:
            query += f" AND cal.date_ymd <= '{end_date}'"
        
        query += """
        GROUP BY p.product_id, p.product_category_name
        ORDER BY unidades_vendidas DESC
        LIMIT 1
        """
        
        return self.execute_query(query)
    
    def get_top_categories(self, start_date: str = None, end_date: str = None, limit: int = 10) -> pd.DataFrame:
        """Categorías más vendidas"""
        query = f"""
        SELECT 
            p.product_category_name as categoria,
            COUNT(*) as unidades_vendidas,
            SUM(f.total) as ventas_totales,
            AVG(f.total) as promedio_venta
        FROM {SCHEMA}.fact_sales f
        JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
        JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
        WHERE p.product_category_name IS NOT NULL
        """
        
        if start_date:
            query += f" AND cal.date_ymd >= '{start_date}'"
        if end_date:
            query += f" AND cal.date_ymd <= '{end_date}'"
        
        query += """
        GROUP BY p.product_category_name
        ORDER BY ventas_totales DESC
        LIMIT :limit
        """
        
        return self.execute_query(query, {"limit": limit})
    
    def get_top_seller(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Vendedor con más ventas"""
        query = f"""
        SELECT 
            s.seller_id,
            s.seller_city,
            s.seller_state,
            COUNT(DISTINCT f.order_id) as total_ordenes,
            SUM(f.total) as ventas_totales,
            AVG(f.total) as promedio_venta
        FROM {SCHEMA}.fact_sales f
        JOIN {SCHEMA}.dim_sellers s ON f.seller_key = s.seller_key
        JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
        WHERE 1=1
        """
        
        if start_date:
            query += f" AND cal.date_ymd >= '{start_date}'"
        if end_date:
            query += f" AND cal.date_ymd <= '{end_date}'"
        
        query += """
        GROUP BY s.seller_id, s.seller_city, s.seller_state
        ORDER BY ventas_totales DESC
        LIMIT 1
        """
        
        return self.execute_query(query)
    
    def get_top_customer(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Cliente con más compras"""
        query = f"""
        SELECT 
            c.customer_id,
            c.customer_city,
            c.customer_state,
            COUNT(DISTINCT f.order_id) as total_ordenes,
            SUM(f.total) as total_comprado,
            AVG(f.total) as promedio_compra
        FROM {SCHEMA}.fact_sales f
        JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
        JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
        WHERE 1=1
        """
        
        if start_date:
            query += f" AND cal.date_ymd >= '{start_date}'"
        if end_date:
            query += f" AND cal.date_ymd <= '{end_date}'"
        
        query += """
        GROUP BY c.customer_id, c.customer_city, c.customer_state
        ORDER BY total_comprado DESC
        LIMIT 1
        """
        
        return self.execute_query(query)
    
    # ==================== ESTADÍSTICAS ====================
    
    def get_statistics(
        self,
        metric: str = "total",  # total, price, freight_value
        group_by: str = None,  # customer_state, seller_state, product_category_name, etc.
        filter_value: str = None,
        start_date: str = None,
        end_date: str = None
    ) -> Dict:
        """
        Calcula estadísticas descriptivas para una métrica específica
        """
        # Construir query base
        query = f"""
        SELECT f.{metric} as valor
        FROM {SCHEMA}.fact_sales f
        JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
        JOIN {SCHEMA}.dim_sellers s ON f.seller_key = s.seller_key
        JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
        JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
        WHERE 1=1
        """
        
        # Agregar filtros
        if start_date:
            query += f" AND cal.date_ymd >= '{start_date}'"
        if end_date:
            query += f" AND cal.date_ymd <= '{end_date}'"
        
        if group_by and filter_value:
            if group_by == "customer_state":
                query += f" AND c.customer_state = '{filter_value}'"
            elif group_by == "seller_state":
                query += f" AND s.seller_state = '{filter_value}'"
            elif group_by == "customer_city":
                query += f" AND c.customer_city = '{filter_value}'"
            elif group_by == "seller_city":
                query += f" AND s.seller_city = '{filter_value}'"
            elif group_by == "product_category_name":
                query += f" AND p.product_category_name = '{filter_value}'"
        
        # Ejecutar query
        df = self.execute_query(query)
        
        if df.empty or df['valor'].isna().all():
            return {
                "media": 0,
                "mediana": 0,
                "moda": 0,
                "desviacion_std": 0,
                "q1": 0,
                "q2": 0,
                "q3": 0,
                "iqr": 0,
                "minimo": 0,
                "maximo": 0,
                "count": 0
            }
        
        values = df['valor'].dropna()
        
        # Calcular estadísticas
        try:
            mode_result = values.mode()
            moda = mode_result.iloc[0] if len(mode_result) > 0 else values.mean()
        except:
            moda = values.mean()
        
        q1, q2, q3 = values.quantile([0.25, 0.50, 0.75])
        
        return {
            "media": float(values.mean()),
            "mediana": float(values.median()),
            "moda": float(moda),
            "desviacion_std": float(values.std()),
            "q1": float(q1),
            "q2": float(q2),
            "q3": float(q3),
            "iqr": float(q3 - q1),
            "minimo": float(values.min()),
            "maximo": float(values.max()),
            "count": int(len(values))
        }
    
    # ==================== FILTROS ====================
    
    def get_available_states(self) -> List[str]:
        """Obtiene lista de estados disponibles"""
        query = f"SELECT DISTINCT customer_state FROM {SCHEMA}.dim_customers ORDER BY customer_state"
        df = self.execute_query(query)
        return df['customer_state'].tolist()
    
    def get_available_cities(self, state: str = None) -> List[str]:
        """Obtiene lista de ciudades disponibles"""
        query = f"SELECT DISTINCT customer_city FROM {SCHEMA}.dim_customers"
        if state:
            query += f" WHERE customer_state = '{state}'"
        query += " ORDER BY customer_city"
        df = self.execute_query(query)
        return df['customer_city'].tolist()
    
    def get_available_categories(self) -> List[str]:
        """Obtiene lista de categorías disponibles"""
        query = f"SELECT DISTINCT product_category_name FROM {SCHEMA}.dim_products WHERE product_category_name IS NOT NULL ORDER BY product_category_name"
        df = self.execute_query(query)
        return df['product_category_name'].tolist()
    
    def get_date_range(self) -> Tuple[str, str]:
        """Obtiene el rango de fechas disponible en la base de datos"""
        query = f"""
        SELECT 
            MIN(cal.date_ymd) as min_date,
            MAX(cal.date_ymd) as max_date
        FROM {SCHEMA}.fact_sales f
        JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
        """
        df = self.execute_query(query)
        return (str(df['min_date'].iloc[0]), str(df['max_date'].iloc[0]))
    
    def get_overview_metrics(self, start_date: str = None, end_date: str = None) -> Dict:
        """Métricas generales del dashboard"""
        query = f"""
        SELECT 
            COUNT(DISTINCT f.order_id) as total_ordenes,
            SUM(f.total) as ventas_totales,
            AVG(f.total) as ticket_promedio,
            COUNT(DISTINCT f.customer_key) as clientes_unicos,
            COUNT(DISTINCT f.seller_key) as vendedores_activos
        FROM {SCHEMA}.fact_sales f
        JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
        WHERE 1=1
        """
        
        if start_date:
            query += f" AND cal.date_ymd >= '{start_date}'"
        if end_date:
            query += f" AND cal.date_ymd <= '{end_date}'"
        
        df = self.execute_query(query)
        return df.iloc[0].to_dict()


# Instancia global
db = DatabaseManager()