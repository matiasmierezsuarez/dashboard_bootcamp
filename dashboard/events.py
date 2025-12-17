
# """
# Events - Lógica de negocio del dashboard como sub-estados de Reflex.
# VERSIÓN CON CACHÉ: Limpieza automática al cambiar filtros
# """
# import reflex as rx
# import pandas as pd
# import plotly.express as px
# from .database import db
# import plotly.graph_objects as go


# class DataEvents(rx.State):
#     """Eventos relacionados con la carga de datos"""
#     # ==================== DATOS PARA GRÁFICOS RECHARTS ====================
#     top_states_chart: list[dict] = []
#     bottom_states_chart: list[dict] = []
#     categories_chart: list[dict] = []

#     # ==================== DATOS PARA MÉTRICAS ====================
#     top_product_data: dict = {}
#     top_seller_data: dict = {}
#     top_customer_data: dict = {}
#     overview_metrics: dict = {}
#     statistics_data: dict = {}

#     # ==================== COMPUTED VARS ====================
#     @rx.var
#     def has_data(self) -> bool:
#         return len(self.top_states_chart) > 0

#     @rx.var
#     def seller_id_display(self) -> str:
#         seller_id = self.top_seller_data.get('seller_id', 'N/A')
#         return seller_id[:20] if len(seller_id) > 20 else seller_id

#     @rx.var
#     def customer_id_display(self) -> str:
#         customer_id = self.top_customer_data.get('customer_id', 'N/A')
#         return customer_id[:20] if len(customer_id) > 20 else customer_id

#     @rx.var
#     def product_id_display(self) -> str:
#         product_id = self.top_product_data.get('product_id', 'N/A')
#         return product_id[:20] if len(product_id) > 20 else product_id

    
#     def refresh_all_data(self):
#         """Actualiza todos los datos con filtros globales (optimizado con yield)"""
#         parent_state = self.get_parent()
#         parent_state.is_loading = True
#         filters = parent_state.filters

#         state_filter = filters.selected_state_filter or None
#         category_filter = filters.selected_category_filter or None

#         # 1️⃣ MÉTRICAS GENERALES (rápido, feedback inmediato)
#         self.overview_metrics = db.get_overview_metrics(
#             start_date=filters.start_date or None,
#             end_date=filters.end_date or None,
#             state_filter=state_filter,
#             category_filter=category_filter
#         )

#         # 👉 Render parcial: métricas visibles
#         yield

#         # 2️⃣ GRÁFICOS RECHARTS (top / bottom / categorías)
#         self._load_state_charts(filters, state_filter, category_filter)

#         # 👉 Render parcial: charts visibles
#         yield

#         # 3️⃣ TOP PERFORMERS (más pesado)
#         self._load_top_entities(filters, state_filter, category_filter)

#         # 👉 Render parcial: cards visibles
#         yield

#         # 4️⃣ ESTADÍSTICAS
#         yield parent_state.data.calculate_statistics

#         parent_state.is_loading = False

    
#     def calculate_statistics(self):
#         """Calcula estadísticas con filtros globales"""
#         parent_state = self.get_parent()
#         filters = parent_state.filters
        
#         self.statistics_data = db.get_statistics(
#             metric=filters.selected_metric,
#             group_by=filters.selected_group if filters.selected_filter_value else None,
#             filter_value=filters.selected_filter_value if filters.selected_filter_value else None,
#             start_date=filters.start_date if filters.start_date else None,
#             end_date=filters.end_date if filters.end_date else None,
#             state_filter=filters.selected_state_filter if filters.selected_state_filter else None,
#             category_filter=filters.selected_category_filter if filters.selected_category_filter else None
#         )
    


