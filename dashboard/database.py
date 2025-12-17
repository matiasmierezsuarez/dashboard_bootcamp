"""
Módulo de acceso a datos y análisis estadístico
VERSIÓN MEJORADA: Soporte completo para filtros globales (estado, categoría, fechas)
INCLUYE: Métodos de análisis temporal + SISTEMA DE CACHÉ
"""

import pandas as pd
from sqlalchemy import create_engine, text
from typing import Dict, List, Optional, Tuple
import numpy as np
from .config import DATABASE_URL, DB_CONFIG
from functools import lru_cache
import hashlib, json

SCHEMA = "gold"


def _make_cache_key(prefix: str, **kwargs) -> str:
    raw = prefix + json.dumps(kwargs, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()


class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(
            DATABASE_URL,
            pool_size=DB_CONFIG["pool_size"],
            max_overflow=DB_CONFIG["max_overflow"],
            pool_timeout=DB_CONFIG["pool_timeout"],
            pool_recycle=DB_CONFIG["pool_recycle"],
        )
        self._cache = {}
    
    def _cached(self, key: str, fn):
        if key in self._cache:
            return self._cache[key]
        result = fn()
        self._cache[key] = result
        return result
    
    def execute_query(self, query: str, params: Dict = None) -> pd.DataFrame:
        """Ejecuta una query y retorna un DataFrame"""
        with self.engine.connect() as conn:
            return pd.read_sql(text(query), conn, params=params)
    
    def _build_filter_conditions(
        self,
        start_date: str = None,
        end_date: str = None,
        state_filter: str = None,
        category_filter: str = None,
        base_alias: str = "f"
    ) -> str:
        """
        Construye condiciones WHERE comunes para filtros globales
        
        Args:
            start_date: Fecha inicio
            end_date: Fecha fin
            state_filter: Estado del cliente
            category_filter: Categoría de producto
            base_alias: Alias de la tabla fact_sales
        """
        conditions = []
        
        if start_date:
            conditions.append(f"cal.date_ymd >= '{start_date}'")
        if end_date:
            conditions.append(f"cal.date_ymd <= '{end_date}'")
        if state_filter:
            conditions.append(f"c.customer_state = '{state_filter}'")
        if category_filter:
            conditions.append(f"p.product_category_name = '{category_filter}'")
        
        return " AND " + " AND ".join(conditions) if conditions else ""
    
    # ==================== QUERIES CON FILTROS GLOBALES + CACHÉ ====================
    
    def get_top_states_by_sales(
        self,
        start_date: str = None,
        end_date: str = None,
        limit: int = 10,
        state_filter: str = None,
        category_filter: str = None
    ) -> pd.DataFrame:
        """Estados con más ventas - CON FILTROS GLOBALES + CACHÉ"""
        key = _make_cache_key(
            "top_states",
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            state=state_filter,
            category=category_filter,
        )
        
        def _query():
            query = f"""
            SELECT 
                c.customer_state as estado,
                COUNT(DISTINCT f.order_id) as total_ordenes,
                SUM(f.total) as ventas_totales,
                AVG(f.total) as promedio_venta
            FROM {SCHEMA}.fact_sales f
            JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
            JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
            JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
            WHERE 1=1
            {self._build_filter_conditions(start_date, end_date, state_filter, category_filter)}
            GROUP BY c.customer_state
            ORDER BY ventas_totales DESC
            LIMIT :limit
            """
            return self.execute_query(query, {"limit": limit})
        
        return self._cached(key, _query)
    
    def get_bottom_states_by_sales(
        self,
        start_date: str = None,
        end_date: str = None,
        limit: int = 10,
        state_filter: str = None,
        category_filter: str = None
    ) -> pd.DataFrame:
        """Estados con menos ventas - CON FILTROS GLOBALES + CACHÉ"""
        key = _make_cache_key(
            "bottom_states",
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            state=state_filter,
            category=category_filter,
        )
        
        def _query():
            query = f"""
            SELECT 
                c.customer_state as estado,
                COUNT(DISTINCT f.order_id) as total_ordenes,
                SUM(f.total) as ventas_totales,
                AVG(f.total) as promedio_venta
            FROM {SCHEMA}.fact_sales f
            JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
            JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
            JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
            WHERE 1=1
            {self._build_filter_conditions(start_date, end_date, state_filter, category_filter)}
            GROUP BY c.customer_state
            ORDER BY ventas_totales ASC
            LIMIT :limit
            """
            return self.execute_query(query, {"limit": limit})
        
        return self._cached(key, _query)
    
    def get_top_product(
        self,
        start_date: str = None,
        end_date: str = None,
        state_filter: str = None,
        category_filter: str = None
    ) -> pd.DataFrame:
        """Producto más vendido - CON FILTROS GLOBALES + CACHÉ"""
        key = _make_cache_key(
            "top_product",
            start_date=start_date,
            end_date=end_date,
            state=state_filter,
            category=category_filter,
        )
        
        def _query():
            query = f"""
            SELECT 
                p.product_id,
                p.product_category_name as categoria,
                COUNT(*) as unidades_vendidas,
                SUM(f.total) as ventas_totales,
                AVG(f.price) as precio_promedio
            FROM {SCHEMA}.fact_sales f
            JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
            JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
            JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
            WHERE 1=1
            {self._build_filter_conditions(start_date, end_date, state_filter, category_filter)}
            GROUP BY p.product_id, p.product_category_name
            ORDER BY unidades_vendidas DESC
            LIMIT 1
            """
            return self.execute_query(query)
        
        return self._cached(key, _query)
    
    def get_top_categories(
        self,
        start_date: str = None,
        end_date: str = None,
        limit: int = 10,
        state_filter: str = None,
        category_filter: str = None
    ) -> pd.DataFrame:
        """Categorías más vendidas - CON FILTROS GLOBALES + CACHÉ"""
        key = _make_cache_key(
            "top_categories",
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            state=state_filter,
            category=category_filter,
        )
        
        def _query():
            query = f"""
            SELECT 
                p.product_category_name as categoria,
                COUNT(*) as unidades_vendidas,
                SUM(f.total) as ventas_totales,
                AVG(f.total) as promedio_venta
            FROM {SCHEMA}.fact_sales f
            JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
            JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
            JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
            WHERE p.product_category_name IS NOT NULL
            {self._build_filter_conditions(start_date, end_date, state_filter, category_filter)}
            GROUP BY p.product_category_name
            ORDER BY ventas_totales DESC
            LIMIT :limit
            """
            return self.execute_query(query, {"limit": limit})
        
        return self._cached(key, _query)
    
    def get_top_seller(
        self,
        start_date: str = None,
        end_date: str = None,
        state_filter: str = None,
        category_filter: str = None
    ) -> pd.DataFrame:
        """Vendedor con más ventas - CON FILTROS GLOBALES + CACHÉ"""
        key = _make_cache_key(
            "top_seller",
            start_date=start_date,
            end_date=end_date,
            state=state_filter,
            category=category_filter,
        )
        
        def _query():
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
            JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
            JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
            JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
            WHERE 1=1
            {self._build_filter_conditions(start_date, end_date, state_filter, category_filter)}
            GROUP BY s.seller_id, s.seller_city, s.seller_state
            ORDER BY ventas_totales DESC
            LIMIT 1
            """
            return self.execute_query(query)
        
        return self._cached(key, _query)
    
    def get_top_customer(
        self,
        start_date: str = None,
        end_date: str = None,
        state_filter: str = None,
        category_filter: str = None
    ) -> pd.DataFrame:
        """Cliente con más compras - CON FILTROS GLOBALES + CACHÉ"""
        key = _make_cache_key(
            "top_customer",
            start_date=start_date,
            end_date=end_date,
            state=state_filter,
            category=category_filter,
        )
        
        def _query():
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
            JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
            JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
            WHERE 1=1
            {self._build_filter_conditions(start_date, end_date, state_filter, category_filter)}
            GROUP BY c.customer_id, c.customer_city, c.customer_state
            ORDER BY total_comprado DESC
            LIMIT 1
            """
            return self.execute_query(query)
        
        return self._cached(key, _query)
    
    def get_overview_metrics(
        self,
        start_date: str = None,
        end_date: str = None,
        state_filter: str = None,
        category_filter: str = None
    ) -> Dict:
        """Métricas generales del dashboard - CON FILTROS GLOBALES + CACHÉ"""
        key = _make_cache_key(
            "overview",
            start_date=start_date,
            end_date=end_date,
            state=state_filter,
            category=category_filter,
        )
        
        def _query():
            query = f"""
            SELECT 
                COUNT(DISTINCT f.order_id) as total_ordenes,
                SUM(f.total) as ventas_totales,
                AVG(f.total) as ticket_promedio,
                COUNT(DISTINCT f.customer_key) as clientes_unicos,
                COUNT(DISTINCT f.seller_key) as vendedores_activos
            FROM {SCHEMA}.fact_sales f
            JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
            JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
            JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
            WHERE 1=1
            {self._build_filter_conditions(start_date, end_date, state_filter, category_filter)}
            """
            df = self.execute_query(query)
            return df.iloc[0].to_dict() if not df.empty else {
                'total_ordenes': 0,
                'ventas_totales': 0,
                'ticket_promedio': 0,
                'clientes_unicos': 0,
                'vendedores_activos': 0
            }
        
        return self._cached(key, _query)
    
    # ==================== ESTADÍSTICAS CON FILTROS GLOBALES + CACHÉ ====================
    
    def get_statistics(
        self,
        metric: str = "total",
        group_by: str = None,
        filter_value: str = None,
        start_date: str = None,
        end_date: str = None,
        state_filter: str = None,
        category_filter: str = None
    ) -> Dict:
        """Calcula estadísticas descriptivas - CON FILTROS GLOBALES + CACHÉ"""
        key = _make_cache_key(
            "statistics",
            metric=metric,
            group_by=group_by,
            filter_value=filter_value,
            start_date=start_date,
            end_date=end_date,
            state=state_filter,
            category=category_filter,
        )
        
        def _query():
            query = f"""
            SELECT f.{metric} as valor
            FROM {SCHEMA}.fact_sales f
            JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
            JOIN {SCHEMA}.dim_sellers s ON f.seller_key = s.seller_key
            JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
            JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
            WHERE 1=1
            {self._build_filter_conditions(start_date, end_date, state_filter, category_filter)}
            """
            
            # Filtros adicionales específicos para estadísticas
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
        
        return self._cached(key, _query)
    
    # ==================== QUERIES DINÁMICAS PLOTLY CON FILTROS GLOBALES + CACHÉ ====================
    
    def get_sales_by_state_dynamic(
        self,
        start_date: str = None,
        end_date: str = None,
        metric: str = "total_sales",
        limit: int = 10,
        state_filter: str = None,
        category_filter: str = None
    ) -> List[Dict]:
        """Query dinámica para ventas por estado - CON FILTROS GLOBALES + CACHÉ"""
        key = _make_cache_key(
            "sales_state_dynamic",
            start_date=start_date,
            end_date=end_date,
            metric=metric,
            limit=limit,
            state=state_filter,
            category=category_filter,
        )
        
        def _query():
            metric_mapping = {
                "total_sales": "SUM(f.total)",
                "avg_sales": "AVG(f.total)",
                "total_orders": "COUNT(DISTINCT f.order_id)",
                "avg_ticket": "AVG(f.total)"
            }
            
            metric_sql = metric_mapping.get(metric, metric_mapping["total_sales"])
            
            query = f"""
            SELECT 
                c.customer_state as state,
                {metric_sql} as total_sales,
                AVG(f.total) as avg_sales,
                COUNT(DISTINCT f.order_id) as total_orders,
                AVG(f.total) as avg_ticket
            FROM {SCHEMA}.fact_sales f
            JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
            JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
            JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
            WHERE 1=1
            {self._build_filter_conditions(start_date, end_date, state_filter, category_filter)}
            GROUP BY c.customer_state
            ORDER BY {metric_sql} DESC
            LIMIT :limit
            """
            
            df = self.execute_query(query, {"limit": limit})
            return df.to_dict('records') if not df.empty else []
        
        return self._cached(key, _query)
    
    def get_sales_by_city_dynamic(
        self,
        start_date: str = None,
        end_date: str = None,
        metric: str = "total_sales",
        limit: int = 10,
        state_filter: str = None,
        category_filter: str = None
    ) -> List[Dict]:
        """Query dinámica para ventas por ciudad - CON FILTROS GLOBALES + CACHÉ"""
        key = _make_cache_key(
            "sales_city_dynamic",
            start_date=start_date,
            end_date=end_date,
            metric=metric,
            limit=limit,
            state=state_filter,
            category=category_filter,
        )
        
        def _query():
            metric_mapping = {
                "total_sales": "SUM(f.total)",
                "avg_sales": "AVG(f.total)",
                "total_orders": "COUNT(DISTINCT f.order_id)",
                "avg_ticket": "AVG(f.total)"
            }
            
            metric_sql = metric_mapping.get(metric, metric_mapping["total_sales"])
            
            query = f"""
            SELECT 
                c.customer_city as city,
                c.customer_state as state,
                {metric_sql} as total_sales,
                AVG(f.total) as avg_sales,
                COUNT(DISTINCT f.order_id) as total_orders,
                AVG(f.total) as avg_ticket
            FROM {SCHEMA}.fact_sales f
            JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
            JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
            JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
            WHERE 1=1
            {self._build_filter_conditions(start_date, end_date, state_filter, category_filter)}
            GROUP BY c.customer_city, c.customer_state
            ORDER BY {metric_sql} DESC
            LIMIT :limit
            """
            
            df = self.execute_query(query, {"limit": limit})
            return df.to_dict('records') if not df.empty else []
        
        return self._cached(key, _query)
    
    def get_sales_by_category_dynamic(
        self,
        start_date: str = None,
        end_date: str = None,
        metric: str = "total_sales",
        limit: int = 10,
        state_filter: str = None,
        category_filter: str = None
    ) -> List[Dict]:
        """Query dinámica para ventas por categoría - CON FILTROS GLOBALES + CACHÉ"""
        key = _make_cache_key(
            "sales_category_dynamic",
            start_date=start_date,
            end_date=end_date,
            metric=metric,
            limit=limit,
            state=state_filter,
            category=category_filter,
        )
        
        def _query():
            metric_mapping = {
                "total_sales": "SUM(f.total)",
                "avg_sales": "AVG(f.total)",
                "total_orders": "COUNT(DISTINCT f.order_id)",
                "avg_ticket": "AVG(f.total)"
            }
            
            metric_sql = metric_mapping.get(metric, metric_mapping["total_sales"])
            
            query = f"""
            SELECT 
                p.product_category_name as category,
                {metric_sql} as total_sales,
                AVG(f.total) as avg_sales,
                COUNT(DISTINCT f.order_id) as total_orders,
                AVG(f.total) as avg_ticket,
                COUNT(DISTINCT p.product_id) as total_products
            FROM {SCHEMA}.fact_sales f
            JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
            JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
            JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
            WHERE p.product_category_name IS NOT NULL
            {self._build_filter_conditions(start_date, end_date, state_filter, category_filter)}
            GROUP BY p.product_category_name
            ORDER BY {metric_sql} DESC
            LIMIT :limit
            """
            
            df = self.execute_query(query, {"limit": limit})
            return df.to_dict('records') if not df.empty else []
        
        return self._cached(key, _query)
    
    def get_sales_by_seller_dynamic(
        self,
        start_date: str = None,
        end_date: str = None,
        metric: str = "total_sales",
        limit: int = 10,
        state_filter: str = None,
        category_filter: str = None
    ) -> List[Dict]:
        """Query dinámica para ventas por vendedor - CON FILTROS GLOBALES + CACHÉ"""
        key = _make_cache_key(
            "sales_seller_dynamic",
            start_date=start_date,
            end_date=end_date,
            metric=metric,
            limit=limit,
            state=state_filter,
            category=category_filter,
        )
        
        def _query():
            metric_mapping = {
                "total_sales": "SUM(f.total)",
                "avg_sales": "AVG(f.total)",
                "total_orders": "COUNT(DISTINCT f.order_id)",
                "avg_ticket": "AVG(f.total)"
            }
            
            metric_sql = metric_mapping.get(metric, metric_mapping["total_sales"])
            
            query = f"""
            SELECT 
                s.seller_id,
                s.seller_state as state,
                s.seller_city as city,
                {metric_sql} as total_sales,
                AVG(f.total) as avg_sales,
                COUNT(DISTINCT f.order_id) as total_orders,
                AVG(f.total) as avg_ticket,
                COUNT(DISTINCT f.customer_key) as unique_customers
            FROM {SCHEMA}.fact_sales f
            JOIN {SCHEMA}.dim_sellers s ON f.seller_key = s.seller_key
            JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
            JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
            JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
            WHERE 1=1
            {self._build_filter_conditions(start_date, end_date, state_filter, category_filter)}
            GROUP BY s.seller_id, s.seller_state, s.seller_city
            ORDER BY {metric_sql} DESC
            LIMIT :limit
            """
            
            df = self.execute_query(query, {"limit": limit})
            return df.to_dict('records') if not df.empty else []
        
        return self._cached(key, _query)
    
    # ==================== ANÁLISIS TEMPORAL + CACHÉ ====================
    
    def get_sales_by_year(
        self,
        metric: str = "avg_sales",
        state_filter: str = None,
        category_filter: str = None
    ) -> List[Dict]:
        """Obtiene ventas agrupadas por año - CON FILTROS GLOBALES + CACHÉ"""
        key = _make_cache_key(
            "sales_year",
            metric=metric,
            state=state_filter,
            category=category_filter,
        )
        
        def _query():
            allowed_metrics = {"avg_sales", "sum_sales", "std_sales"}
            if metric not in allowed_metrics:
                metric_used = "avg_sales"
            else:
                metric_used = metric
            
            query = f"""
            SELECT 
                cal.date_year,
                ROUND(AVG(f.total), 2) AS avg_sales,
                ROUND(SUM(f.total), 2) AS sum_sales,
                ROUND(STDDEV(f.total), 2) AS std_sales
            FROM {SCHEMA}.fact_sales f
            INNER JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
            INNER JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
            INNER JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
            WHERE 1=1
            """
            
            if state_filter:
                query += f" AND c.customer_state = '{state_filter}'"
            if category_filter:
                query += f" AND p.product_category_name = '{category_filter}'"
            
            query += f"""
            GROUP BY cal.date_year
            ORDER BY cal.date_year, {metric_used} DESC
            """
            
            df = self.execute_query(query)
            return df.to_dict('records') if not df.empty else []
        
        return self._cached(key, _query)
    
    def get_sales_by_year_month(
        self,
        metric: str = "avg_sales",
        start_date: str = None,
        end_date: str = None,
        state_filter: str = None,
        category_filter: str = None
    ) -> List[Dict]:
        """Obtiene ventas agrupadas por año-mes - CON FILTROS GLOBALES + CACHÉ"""
        key = _make_cache_key(
            "sales_year_month",
            metric=metric,
            start_date=start_date,
            end_date=end_date,
            state=state_filter,
            category=category_filter,
        )
        
        def _query():
            allowed_metrics = {"avg_sales", "sum_sales", "std_sales"}
            if metric not in allowed_metrics:
                metric_used = "avg_sales"
            else:
                metric_used = metric
            
            query = f"""
            SELECT 
                cal.yyyymm,
                ROUND(AVG(f.total), 2) AS avg_sales,
                ROUND(SUM(f.total), 2) AS sum_sales,
                ROUND(STDDEV(f.total), 2) AS std_sales
            FROM {SCHEMA}.fact_sales f
            INNER JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
            INNER JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
            INNER JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
            WHERE 1=1
            """
            
            if start_date:
                query += f" AND cal.iso_date::DATE >= '{start_date}'"
            if end_date:
                query += f" AND cal.iso_date::DATE <= '{end_date}'"
            if state_filter:
                query += f" AND c.customer_state = '{state_filter}'"
            if category_filter:
                query += f" AND p.product_category_name = '{category_filter}'"
            
            query += f"""
            GROUP BY cal.yyyymm
            ORDER BY cal.yyyymm, {metric_used} DESC
            """
            
            df = self.execute_query(query)
            return df.to_dict('records') if not df.empty else []
        
        return self._cached(key, _query)
    
    def get_sales_by_year_month_day(
        self,
        metric: str = "avg_sales",
        start_date: str = None,
        end_date: str = None,
        state_filter: str = None,
        category_filter: str = None
    ) -> List[Dict]:
        """Obtiene ventas agrupadas por año-mes-día - CON FILTROS GLOBALES + CACHÉ"""
        key = _make_cache_key(
            "sales_year_month_day",
            metric=metric,
            start_date=start_date,
            end_date=end_date,
            state=state_filter,
            category=category_filter,
        )
        
        def _query():
            allowed_metrics = {"avg_sales", "sum_sales", "std_sales"}
            if metric not in allowed_metrics:
                metric_used = "avg_sales"
            else:
                metric_used = metric
            
            query = f"""
            SELECT 
                cal.yyyymmdd,
                ROUND(AVG(f.total), 2) AS avg_sales,
                ROUND(SUM(f.total), 2) AS sum_sales,
                ROUND(STDDEV(f.total), 2) AS std_sales
            FROM {SCHEMA}.fact_sales f
            INNER JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
            INNER JOIN {SCHEMA}.dim_customers c ON f.customer_key = c.customer_key
            INNER JOIN {SCHEMA}.dim_products p ON f.product_key = p.product_key
            WHERE 1=1
            """
            
            if start_date:
                query += f" AND cal.iso_date::DATE >= '{start_date}'"
            if end_date:
                query += f" AND cal.iso_date::DATE <= '{end_date}'"
            if state_filter:
                query += f" AND c.customer_state = '{state_filter}'"
            if category_filter:
                query += f" AND p.product_category_name = '{category_filter}'"
            
            query += f"""
            GROUP BY cal.yyyymmdd
            ORDER BY cal.yyyymmdd, {metric_used} DESC
            """
            
            df = self.execute_query(query)
            return df.to_dict('records') if not df.empty else []
        
        return self._cached(key, _query)
    
    # ==================== FILTROS Y UTILIDADES ====================
    
    def get_available_states(self) -> List[str]:
        """Obtiene lista de estados disponibles"""
        query = f"SELECT DISTINCT customer_state FROM {SCHEMA}.dim_customers WHERE customer_state IS NOT NULL ORDER BY customer_state"
        df = self.execute_query(query)
        return df['customer_state'].tolist()
    
    def get_available_cities(self, state: str = None) -> List[str]:
        """Obtiene lista de ciudades disponibles"""
        query = f"SELECT DISTINCT customer_city FROM {SCHEMA}.dim_customers WHERE customer_city IS NOT NULL"
        if state:
            query += f" AND customer_state = '{state}'"
        query += " ORDER BY customer_city"
        df = self.execute_query(query)
        return df['customer_city'].tolist()
    
    def get_available_categories(self) -> List[str]:
        """Obtiene lista de categorías disponibles"""
        query = f"SELECT DISTINCT product_category_name FROM {SCHEMA}.dim_products WHERE product_category_name IS NOT NULL ORDER BY product_category_name"
        df = self.execute_query(query)
        return df['product_category_name'].tolist()
    
    def get_date_range(self) -> Tuple[str, str]:
        """Obtiene el rango de fechas disponible"""
        query = f"""
        SELECT 
            MIN(cal.date_ymd) as min_date,
            MAX(cal.date_ymd) as max_date
        FROM {SCHEMA}.fact_sales f
        JOIN {SCHEMA}.dim_calendar cal ON f.date_purchase_key = cal.date_key
        """
        df = self.execute_query(query)
        if df.empty:
            return ("2016-01-01", "2018-12-31")  # Fallback
        return (str(df['min_date'].iloc[0]), str(df['max_date'].iloc[0]))


# Instancia global
db = DatabaseManager()