#     def _load_state_charts(self, filters, state_filter, category_filter):
#         # Top Estados
#         df_top = db.get_top_states_by_sales(
#             filters.start_date, filters.end_date, 10,
#             state_filter=state_filter,
#             category_filter=category_filter
#         )
#         self.top_states_chart = [
#             {
#                 "estado": row["estado"],
#                 "ventas": float(row["ventas_totales"]),
#                 "ordenes": int(row["total_ordenes"]),
#             }
#             for _, row in df_top.iterrows()
#         ] if not df_top.empty else []

#         # Bottom Estados
#         df_bottom = db.get_bottom_states_by_sales(
#             filters.start_date, filters.end_date, 10,
#             state_filter=state_filter,
#             category_filter=category_filter
#         )
#         self.bottom_states_chart = [
#             {
#                 "estado": row["estado"],
#                 "ventas": float(row["ventas_totales"]),
#                 "ordenes": int(row["total_ordenes"]),
#             }
#             for _, row in df_bottom.iterrows()
#         ] if not df_bottom.empty else []

#         # Categorías
#         df_categories = db.get_top_categories(
#             filters.start_date, filters.end_date, 10,
#             state_filter=state_filter,
#             category_filter=category_filter
#         )
#         self.categories_chart = [
#             {
#                 "categoria": row["categoria"][:20],
#                 "ventas": float(row["ventas_totales"]),
#                 "unidades": int(row["unidades_vendidas"]),
#             }
#             for _, row in df_categories.iterrows()
#         ] if not df_categories.empty else []
    

#     def _load_top_entities(self, filters, state_filter, category_filter):
#         df_product = db.get_top_product(
#             filters.start_date, filters.end_date,
#             state_filter=state_filter,
#             category_filter=category_filter
#         )
#         self.top_product_data = df_product.iloc[0].to_dict() if not df_product.empty else {}

#         df_seller = db.get_top_seller(
#             filters.start_date, filters.end_date,
#             state_filter=state_filter,
#             category_filter=category_filter
#         )
#         self.top_seller_data = df_seller.iloc[0].to_dict() if not df_seller.empty else {}

#         df_customer = db.get_top_customer(
#             filters.start_date, filters.end_date,
#             state_filter=state_filter,
#             category_filter=category_filter
#         )
#         self.top_customer_data = df_customer.iloc[0].to_dict() if not df_customer.empty else {}


# class FilterEvents(rx.State):
#     """Eventos relacionados con filtros"""
#     # ==================== FILTROS GLOBALES ====================
#     start_date: str = ""
#     end_date: str = ""
#     min_available_date: str = ""
#     max_available_date: str = ""
#     selected_state_filter: str = ""
#     selected_category_filter: str = ""
    
#     # ==================== FILTROS ADICIONALES PARA ESTADÍSTICAS ====================
#     selected_metric: str = "total"
#     selected_group: str = "customer_state"
#     selected_filter_value: str = ""

#     # ==================== OPCIONES PARA FILTROS ====================
#     available_states: list[str] = []
#     available_categories: list[str] = []

#     # ==================== COMPUTED VARS ====================
#     @rx.var
#     def states_filter_options(self) -> list[str]:
#         return ["Todos"] + self.available_states

#     @rx.var
#     def categories_filter_options(self) -> list[str]:
#         return ["Todas"] + self.available_categories

#     @rx.var
#     def states_options(self) -> list[str]:
#         return ["Todos"] + self.available_states

#     @rx.var
#     def categories_options(self) -> list[str]:
#         return ["Todas"] + self.available_categories

#     @rx.var
#     def active_filters_text(self) -> str:
#         """Texto descriptivo de filtros activos"""
#         filters = []
#         if self.start_date and self.end_date:
#             filters.append(f"📅 {self.start_date} al {self.end_date}")
#         if self.selected_state_filter:
#             filters.append(f"📍 Estado: {self.selected_state_filter}")
#         if self.selected_category_filter:
#             filters.append(f"🏷️ Categoría: {self.selected_category_filter}")
        
#         return " | ".join(filters) if filters else "Sin filtros aplicados"

#     @rx.var
#     def has_active_filters(self) -> bool:
#         """Verifica si hay filtros activos"""
#         return bool(self.start_date or self.end_date or self.selected_state_filter or self.selected_category_filter)
    
#     @rx.var
#     def metric_labels(self) -> dict:
#         """Etiquetas para las métricas"""
#         return {
#             "total_sales": "Ventas Totales ($)",
#             "avg_sales": "Promedio de Ventas ($)",
#             "total_orders": "Total de Órdenes",
#             "avg_ticket": "Ticket Promedio ($)"
#         }
    
#     def set_start_date(self, value: str):
#         self.start_date = value
    
#     def set_end_date(self, value: str):
#         self.end_date = value
    
#     def set_state_filter(self, value: str):
#         self.selected_state_filter = "" if value == "Todos" else value
    
#     def set_category_filter(self, value: str):
#         self.selected_category_filter = "" if value == "Todas" else value
    
#     def apply_global_filters(self):
#         """Aplica filtros globales a todo el dashboard"""
#         parent_state = self.get_parent()
#         parent_state.is_loading = True
        
#         # 🔥 LIMPIAR CACHÉ ANTES DE RECARGAR
#         db._cache.clear()
        
#         try:
#             # Usamos yield para encadenar eventos
#             yield parent_state.data.refresh_all_data
#             if parent_state.current_page == "charts":
#                 yield parent_state.plotly.load_all_plotly_charts
#             if parent_state.current_page == "temporal":
#                 yield parent_state.temporal.load_all_temporal_charts
#         finally:
#             parent_state.is_loading = False

#     def clear_global_filters(self):
#         parent_state = self.get_parent()
        
#         # 🔥 LIMPIAR CACHÉ AL RESETEAR FILTROS
#         db._cache.clear()
        
#         # Resetear filtros
#         self.selected_state_filter = ""
#         self.selected_category_filter = ""
#         self.start_date = ""
#         self.end_date = ""
        
#         # Reaplicar filtros
#         return self.apply_global_filters
    
#     def set_metric(self, value: str):
#         self.selected_metric = value
#         return self.get_parent().data.calculate_statistics
    
#     def set_group(self, value: str):
#         self.selected_group = value
#         self.selected_filter_value = ""
    
#     def set_filter_value(self, value: str):
#         if value in ["Todos", "Todas"]:
#             self.selected_filter_value = ""
#         else:
#             self.selected_filter_value = value
#         return self.get_parent().data.calculate_statistics


# class PlotlyEvents(rx.State):
#     """Eventos para gráficos Plotly"""
#     # ==================== DATOS PARA GRÁFICOS PLOTLY ====================
#     fig_states_plotly: dict = {}
#     fig_cities_plotly: dict = {}
#     fig_categories_plotly: dict = {}
#     fig_sellers_plotly: dict = {}

#     # ==================== CONTROLES PARA GRÁFICOS DINÁMICOS ====================
#     selected_metric_state: str = "total_sales"
#     num_states_to_show: str = "10"
#     selected_metric_city: str = "total_sales"
#     num_cities_to_show: str = "10"
#     selected_metric_category: str = "total_sales"
#     num_categories_to_show: str = "10"
#     selected_metric_seller: str = "total_sales"
#     num_sellers_to_show: str = "10"
    
#     metric_options: list[str] = ["total_sales", "avg_sales", "total_orders", "avg_ticket"]
#     limit_options: list[str] = ["5", "10", "15", "20", "25"]

#     # ==================== FLAGS DE CARGA ====================
#     loading_chart_states: bool = False
#     loading_chart_cities: bool = False
#     loading_chart_categories: bool = False
#     loading_chart_sellers: bool = False

    
#     def load_states_plotly(self):
#         """Carga el gráfico dinámico de estados con Plotly"""
#         parent_state = self.get_parent()
#         filters = parent_state.filters

#         self.loading_chart_states = True
        
#         try:
#             state_filter = filters.selected_state_filter if filters.selected_state_filter else None
#             category_filter = filters.selected_category_filter if filters.selected_category_filter else None
            
#             data = db.get_sales_by_state_dynamic(
#                 start_date=filters.start_date if filters.start_date else None,
#                 end_date=filters.end_date if filters.end_date else None,
#                 metric=self.selected_metric_state,
#                 limit=int(self.num_states_to_show),
#                 state_filter=state_filter,
#                 category_filter=category_filter
#             )
            
#             if data:
#                 df = pd.DataFrame(data)
                
#                 fig = px.bar(
#                     df,
#                     x=self.selected_metric_state,
#                     y="state",
#                     orientation='h',
#                     title=f"Ventas por Estado (Top {self.num_states_to_show})",
#                     color=self.selected_metric_state,
#                     color_continuous_scale="Blues"
#                 )
#                 self.fig_states_plotly = fig.to_dict()
                
#                 self.fig_states_plotly.update_layout(
#                     autosize=True,
#                     height=600,
#                     xaxis_title=self.get_parent().filters.metric_labels.get(self.selected_metric_state),
#                     yaxis_title="Estado",
#                     showlegend=False,
#                     hovermode='closest'
#                 )
                
#         except Exception as e:
#             print(f"Error loading states chart: {e}")
#         finally:
#             self.loading_chart_states = False
    
#     def update_metric_state(self, metric: str):
#         self.selected_metric_state = metric
#         return self.load_states_plotly
    
#     def update_limit_state(self, limit: str):
#         try:
#             self.num_states_to_show = str(max(5, int(limit)))
#         except ValueError:
#             self.num_states_to_show = "10"
#         return self.load_states_plotly
    
#     def load_cities_plotly(self):
#         """Carga el gráfico dinámico de ciudades"""
#         parent_state = self.get_parent()
#         filters = parent_state.filters

#         self.loading_chart_cities = True
        
#         try:
#             state_filter = filters.selected_state_filter if filters.selected_state_filter else None
#             category_filter = filters.selected_category_filter if filters.selected_category_filter else None
            
#             data = db.get_sales_by_city_dynamic(
#                 start_date=filters.start_date if filters.start_date else None,
#                 end_date=filters.end_date if filters.end_date else None,
#                 metric=self.selected_metric_city,
#                 limit=int(self.num_cities_to_show),
#                 state_filter=state_filter,
#                 category_filter=category_filter
#             )
            
#             if data:
#                 df = pd.DataFrame(data)
                
#                 fig = px.bar(
#                     df,
#                     x=self.selected_metric_city,
#                     y="city",
#                     orientation='h',
#                     title=f"Ventas por Ciudad (Top {self.num_cities_to_show})",
#                     color=self.selected_metric_city,
#                     color_continuous_scale="Greens"
#                 )
#                 self.fig_cities_plotly = fig.to_dict()
                
#                 self.fig_cities_plotly.update_layout(
#                     autosize=True,
#                     height=600,
#                     xaxis_title=self.get_parent().filters.metric_labels.get(self.selected_metric_city),
#                     yaxis_title="Ciudad",
#                     showlegend=False
#                 )
                
#         except Exception as e:
#             print(f"Error loading cities chart: {e}")
#         finally:
#             self.loading_chart_cities = False
    
#     def update_metric_city(self, metric: str):
#         self.selected_metric_city = metric
#         return self.load_cities_plotly
    
#     def update_limit_city(self, limit: str):
#         try:
#             self.num_cities_to_show = str(max(5, int(limit)))
#         except ValueError:
#             self.num_cities_to_show = "10"
#         return self.load_cities_plotly
    
#     def load_categories_plotly(self):
#         """Carga el gráfico dinámico de categorías"""
#         parent_state = self.get_parent()
#         filters = parent_state.filters

#         self.loading_chart_categories = True
        
#         try:
#             state_filter = filters.selected_state_filter if filters.selected_state_filter else None
#             category_filter = filters.selected_category_filter if filters.selected_category_filter else None
            
#             data = db.get_sales_by_category_dynamic(
#                 start_date=filters.start_date if filters.start_date else None,
#                 end_date=filters.end_date if filters.end_date else None,
#                 metric=self.selected_metric_category,
#                 limit=int(self.num_categories_to_show),
#                 state_filter=state_filter,
#                 category_filter=category_filter
#             )
            
#             if data:
#                 df = pd.DataFrame(data)
                
#                 fig = px.bar(
#                     df,
#                     x=self.selected_metric_category,
#                     y="category",
#                     orientation='h',
#                     title=f"Ventas por Categoría (Top {self.num_categories_to_show})",
#                     color=self.selected_metric_category,
#                     color_continuous_scale="Purples"
#                 )
#                 self.fig_categories_plotly = fig.to_dict()
                
#                 self.fig_categories_plotly.update_layout(
#                     autosize=True,
#                     height=600,
#                     xaxis_title=self.get_parent().filters.metric_labels.get(self.selected_metric_category),
#                     yaxis_title="Categoría",
#                     showlegend=False
#                 )
                
#         except Exception as e:
#             print(f"Error loading categories chart: {e}")
#         finally:
#             self.loading_chart_categories = False
    
#     def update_metric_category(self, metric: str):
#         self.selected_metric_category = metric
#         return self.load_categories_plotly
    
#     def update_limit_category(self, limit: str):
#         try:
#             self.num_categories_to_show = str(max(5, int(limit)))
#         except ValueError:
#             self.num_categories_to_show = "10"
#         return self.load_categories_plotly
    
#     def load_sellers_plotly(self):
#         """Carga el gráfico dinámico de vendedores"""
#         parent_state = self.get_parent()
#         filters = parent_state.filters

#         self.loading_chart_sellers = True
        
#         try:
#             state_filter = filters.selected_state_filter if filters.selected_state_filter else None
#             category_filter = filters.selected_category_filter if filters.selected_category_filter else None
            
#             data = db.get_sales_by_seller_dynamic(
#                 start_date=filters.start_date if filters.start_date else None,
#                 end_date=filters.end_date if filters.end_date else None,
#                 metric=self.selected_metric_seller,
#                 limit=int(self.num_sellers_to_show),
#                 state_filter=state_filter,
#                 category_filter=category_filter
#             )
            
#             if data:
#                 df = pd.DataFrame(data)
#                 df['seller_display'] = df['seller_id'].str[:15]
                
#                 fig = px.bar(
#                     df,
#                     x=self.selected_metric_seller,
#                     y="seller_display",
#                     orientation='h',
#                     title=f"Ventas por Vendedor (Top {self.num_sellers_to_show})",
#                     color=self.selected_metric_seller,
#                     color_continuous_scale="Oranges"
#                 )
#                 self.fig_sellers_plotly = fig.to_dict()
                
#                 self.fig_sellers_plotly.update_layout(
#                     autosize=True,
#                     height=600,
#                     xaxis_title=self.get_parent().filters.metric_labels.get(self.selected_metric_seller),
#                     yaxis_title="Vendedor",
#                     showlegend=False
#                 )
                
#         except Exception as e:
#             print(f"Error loading sellers chart: {e}")
#         finally:
#             self.loading_chart_sellers = False
    
#     def update_metric_seller(self, metric: str):
#         self.selected_metric_seller = metric
#         return self.load_sellers_plotly
    
#     def update_limit_seller(self, limit: str):
#         try:
#             self.num_sellers_to_show = str(max(5, int(limit)))
#         except ValueError:
#             self.num_sellers_to_show = "10"
#         return self.load_sellers_plotly
    
#     def load_all_plotly_charts(self):
#         """Carga todos los gráficos Plotly"""
#         yield self.load_states_plotly
#         yield self.load_cities_plotly
#         yield self.load_categories_plotly
#         yield self.load_sellers_plotly


# class TemporalEvents(rx.State):
#     """Eventos para análisis temporal"""
#     # ==================== ANÁLISIS TEMPORAL ====================
#     fig_sales_by_year: dict = {}
#     fig_sales_by_year_month: dict = {}
#     fig_sales_by_year_month_day: dict = {}
    
#     selected_metric_year: str = "sum_sales"
#     selected_metric_year_month: str = "sum_sales"
#     selected_metric_year_month_day: str = "sum_sales"
    
#     start_date_month: str = ""
#     end_date_month: str = ""
#     start_date_day: str = ""
#     end_date_day: str = ""
    
#     loading_chart_year: bool = False
#     loading_chart_year_month: bool = False
#     loading_chart_year_month_day: bool = False

#     has_year_data: bool = False
#     has_year_month_data: bool = False
#     has_year_month_day_data: bool = False
    
#     @rx.var
#     def temporal_metric_labels(self) -> dict:
#         return {
#             "avg_sales": "Promedio de Ventas ($)",
#             "sum_sales": "Ventas Totales ($)",
#             "std_sales": "Desviación Estándar ($)"
#         }
    
#     @rx.var
#     def temporal_metric_options(self) -> list[str]:
#         return list(self.temporal_metric_labels.keys())
    
#     def init_temporal_dates(self):
#         """Inicializa las fechas para los gráficos temporales"""
#         parent_state = self.get_parent()
#         filters = parent_state.filters
#         self.start_date_month = filters.start_date
#         self.end_date_month = filters.end_date
#         self.start_date_day = filters.start_date
#         self.end_date_day = filters.end_date
    
#     def load_sales_by_year(self):
#         """Carga el gráfico de ventas por año"""
#         parent_state = self.get_parent()
#         filters = parent_state.filters

#         self.loading_chart_year = True
        
#         try:
#             state_filter = filters.selected_state_filter if filters.selected_state_filter else None
#             category_filter = filters.selected_category_filter if filters.selected_category_filter else None
            
#             data = db.get_sales_by_year(
#                 metric=self.selected_metric_year,
#                 state_filter=state_filter,
#                 category_filter=category_filter
#             )
            
#             if data:
#                 df = pd.DataFrame(data)
#                 df['date_year'] = df['date_year'].astype(str)
                
#                 fig = px.line(
#                     df,
#                     x="date_year",
#                     y=self.selected_metric_year,
#                     title=f"Ventas por Año - {self.temporal_metric_labels.get(self.selected_metric_year)}",
#                     markers=True
#                 )
#                 self.fig_sales_by_year = fig.to_dict()
                
#                 self.fig_sales_by_year.update_layout(
#                     autosize=True,
#                     height=500,
#                     xaxis_title="Año",
#                     yaxis_title=self.temporal_metric_labels.get(self.selected_metric_year),
#                     hovermode='x unified'
#                 )
                
#                 self.has_year_data = True
#             else:
#                 self.has_year_data = False
                
#         except Exception as e:
#             print(f"Error loading year chart: {e}")
#             self.has_year_data = False
#         finally:
#             self.loading_chart_year = False
    
#     def load_sales_by_year_month(self):
#         """Carga el gráfico de ventas por año-mes"""
#         parent_state = self.get_parent()
#         filters = parent_state.filters

#         self.loading_chart_year_month = True
        
#         try:
#             state_filter = filters.selected_state_filter if filters.selected_state_filter else None
#             category_filter = filters.selected_category_filter if filters.selected_category_filter else None
            
#             data = db.get_sales_by_year_month(
#                 metric=self.selected_metric_year_month,
#                 start_date=self.start_date_month if self.start_date_month else None,
#                 end_date=self.end_date_month if self.end_date_month else None,
#                 state_filter=state_filter,
#                 category_filter=category_filter
#             )
            
#             if data:
#                 df = pd.DataFrame(data)
                
#                 fig = px.line(
#                     df,
#                     x="yyyymm",
#                     y=self.selected_metric_year_month,
#                     title=f"Ventas por Año-Mes - {self.temporal_metric_labels.get(self.selected_metric_year_month)}",
#                     markers=True
#                 )
#                 self.fig_sales_by_year_month = fig.to_dict()

#                 self.fig_sales_by_year_month.update_layout(
#                     autosize=True,
#                     height=500,
#                     xaxis_title="Año-Mes",
#                     yaxis_title=self.temporal_metric_labels.get(self.selected_metric_year_month),
#                     hovermode='x unified'
#                 )
                
#                 self.has_year_month_data = True
#             else:
#                 self.has_year_month_data = False
                
#         except Exception as e:
#             print(f"Error loading year-month chart: {e}")
#             self.has_year_month_data = False
#         finally:
#             self.loading_chart_year_month = False
    
#     def load_sales_by_year_month_day(self):
#         """Carga el gráfico de ventas por año-mes-día"""
#         parent_state = self.get_parent()
#         filters = parent_state.filters

#         self.loading_chart_year_month_day = True
        
#         try:
#             state_filter = filters.selected_state_filter if filters.selected_state_filter else None
#             category_filter = filters.selected_category_filter if filters.selected_category_filter else None
            
#             data = db.get_sales_by_year_month_day(
#                 metric=self.selected_metric_year_month_day,
#                 start_date=self.start_date_day if self.start_date_day else None,
#                 end_date=self.end_date_day if self.end_date_day else None,
#                 state_filter=state_filter,
#                 category_filter=category_filter
#             )
            
#             if data:
#                 df = pd.DataFrame(data)
                
#                 fig = px.line(
#                     df,
#                     x="yyyymmdd",
#                     y=self.selected_metric_year_month_day,
#                     title=f"Ventas por Año-Mes-Día - {self.temporal_metric_labels.get(self.selected_metric_year_month_day)}",
#                     markers=True
#                 )
#                 self.fig_sales_by_year_month_day = fig.to_dict()
                
#                 self.fig_sales_by_year_month_day.update_layout(
#                     autosize=True,
#                     height=500,
#                     xaxis_title="Fecha",
#                     yaxis_title=self.temporal_metric_labels.get(self.selected_metric_year_month_day),
#                     hovermode='x unified'
#                 )
                
#                 self.has_year_month_day_data = True
#             else:
#                 self.has_year_month_day_data = False
                
#         except Exception as e:
#             print(f"Error loading year-month-day chart: {e}")
#             self.has_year_month_day_data = False
#         finally:
#             self.loading_chart_year_month_day = False
    
#     def update_metric_year(self, metric: str):
#         self.selected_metric_year = metric
#         return self.load_sales_by_year
    
#     def update_metric_year_month(self, metric: str):
#         self.selected_metric_year_month = metric
#         return self.load_sales_by_year_month
    
#     def update_metric_year_month_day(self, metric: str):
#         self.selected_metric_year_month_day = metric
#         return self.load_sales_by_year_month_day
    
#     def set_start_date_day(self, value: str):
#         self.start_date_day = value
    
#     def set_end_date_day(self, value: str):
#         self.end_date_day = value
    
#     def set_start_date_month(self, value: str):
#         self.start_date_month = value
    
#     def set_end_date_month(self, value: str):
#         self.end_date_month = value
    
#     def apply_day_filters(self):
#         return self.load_sales_by_year_month_day
    
#     def apply_month_filters(self):
#         return self.load_sales_by_year_month
    
#     def apply_year_filters(self):
#         return self.load_sales_by_year
    
#     def load_all_temporal_charts(self):
#         """Carga todos los gráficos temporales"""
#         yield self.load_sales_by_year
#         yield self.load_sales_by_year_month
#         yield self.load_sales_by_year_month_day
