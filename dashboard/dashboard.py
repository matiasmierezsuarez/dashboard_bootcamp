"""
Dashboard Analytics - Versión con Filtros Globales y Navegación
INCLUYE: Análisis Temporal Integrado
"""
import reflex as rx
from datetime import datetime, timedelta
from .database import db
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class DashboardState(rx.State):
    """Estado principal del dashboard"""
    
    # ==================== NAVEGACIÓN ====================
    current_page: str = "overview"
    
    # ==================== FILTROS GLOBALES ====================
    start_date: str = ""
    end_date: str = ""
    min_available_date: str = ""
    max_available_date: str = ""
    selected_state_filter: str = ""  # Filtro global por estado
    selected_category_filter: str = ""  # Filtro global por categoría
    
    # ==================== FILTROS ADICIONALES PARA ESTADÍSTICAS ====================
    selected_metric: str = "total"
    selected_group: str = "customer_state"
    selected_filter_value: str = ""
    
    # ==================== DATOS PARA GRÁFICOS RECHARTS ====================
    top_states_chart: list[dict] = []
    bottom_states_chart: list[dict] = []
    categories_chart: list[dict] = []
    
    # ==================== DATOS PARA GRÁFICOS PLOTLY ====================
    fig_states_plotly: go.Figure = go.Figure()
    fig_cities_plotly: go.Figure = go.Figure()
    fig_categories_plotly: go.Figure = go.Figure()
    fig_sellers_plotly: go.Figure = go.Figure()
    
    # ==================== ANÁLISIS TEMPORAL ====================
    # Figuras de gráficos temporales
    fig_sales_by_year: go.Figure = go.Figure()
    fig_sales_by_year_month: go.Figure = go.Figure()
    fig_sales_by_year_month_day: go.Figure = go.Figure()
    
    # Métricas seleccionadas
    selected_metric_year: str = "sum_sales"
    selected_metric_year_month: str = "sum_sales"
    selected_metric_year_month_day: str = "sum_sales"
    
    # Fechas específicas para gráficos mensuales y diarios
    start_date_month: str = ""
    end_date_month: str = ""
    start_date_day: str = ""
    end_date_day: str = ""
    
    # Flags de carga temporales
    loading_chart_year: bool = False
    loading_chart_year_month: bool = False
    loading_chart_year_month_day: bool = False
        
    # Opciones de métricas temporales
    temporal_metric_options: list[str] = ["avg_sales", "sum_sales", "std_sales"]
    
    # ==================== CONTROLES PARA GRÁFICOS DINÁMICOS ====================
    selected_metric_state: str = "total_sales"
    num_states_to_show: str = "10"
    selected_metric_city: str = "total_sales"
    num_cities_to_show: str = "10"
    selected_metric_category: str = "total_sales"
    num_categories_to_show: str = "10"
    selected_metric_seller: str = "total_sales"
    num_sellers_to_show: str = "10"
    
    metric_options: list[str] = ["total_sales", "avg_sales", "total_orders", "avg_ticket"]
    limit_options: list[str] = ["5", "10", "15", "20", "25"]
    
    # ==================== FLAGS DE CARGA ====================
    loading_chart_states: bool = False
    loading_chart_cities: bool = False
    loading_chart_categories: bool = False
    loading_chart_sellers: bool = False
    is_loading: bool = False
    has_year_data: bool = False
    has_year_month_data: bool = False
    has_year_month_day_data: bool = False
    
    # ==================== DATOS PARA MÉTRICAS ====================
    top_product_data: dict = {}
    top_seller_data: dict = {}
    top_customer_data: dict = {}
    overview_metrics: dict = {}
    statistics_data: dict = {}
    
    # ==================== OPCIONES PARA FILTROS ====================
    available_states: list[str] = []
    available_categories: list[str] = []
    
    # ==================== COMPUTED VARS ====================
    @rx.var
    def states_filter_options(self) -> list[str]:
        return ["Todos"] + self.available_states
    
    @rx.var
    def categories_filter_options(self) -> list[str]:
        return ["Todas"] + self.available_categories
    
    @rx.var
    def states_options(self) -> list[str]:
        return ["Todos"] + self.available_states
    
    @rx.var
    def categories_options(self) -> list[str]:
        return ["Todas"] + self.available_categories
    
    @rx.var
    def has_data(self) -> bool:
        return len(self.top_states_chart) > 0
    
    @rx.var
    def seller_id_display(self) -> str:
        seller_id = self.top_seller_data.get('seller_id', 'N/A')
        return seller_id[:20] if len(seller_id) > 20 else seller_id
    
    @rx.var
    def customer_id_display(self) -> str:
        customer_id = self.top_customer_data.get('customer_id', 'N/A')
        return customer_id[:20] if len(customer_id) > 20 else customer_id
    
    @rx.var
    def product_id_display(self) -> str:
        product_id = self.top_product_data.get('product_id', 'N/A')
        return product_id[:20] if len(product_id) > 20 else product_id
    
    @rx.var
    def metric_labels(self) -> dict:
        return {
            "total_sales": "Ventas Totales ($)",
            "avg_sales": "Promedio de Ventas ($)",
            "total_orders": "Total de Órdenes",
            "avg_ticket": "Ticket Promedio ($)"
        }
    
    @rx.var
    def temporal_metric_labels(self) -> dict:
        return {
            "avg_sales": "Promedio de Ventas ($)",
            "sum_sales": "Ventas Totales ($)",
            "std_sales": "Desviación Estándar ($)"
        }
    
    @rx.var
    def active_filters_text(self) -> str:
        """Texto descriptivo de filtros activos"""
        filters = []
        if self.start_date and self.end_date:
            filters.append(f"📅 {self.start_date} al {self.end_date}")
        if self.selected_state_filter:
            filters.append(f"📍 Estado: {self.selected_state_filter}")
        if self.selected_category_filter:
            filters.append(f"🏷️ Categoría: {self.selected_category_filter}")
        
        return " | ".join(filters) if filters else "Sin filtros aplicados"
    
    @rx.var
    def has_active_filters(self) -> bool:
        """Verifica si hay filtros activos"""
        return bool(self.selected_state_filter or self.selected_category_filter)
    
    # ==================== NAVEGACIÓN ====================
    
    def navigate_to(self, page: str):
        """Cambia la página actual"""
        self.current_page = page
    
    # ==================== EVENTOS PRINCIPALES ====================
    
    def on_mount(self):
        """Se ejecuta al cargar la página"""
        self.load_initial_data()
        self.init_temporal_dates()
    
    def load_initial_data(self):
        """Carga datos iniciales"""
        self.is_loading = True
        
        # Obtener rango de fechas
        min_date, max_date = db.get_date_range()
        self.min_available_date = min_date
        self.max_available_date = max_date
        
        # Últimos 6 meses
        end = datetime.strptime(max_date, "%Y-%m-%d")
        start = end - timedelta(days=180)
        self.start_date = start.strftime("%Y-%m-%d")
        self.end_date = max_date
        
        # Cargar opciones
        self.available_states = db.get_available_states()
        self.available_categories = db.get_available_categories()
        
        # Cargar datos
        self.refresh_all_data()
        self.is_loading = False
    
    def refresh_all_data(self):
        """Actualiza todos los datos con filtros globales"""
        self.is_loading = True
        
        # Preparar filtros
        state_filter = self.selected_state_filter if self.selected_state_filter else None
        category_filter = self.selected_category_filter if self.selected_category_filter else None
        
        # Métricas generales
        self.overview_metrics = db.get_overview_metrics(
            start_date=self.start_date if self.start_date else None,
            end_date=self.end_date if self.end_date else None,
            state_filter=state_filter,
            category_filter=category_filter
        )
        
        # Top Estados
        df_top = db.get_top_states_by_sales(
            self.start_date, self.end_date, 10,
            state_filter=state_filter,
            category_filter=category_filter
        )
        if not df_top.empty:
            self.top_states_chart = [
                {
                    "estado": row["estado"],
                    "ventas": float(row["ventas_totales"]),
                    "ordenes": int(row["total_ordenes"])
                }
                for _, row in df_top.iterrows()
            ]
        
        # Bottom Estados
        df_bottom = db.get_bottom_states_by_sales(
            self.start_date, self.end_date, 10,
            state_filter=state_filter,
            category_filter=category_filter
        )
        if not df_bottom.empty:
            self.bottom_states_chart = [
                {
                    "estado": row["estado"],
                    "ventas": float(row["ventas_totales"]),
                    "ordenes": int(row["total_ordenes"])
                }
                for _, row in df_bottom.iterrows()
            ]
        
        # Categorías
        df_categories = db.get_top_categories(
            self.start_date, self.end_date, 10,
            state_filter=state_filter,
            category_filter=category_filter
        )
        if not df_categories.empty:
            self.categories_chart = [
                {
                    "categoria": row["categoria"][:20],
                    "ventas": float(row["ventas_totales"]),
                    "unidades": int(row["unidades_vendidas"])
                }
                for _, row in df_categories.iterrows()
            ]
        
        # Top producto
        df_product = db.get_top_product(
            self.start_date, self.end_date,
            state_filter=state_filter,
            category_filter=category_filter
        )
        self.top_product_data = df_product.iloc[0].to_dict() if not df_product.empty else {}
        
        # Top vendedor
        df_seller = db.get_top_seller(
            self.start_date, self.end_date,
            state_filter=state_filter,
            category_filter=category_filter
        )
        self.top_seller_data = df_seller.iloc[0].to_dict() if not df_seller.empty else {}
        
        # Top cliente
        df_customer = db.get_top_customer(
            self.start_date, self.end_date,
            state_filter=state_filter,
            category_filter=category_filter
        )
        self.top_customer_data = df_customer.iloc[0].to_dict() if not df_customer.empty else {}
        
        # Estadísticas
        self.calculate_statistics()
        self.is_loading = False
    
    def calculate_statistics(self):
        """Calcula estadísticas con filtros globales"""
        state_filter = self.selected_state_filter if self.selected_state_filter else None
        category_filter = self.selected_category_filter if self.selected_category_filter else None
        
        self.statistics_data = db.get_statistics(
            metric=self.selected_metric,
            group_by=self.selected_group if self.selected_filter_value else None,
            filter_value=self.selected_filter_value if self.selected_filter_value else None,
            start_date=self.start_date if self.start_date else None,
            end_date=self.end_date if self.end_date else None,
            state_filter=state_filter,
            category_filter=category_filter
        )
    
    # ==================== EVENTOS DE FILTROS ====================
    
    def set_start_date(self, value: str):
        self.start_date = value
    
    def set_end_date(self, value: str):
        self.end_date = value
    
    def set_state_filter(self, value: str):
        if value == "Todos":
            self.selected_state_filter = ""
        else:
            self.selected_state_filter = value
    
    def set_category_filter(self, value: str):
        if value == "Todas":
            self.selected_category_filter = ""
        else:
            self.selected_category_filter = value
    
    def apply_global_filters(self):
        """Aplica filtros globales a todo el dashboard"""
        self.refresh_all_data()
        # Recargar gráficos Plotly si están cargados
        if self.fig_states_plotly.data:
            self.load_states_plotly()
        if self.fig_cities_plotly.data:
            self.load_cities_plotly()
        if self.fig_categories_plotly.data:
            self.load_categories_plotly()
        if self.fig_sellers_plotly.data:
            self.load_sellers_plotly()
    
    def clear_global_filters(self):
        """Limpia todos los filtros globales"""
        self.selected_state_filter = ""
        self.selected_category_filter = ""
        self.apply_global_filters()
    
    def set_metric(self, value: str):
        self.selected_metric = value
        self.calculate_statistics()
    
    def set_group(self, value: str):
        self.selected_group = value
        self.selected_filter_value = ""
    
    def set_filter_value(self, value: str):
        if value in ["Todos", "Todas"]:
            self.selected_filter_value = ""
        else:
            self.selected_filter_value = value
        self.calculate_statistics()
    
    # ==================== EVENTOS PARA GRÁFICOS PLOTLY ====================
    
    @rx.event
    def load_states_plotly(self):
        """Carga el gráfico dinámico de estados con Plotly"""
        self.loading_chart_states = True
        
        try:
            state_filter = self.selected_state_filter if self.selected_state_filter else None
            category_filter = self.selected_category_filter if self.selected_category_filter else None
            
            data = db.get_sales_by_state_dynamic(
                start_date=self.start_date if self.start_date else None,
                end_date=self.end_date if self.end_date else None,
                metric=self.selected_metric_state,
                limit=int(self.num_states_to_show),
                state_filter=state_filter,
                category_filter=category_filter
            )
            
            if data:
                df = pd.DataFrame(data)
                
                self.fig_states_plotly = px.bar(
                    df,
                    x=self.selected_metric_state,
                    y="state",
                    orientation='h',
                    text_auto='.2s',
                    title=f"Ventas por Estado - {self.metric_labels[self.selected_metric_state]} (Top {self.num_states_to_show})",
                    color=self.selected_metric_state,
                    color_continuous_scale="Blues"
                )
                
                self.fig_states_plotly.update_layout(
                    autosize=True,
                    height=600,
                    xaxis_title=self.metric_labels[self.selected_metric_state],
                    yaxis_title="Estado",
                    showlegend=False,
                    hovermode='closest'
                )
                
        except Exception as e:
            print(f"Error loading states chart: {e}")
        finally:
            self.loading_chart_states = False
    
    @rx.event
    def update_metric_state(self, metric: str):
        self.selected_metric_state = metric
        self.load_states_plotly()
    
    @rx.event
    def update_limit_state(self, limit: str):
        try:
            self.num_states_to_show = str(max(5, int(limit)))
        except:
            self.num_states_to_show = "10"
        self.load_states_plotly()
    
    @rx.event
    def load_cities_plotly(self):
        """Carga el gráfico dinámico de ciudades con Plotly"""
        self.loading_chart_cities = True
        
        try:
            state_filter = self.selected_state_filter if self.selected_state_filter else None
            category_filter = self.selected_category_filter if self.selected_category_filter else None
            
            data = db.get_sales_by_city_dynamic(
                start_date=self.start_date if self.start_date else None,
                end_date=self.end_date if self.end_date else None,
                metric=self.selected_metric_city,
                limit=int(self.num_cities_to_show),
                state_filter=state_filter,
                category_filter=category_filter
            )
            
            if data:
                df = pd.DataFrame(data)
                
                self.fig_cities_plotly = px.bar(
                    df,
                    x=self.selected_metric_city,
                    y="city",
                    orientation='h',
                    text_auto='.2s',
                    title=f"Ventas por Ciudad - {self.metric_labels[self.selected_metric_city]} (Top {self.num_cities_to_show})",
                    color=self.selected_metric_city,
                    color_continuous_scale="Greens"
                )
                
                self.fig_cities_plotly.update_layout(
                    autosize=True,
                    height=600,
                    xaxis_title=self.metric_labels[self.selected_metric_city],
                    yaxis_title="Ciudad",
                    showlegend=False
                )
                
        except Exception as e:
            print(f"Error loading cities chart: {e}")
        finally:
            self.loading_chart_cities = False
    
    @rx.event
    def update_metric_city(self, metric: str):
        self.selected_metric_city = metric
        self.load_cities_plotly()
    
    @rx.event
    def update_limit_city(self, limit: str):
        try:
            self.num_cities_to_show = str(max(5, int(limit)))
        except:
            self.num_cities_to_show = "10"
        self.load_cities_plotly()
    
    @rx.event
    def load_categories_plotly(self):
        """Carga el gráfico dinámico de categorías con Plotly"""
        self.loading_chart_categories = True
        
        try:
            state_filter = self.selected_state_filter if self.selected_state_filter else None
            category_filter = self.selected_category_filter if self.selected_category_filter else None
            
            data = db.get_sales_by_category_dynamic(
                start_date=self.start_date if self.start_date else None,
                end_date=self.end_date if self.end_date else None,
                metric=self.selected_metric_category,
                limit=int(self.num_categories_to_show),
                state_filter=state_filter,
                category_filter=category_filter
            )
            
            if data:
                df = pd.DataFrame(data)
                
                self.fig_categories_plotly = px.bar(
                    df,
                    x=self.selected_metric_category,
                    y="category",
                    orientation='h',
                    text_auto='.2s',
                    title=f"Ventas por Categoría - {self.metric_labels[self.selected_metric_category]} (Top {self.num_categories_to_show})",
                    color=self.selected_metric_category,
                    color_continuous_scale="Purples"
                )
                
                self.fig_categories_plotly.update_layout(
                    autosize=True,
                    height=600,
                    xaxis_title=self.metric_labels[self.selected_metric_category],
                    yaxis_title="Categoría",
                    showlegend=False
                )
                
        except Exception as e:
            print(f"Error loading categories chart: {e}")
        finally:
            self.loading_chart_categories = False
    
    @rx.event
    def update_metric_category(self, metric: str):
        self.selected_metric_category = metric
        self.load_categories_plotly()
    
    @rx.event
    def update_limit_category(self, limit: str):
        try:
            self.num_categories_to_show = str(max(5, int(limit)))
        except:
            self.num_categories_to_show = "10"
        self.load_categories_plotly()
    
    @rx.event
    def load_sellers_plotly(self):
        """Carga el gráfico dinámico de vendedores con Plotly"""
        self.loading_chart_sellers = True
        
        try:
            state_filter = self.selected_state_filter if self.selected_state_filter else None
            category_filter = self.selected_category_filter if self.selected_category_filter else None
            
            data = db.get_sales_by_seller_dynamic(
                start_date=self.start_date if self.start_date else None,
                end_date=self.end_date if self.end_date else None,
                metric=self.selected_metric_seller,
                limit=int(self.num_sellers_to_show),
                state_filter=state_filter,
                category_filter=category_filter
            )
            
            if data:
                df = pd.DataFrame(data)
                df['seller_display'] = df['seller_id'].str[:15]
                
                self.fig_sellers_plotly = px.bar(
                    df,
                    x=self.selected_metric_seller,
                    y="seller_display",
                    orientation='h',
                    text_auto='.2s',
                    title=f"Ventas por Vendedor - {self.metric_labels[self.selected_metric_seller]} (Top {self.num_sellers_to_show})",
                    color=self.selected_metric_seller,
                    color_continuous_scale="Oranges"
                )
                
                self.fig_sellers_plotly.update_layout(
                    autosize=True,
                    height=600,
                    xaxis_title=self.metric_labels[self.selected_metric_seller],
                    yaxis_title="Vendedor",
                    showlegend=False
                )
                
        except Exception as e:
            print(f"Error loading sellers chart: {e}")
        finally:
            self.loading_chart_sellers = False
    
    @rx.event
    def update_metric_seller(self, metric: str):
        self.selected_metric_seller = metric
        self.load_sellers_plotly()
    
    @rx.event
    def update_limit_seller(self, limit: str):
        try:
            self.num_sellers_to_show = str(max(5, int(limit)))
        except:
            self.num_sellers_to_show = "10"
        self.load_sellers_plotly()
    
    @rx.event
    def load_all_plotly_charts(self):
        """Carga todos los gráficos Plotly"""
        self.load_states_plotly()
        self.load_cities_plotly()
        self.load_categories_plotly()
        self.load_sellers_plotly()
    
    # ==================== EVENTOS DE ANÁLISIS TEMPORAL ====================
    
    @rx.event
    def init_temporal_dates(self):
        """Inicializa las fechas para los gráficos temporales"""
        # Usar las mismas fechas que los filtros globales
        self.start_date_month = self.start_date
        self.end_date_month = self.end_date
        self.start_date_day = self.start_date
        self.end_date_day = self.end_date
    
    @rx.event
    def load_sales_by_year(self):
        """Carga el gráfico de ventas por año"""
        self.loading_chart_year = True
        
        try:
            state_filter = self.selected_state_filter if self.selected_state_filter else None
            category_filter = self.selected_category_filter if self.selected_category_filter else None
            
            data = db.get_sales_by_year(
                metric=self.selected_metric_year,
                state_filter=state_filter,
                category_filter=category_filter
            )
            
            if data:
                df = pd.DataFrame(data)
                df['date_year'] = df['date_year'].astype(str)
                
                self.fig_sales_by_year = px.line(
                    df,
                    x="date_year",
                    y=self.selected_metric_year,
                    title=f"Ventas por Año - {self.temporal_metric_labels[self.selected_metric_year]}",
                    markers=True
                )
                
                self.fig_sales_by_year.update_layout(
                    autosize=True,
                    height=500,
                    xaxis_title="Año",
                    yaxis_title=self.temporal_metric_labels[self.selected_metric_year],
                    hovermode='x unified'
                )
                
                self.has_year_data = True  # ✅ Activar flag
            else:
                self.has_year_data = False  # ✅ Desactivar flag
                
        except Exception as e:
            print(f"Error loading year chart: {e}")
            self.has_year_data = False  # ✅ Desactivar flag
        finally:
            self.loading_chart_year = False
    
    @rx.event
    def load_sales_by_year_month(self):
        """Carga el gráfico de ventas por año-mes"""
        self.loading_chart_year_month = True
        
        try:
            state_filter = self.selected_state_filter if self.selected_state_filter else None
            category_filter = self.selected_category_filter if self.selected_category_filter else None
            
            data = db.get_sales_by_year_month(
                metric=self.selected_metric_year_month,
                start_date=self.start_date_month if self.start_date_month else None,
                end_date=self.end_date_month if self.end_date_month else None,
                state_filter=state_filter,
                category_filter=category_filter
            )
            
            if data:
                df = pd.DataFrame(data)
                
                self.fig_sales_by_year_month = px.line(
                    df,
                    x="yyyymm",
                    y=self.selected_metric_year_month,
                    title=f"Ventas por Año-Mes - {self.temporal_metric_labels[self.selected_metric_year_month]}",
                    markers=True
                )
                
                self.fig_sales_by_year_month.update_layout(
                    autosize=True,
                    height=500,
                    xaxis_title="Año-Mes",
                    yaxis_title=self.temporal_metric_labels[self.selected_metric_year_month],
                    hovermode='x unified'
                )
                
                self.has_year_month_data = True  # ✅ Activar flag
            else:
                self.has_year_month_data = False  # ✅ Desactivar flag
                return rx.toast.warning(
                    "No existen datos para el rango de fechas seleccionado",
                    position="top-right",
                    duration=4000,
                )
                
        except Exception as e:
            print(f"Error loading year-month chart: {e}")
            self.has_year_month_data = False  # ✅ Desactivar flag
        finally:
            self.loading_chart_year_month = False
    
    @rx.event
    def load_sales_by_year_month_day(self):
        """Carga el gráfico de ventas por año-mes-día"""
        self.loading_chart_year_month_day = True
        
        try:
            state_filter = self.selected_state_filter if self.selected_state_filter else None
            category_filter = self.selected_category_filter if self.selected_category_filter else None
            
            data = db.get_sales_by_year_month_day(
                metric=self.selected_metric_year_month_day,
                start_date=self.start_date_day if self.start_date_day else None,
                end_date=self.end_date_day if self.end_date_day else None,
                state_filter=state_filter,
                category_filter=category_filter
            )
            
            if data:
                df = pd.DataFrame(data)
                
                self.fig_sales_by_year_month_day = px.line(
                    df,
                    x="yyyymmdd",
                    y=self.selected_metric_year_month_day,
                    title=f"Ventas por Año-Mes-Día - {self.temporal_metric_labels[self.selected_metric_year_month_day]}",
                    markers=True
                )
                
                self.fig_sales_by_year_month_day.update_layout(
                    autosize=True,
                    height=500,
                    xaxis_title="Fecha",
                    yaxis_title=self.temporal_metric_labels[self.selected_metric_year_month_day],
                    hovermode='x unified'
                )
                
                self.has_year_month_day_data = True  # ✅ Activar flag
            else:
                self.has_year_month_day_data = False  # ✅ Desactivar flag
                return rx.toast.warning(
                    "No existen datos para el rango de fechas seleccionado",
                    position="top-right",
                    duration=4000,
                )
                
        except Exception as e:
            print(f"Error loading year-month-day chart: {e}")
            self.has_year_month_day_data = False  # ✅ Desactivar flag
        finally:
            self.loading_chart_year_month_day = False
    
    @rx.event
    def update_metric_year(self, metric: str):
        """Actualiza la métrica del gráfico de año-mes-día"""
        self.selected_metric_year = metric
        self.load_sales_by_year()
    
    @rx.event
    def update_metric_year_month(self, metric: str):
        """Actualiza la métrica del gráfico de año-mes-día"""
        self.selected_metric_year_month = metric
        self.load_sales_by_year_month()


    @rx.event
    def update_metric_year_month_day(self, metric: str):
        """Actualiza la métrica del gráfico de año-mes-día"""
        self.selected_metric_year_month_day = metric
        self.load_sales_by_year_month_day()
    
    @rx.event
    def set_start_date_day(self, value: str):
        """Actualiza la fecha de inicio para el análisis diario"""
        self.start_date_day = value
    
    @rx.event
    def set_end_date_day(self, value: str):
        """Actualiza la fecha de fin para el análisis diario"""
        self.end_date_day = value
    
    @rx.event
    def apply_day_filters(self):
        """Aplica los filtros de fecha para el análisis diario"""
        self.load_sales_by_year_month_day()
    @rx.event
    def apply_month_filters(self):
        """Aplica los filtros de fecha para el análisis mensual"""
        self.load_sales_by_year_month()
    @rx.event
    def apply_year_filters(self):
        """Aplica los filtros de fecha para el análisis anual"""
        self.load_sales_by_year()

    @rx.event
    def load_all_temporal_charts(self):
        """Carga todos los gráficos temporales"""
        self.load_sales_by_year()
        self.load_sales_by_year_month()
        self.load_sales_by_year_month_day()


# ==================== COMPONENTES UI ====================

def navbar() -> rx.Component:
    """Barra de navegación del dashboard"""
    return rx.box(
        rx.hstack(
            rx.heading("📊 Dashboard Analytics", size="6"),
            rx.spacer(),
            rx.hstack(
                nav_button("📈 Overview", "overview"),
                nav_button("📊 Gráficos", "charts"),
                nav_button("🔍 Análisis", "analysis"),
                nav_button("📉 Estadísticas", "statistics"),
                nav_button("📅 Temporal", "temporal"),
                spacing="2",
            ),
            width="100%",
            align="center",
            padding="1em",
        ),
        style={
            "background": "var(--gray-3)",
            "border_bottom": "1px solid var(--gray-6)",
            "position": "sticky",
            "top": "0",
            "z_index": "1000",
        }
    )


def nav_button(label: str, page: str) -> rx.Component:
    """Botón de navegación"""
    return rx.button(
        label,
        on_click=lambda: DashboardState.navigate_to(page),
        variant=rx.cond(
            DashboardState.current_page == page,
            "solid",
            "soft"
        ),
        color_scheme=rx.cond(
            DashboardState.current_page == page,
            "blue",
            "gray"
        ),
        size="2",
    )


def metric_card(title: str, value: str, subtitle: str = "", icon: str = "📊", color: str = "blue") -> rx.Component:
    """Tarjeta de métrica"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(icon, font_size="2.5em"),
                rx.spacer(),
            ),
            rx.text(title, size="2", color="gray", weight="medium"),
            rx.text(value, size="7", weight="bold", color=color),
            rx.cond(
                subtitle != "",
                rx.text(subtitle, size="2", color="gray"),
                rx.fragment()
            ),
            spacing="2",
            align="start",
        ),
        style={"padding": "1.5em", "height": "100%", "background": "var(--gray-2)"}
    )


def global_filters_section() -> rx.Component:
    """Sección de filtros globales mejorada"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("🔍 Filtros Globales", size="5"),
                rx.spacer(),
                rx.cond(
                    DashboardState.has_active_filters,
                    rx.button(
                        "🗑️ Limpiar Filtros",
                        on_click=DashboardState.clear_global_filters,
                        size="2",
                        color_scheme="red",
                        variant="soft",
                    ),
                ),
                width="100%",
                align="center",
            ),
            
            rx.divider(),
            
            # Indicador de filtros activos
            rx.callout(
                rx.text(DashboardState.active_filters_text, size="2"),
                icon="filter",
                color_scheme=rx.cond(
                    DashboardState.has_active_filters,
                    "blue",
                    "gray"
                ),
            ),
            
            # Grid de filtros
            rx.grid(
                # Rango de fechas
                rx.vstack(
                    rx.text("📅 Fecha Inicio", size="2", weight="bold"),
                    rx.input(
                        type="date",
                        value=DashboardState.start_date,
                        on_change=DashboardState.set_start_date,
                        min=DashboardState.min_available_date,
                        max=DashboardState.max_available_date,
                        size="2",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("📅 Fecha Fin", size="2", weight="bold"),
                    rx.input(
                        type="date",
                        value=DashboardState.end_date,
                        on_change=DashboardState.set_end_date,
                        min=DashboardState.min_available_date,
                        max=DashboardState.max_available_date,
                        size="2",
                    ),
                    align="start",
                    spacing="1",
                ),
                # Filtro por Estado
                rx.vstack(
                    rx.text("📍 Estado", size="2", weight="bold"),
                    rx.select(
                        DashboardState.states_filter_options,
                        placeholder="Todos los estados",
                        value=rx.cond(
                            DashboardState.selected_state_filter == "",
                            "Todos",
                            DashboardState.selected_state_filter
                        ),
                        on_change=DashboardState.set_state_filter,
                        size="2",
                    ),
                    align="start",
                    spacing="1",
                ),
                # Filtro por Categoría
                rx.vstack(
                    rx.text("🏷️ Categoría", size="2", weight="bold"),
                    rx.select(
                        DashboardState.categories_filter_options,
                        placeholder="Todas las categorías",
                        value=rx.cond(
                            DashboardState.selected_category_filter == "",
                            "Todas",
                            DashboardState.selected_category_filter
                        ),
                        on_change=DashboardState.set_category_filter,
                        size="2",
                    ),
                    align="start",
                    spacing="1",
                ),
                columns="4",
                spacing="3",
                width="100%",
            ),
            
            # Botón aplicar
            rx.button(
                "✅ Aplicar Filtros",
                on_click=DashboardState.apply_global_filters,
                size="3",
                color_scheme="blue",
                width="100%",
            ),
            
            spacing="3",
            align="start",
            width="100%",
        ),
        style={"padding": "1.5em", "background": "var(--gray-2)"}
    )


def stats_grid(title: str, stats: dict) -> rx.Component:
    """Grid de estadísticas"""
    return rx.card(
        rx.vstack(
            rx.heading(title, size="5", margin_bottom="0.5em"),
            rx.divider(),
            rx.grid(
                rx.box(
                    rx.vstack(
                        rx.text("Media", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('media', 0):.2f}", size="5", weight="bold", color="blue"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Mediana", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('mediana', 0):.2f}", size="5", weight="bold", color="green"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Moda", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('moda', 0):.2f}", size="5", weight="bold", color="purple"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Desv. Estándar", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('desviacion_std', 0):.2f}", size="5", weight="bold", color="orange"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Q1 (25%)", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('q1', 0):.2f}", size="4", weight="bold"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Q2 (50%)", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('q2', 0):.2f}", size="4", weight="bold"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Q3 (75%)", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('q3', 0):.2f}", size="4", weight="bold"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("IQR", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('iqr', 0):.2f}", size="4", weight="bold"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Mínimo", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('minimo', 0):.2f}", size="4", weight="bold", color="red"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Máximo", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('maximo', 0):.2f}", size="4", weight="bold", color="green"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Observaciones", size="2", color="gray", weight="medium"),
                        rx.text(f"{stats.get('count', 0):,}", size="4", weight="bold"),
                        spacing="1",
                        align="start"
                    ),
                    grid_column="span 2"
                ),
                columns="4",
                spacing="4",
                width="100%",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        style={"padding": "2em"}
    )


def plotly_chart_card(
    title: str,
    figure: go.Figure,
    loading: bool,
    on_metric_change,
    on_limit_change,
    metric_options: list[str],
    limit_options: list[str],
    selected_metric: str,
    selected_limit: str,
    color: str = "blue"
) -> rx.Component:
    """Card para gráficos Plotly con controles dinámicos"""
    return rx.card(
        rx.vstack(
            rx.heading(title, size="6", color=f"{color}.11"),
            rx.hstack(
                rx.vstack(
                    rx.text("Métrica", size="2", weight="bold"),
                    rx.select(
                        metric_options,
                        value=selected_metric,
                        on_change=on_metric_change,
                        placeholder="Seleccionar métrica",
                        size="2",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.vstack(
                    rx.text("Top N", size="2", weight="bold"),
                    rx.select(
                        limit_options,
                        value=selected_limit,
                        on_change=on_limit_change,
                        placeholder="Cantidad",
                        size="2",
                    ),
                    spacing="1",
                    align="start",
                ),
                spacing="4",
                width="100%",
            ),
            rx.divider(),
            rx.cond(
                loading,
                rx.center(
                    rx.vstack(
                        rx.spinner(size="3"),
                        rx.text("Cargando datos...", size="2"),
                        spacing="2",
                    ),
                    height="500px",
                ),
                rx.plotly(data=figure, layout={"responsive": True})
            ),
            spacing="4",
            width="100%",
        ),
        width="100%",
        style={"padding": "2em"}
    )


def overview_metrics() -> rx.Component:
    """Métricas generales en tarjetas"""
    return rx.grid(
        metric_card(
            "Total Órdenes",
            f"{DashboardState.overview_metrics.get('total_ordenes', 0):,.0f}",
            "Órdenes procesadas",
            "🛒",
            "blue"
        ),
        metric_card(
            "Ventas Totales",
            f"${DashboardState.overview_metrics.get('ventas_totales', 0):,.2f}",
            "Ingresos generados",
            "💰",
            "green"
        ),
        metric_card(
            "Ticket Promedio",
            f"${DashboardState.overview_metrics.get('ticket_promedio', 0):,.2f}",
            "Valor por orden",
            "🎫",
            "purple"
        ),
        metric_card(
            "Clientes Únicos",
            f"{DashboardState.overview_metrics.get('clientes_unicos', 0):,.0f}",
            "Clientes activos",
            "👥",
            "orange"
        ),
        metric_card(
            "Vendedores Activos",
            f"{DashboardState.overview_metrics.get('vendedores_activos', 0):,.0f}",
            "En el período",
            "🪙",
            "red"
        ),
        columns="5",
        spacing="4",
        width="100%",
    )


def top_performers() -> rx.Component:
    """Top vendedor, cliente y producto"""
    return rx.grid(
        # Top Vendedor
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.text("🏆", font_size="2em"),
                    rx.heading("Mejor Vendedor", size="4"),
                    spacing="2",
                ),
                rx.divider(),
                rx.cond(
                    DashboardState.top_seller_data != {},
                    rx.vstack(
                        rx.text(
                            DashboardState.seller_id_display,
                            weight="bold",
                            size="5"
                        ),
                        rx.text(
                            f"📍 {DashboardState.top_seller_data.get('seller_city', '')}, {DashboardState.top_seller_data.get('seller_state', '')}",
                            color="gray",
                            size="2"
                        ),
                        rx.divider(),
                        rx.vstack(
                            rx.hstack(
                                rx.text("Ventas:", size="2", color="gray"),
                                rx.text(
                                    f"${DashboardState.top_seller_data.get('ventas_totales', 0):,.2f}",
                                    weight="bold",
                                    size="4",
                                    color="green"
                                ),
                                spacing="2",
                            ),
                            rx.hstack(
                                rx.text("Órdenes:", size="2", color="gray"),
                                rx.text(
                                    f"{DashboardState.top_seller_data.get('total_ordenes', 0):,.0f}",
                                    weight="bold",
                                    size="4"
                                ),
                                spacing="2",
                            ),
                            spacing="1",
                            align="start",
                            width="100%",
                        ),
                        spacing="2",
                        align="start",
                        width="100%",
                    ),
                    rx.text("Sin datos", color="gray")
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            style={"padding": "1.5em", "height": "100%"}
        ),
        # Top Cliente
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.text("🌟", font_size="2em"),
                    rx.heading("Mejor Cliente", size="4"),
                    spacing="2",
                ),
                rx.divider(),
                rx.cond(
                    DashboardState.top_customer_data != {},
                    rx.vstack(
                        rx.text(
                            DashboardState.customer_id_display,
                            weight="bold",
                            size="5"
                        ),
                        rx.text(
                            f"📍 {DashboardState.top_customer_data.get('customer_city', '')}, {DashboardState.top_customer_data.get('customer_state', '')}",
                            color="gray",
                            size="2"
                        ),
                        rx.divider(),
                        rx.vstack(
                            rx.hstack(
                                rx.text("Compras:", size="2", color="gray"),
                                rx.text(
                                    f"${DashboardState.top_customer_data.get('total_comprado', 0):,.2f}",
                                    weight="bold",
                                    size="4",
                                    color="green"
                                ),
                                spacing="2",
                            ),
                            rx.hstack(
                                rx.text("Órdenes:", size="2", color="gray"),
                                rx.text(
                                    f"{DashboardState.top_customer_data.get('total_ordenes', 0):,.0f}",
                                    weight="bold",
                                    size="4"
                                ),
                                spacing="2",
                            ),
                            spacing="1",
                            align="start",
                            width="100%",
                        ),
                        spacing="2",
                        align="start",
                        width="100%",
                    ),
                    rx.text("Sin datos", color="gray")
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            style={"padding": "1.5em", "height": "100%"}
        ),
        # Top Producto
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.text("🥇", font_size="2em"),
                    rx.heading("Producto Más Vendido", size="4"),
                    spacing="2",
                ),
                rx.divider(),
                rx.cond(
                    DashboardState.top_product_data != {},
                    rx.vstack(
                        rx.text(
                            DashboardState.product_id_display,
                            weight="bold",
                            size="5"
                        ),
                        rx.text(
                            DashboardState.top_product_data.get('categoria', 'N/A'),
                            color="gray",
                            size="2"
                        ),
                        rx.divider(),
                        rx.vstack(
                            rx.hstack(
                                rx.text("Unidades:", size="2", color="gray"),
                                rx.text(
                                    f"{DashboardState.top_product_data.get('unidades_vendidas', 0):,.0f}",
                                    weight="bold",
                                    size="4",
                                    color="white"
                                ),
                                spacing="2",
                            ),
                            rx.hstack(
                                rx.text("Ventas:", size="2", color="gray"),
                                rx.text(
                                    f"${DashboardState.top_product_data.get('ventas_totales', 0):,.2f}",
                                    weight="bold",
                                    size="4",
                                    color="green"
                                ),
                                spacing="2",
                            ),
                            spacing="1",
                            align="start",
                            width="100%",
                        ),
                        spacing="2",
                        align="start",
                        width="100%",
                    ),
                    rx.text("Sin datos", color="gray")
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            style={"padding": "1.5em", "height": "100%"}
        ),
        columns="3",
        spacing="4",
    )


def overview_page() -> rx.Component:
    """Página Overview"""
    return rx.vstack(
        rx.heading("📈 Vista General", size="7"),
        overview_metrics(),
        top_performers(),
        spacing="5",
        width="100%",
    )


def charts_page() -> rx.Component:
    """Página de Gráficos Plotly"""
    return rx.vstack(
        rx.card(
            rx.hstack(
                rx.heading("📊 Gráficos Interactivos Dinámicos", size="6"),
                rx.spacer(),
                rx.button(
                    "🔄 Cargar Todos los Gráficos",
                    on_click=DashboardState.load_all_plotly_charts,
                    size="3",
                    color_scheme="blue",
                ),
                width="100%",
                align="center",
            ),
            style={"padding": "1.5em", "background": "var(--gray-2)"}
        ),
        rx.callout(
            rx.text("💡 Usa los selectores para cambiar la métrica y la cantidad de resultados mostrados"),
            icon="info",
            color="white",
        ),
        rx.grid(
            plotly_chart_card(
                title="📍 Ventas por Estado",
                figure=DashboardState.fig_states_plotly,
                loading=DashboardState.loading_chart_states,
                on_metric_change=DashboardState.update_metric_state,
                on_limit_change=DashboardState.update_limit_state,
                metric_options=DashboardState.metric_options,
                limit_options=DashboardState.limit_options,
                selected_metric=DashboardState.selected_metric_state,
                selected_limit=DashboardState.num_states_to_show,
                color="blue",
            ),
            plotly_chart_card(
                title="🏙️ Ventas por Ciudad",
                figure=DashboardState.fig_cities_plotly,
                loading=DashboardState.loading_chart_cities,
                on_metric_change=DashboardState.update_metric_city,
                on_limit_change=DashboardState.update_limit_city,
                metric_options=DashboardState.metric_options,
                limit_options=DashboardState.limit_options,
                selected_metric=DashboardState.selected_metric_city,
                selected_limit=DashboardState.num_cities_to_show,
                color="green",
            ),
            plotly_chart_card(
                title="🏷️ Ventas por Categoría",
                figure=DashboardState.fig_categories_plotly,
                loading=DashboardState.loading_chart_categories,
                on_metric_change=DashboardState.update_metric_category,
                on_limit_change=DashboardState.update_limit_category,
                metric_options=DashboardState.metric_options,
                limit_options=DashboardState.limit_options,
                selected_metric=DashboardState.selected_metric_category,
                selected_limit=DashboardState.num_categories_to_show,
                color="purple",
            ),
            plotly_chart_card(
                title="🪙 Ventas por Vendedor",
                figure=DashboardState.fig_sellers_plotly,
                loading=DashboardState.loading_chart_sellers,
                on_metric_change=DashboardState.update_metric_seller,
                on_limit_change=DashboardState.update_limit_seller,
                metric_options=DashboardState.metric_options,
                limit_options=DashboardState.limit_options,
                selected_metric=DashboardState.selected_metric_seller,
                selected_limit=DashboardState.num_sellers_to_show,
                color="orange",
            ),
            columns="1",
            spacing="5",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def analysis_page() -> rx.Component:
    """Página de Análisis (Gráficos Recharts)"""
    return rx.vstack(
        rx.heading("🔍 Análisis por Dimensión", size="7"),
        rx.card(
            rx.vstack(
                rx.heading("📊 Top 10 Estados por Ventas", size="5"),
                rx.divider(),
                rx.cond(
                    DashboardState.has_data,
                    rx.recharts.composed_chart(
                        rx.recharts.bar(
                            data_key="ventas",
                            fill="#8884d8",
                        ),
                        rx.recharts.x_axis(data_key="estado"),
                        rx.recharts.y_axis(),
                        rx.recharts.tooltip(),
                        rx.recharts.legend(),
                        data=DashboardState.top_states_chart,
                        width="100%",
                        height=400,
                    ),
                    rx.center(
                        rx.text("No hay datos disponibles", color="gray", size="4"),
                        padding="4em"
                    )
                ),
                spacing="3",
                width="100%",
            ),
            style={"padding": "2em"}
        ),
        rx.card(
            rx.vstack(
                rx.heading("🏷️ Top 10 Categorías por Ventas", size="5"),
                rx.divider(),
                rx.cond(
                    DashboardState.has_data,
                    rx.recharts.composed_chart(
                        rx.recharts.bar(
                            data_key="ventas",
                            fill="#82ca9d",
                        ),
                        rx.recharts.x_axis(
                            data_key="categoria", 
                            angle=-45, 
                            text_anchor="end", 
                            height=100
                        ),
                        rx.recharts.y_axis(),
                        rx.recharts.tooltip(),
                        rx.recharts.legend(),
                        data=DashboardState.categories_chart,
                        width="100%",
                        height=450,
                    ),
                    rx.center(
                        rx.text("No hay datos disponibles", color="gray", size="4"),
                        padding="4em"
                    )
                ),
                spacing="3",
                width="100%",
            ),
            style={"padding": "2em"}
        ),
        rx.card(
            rx.vstack(
                rx.heading("📉 Bottom 10 Estados por Ventas", size="5"),
                rx.divider(),
                rx.cond(
                    DashboardState.has_data,
                    rx.recharts.composed_chart(
                        rx.recharts.bar(
                            data_key="ventas",
                            fill="#ff7c7c",
                        ),
                        rx.recharts.x_axis(data_key="estado"),
                        rx.recharts.y_axis(),
                        rx.recharts.tooltip(),
                        rx.recharts.legend(),
                        data=DashboardState.bottom_states_chart,
                        width="100%",
                        height=400,
                    ),
                    rx.center(
                        rx.text("No hay datos disponibles", color="gray", size="4"),
                        padding="4em"
                    )
                ),
                spacing="3",
                width="100%",
            ),
            style={"padding": "2em"}
        ),
        spacing="4",
        width="100%",
    )


def statistics_page() -> rx.Component:
    """Página de Estadísticas"""
    return rx.vstack(
        rx.heading("📉 Análisis Estadístico", size="7"),
        rx.card(
            rx.vstack(
                rx.heading("🔧 Configuración de Análisis", size="5", color="gray"),
                rx.grid(
                    rx.vstack(
                        rx.text("Métrica", size="2", weight="bold"),
                        rx.select(
                            ["total", "price", "freight_value"],
                            value=DashboardState.selected_metric,
                            on_change=DashboardState.set_metric,
                            size="3",
                        ),
                        align="start",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Agrupar por", size="2", weight="bold"),
                        rx.select(
                            ["customer_state", "seller_state", "customer_city", "product_category_name"],
                            value=DashboardState.selected_group,
                            on_change=DashboardState.set_group,
                            size="3",
                        ),
                        align="start",
                        spacing="1",
                    ),
                    columns="2",
                    spacing="3",
                    width="100%",
                ),
                rx.cond(
                    DashboardState.selected_group == "customer_state",
                    rx.vstack(
                        rx.text("Filtrar Estado", size="2", weight="bold"),
                        rx.select(
                            DashboardState.states_options,
                            placeholder="Selecciona un estado",
                            value=rx.cond(
                                DashboardState.selected_filter_value == "",
                                "Todos",
                                DashboardState.selected_filter_value
                            ),
                            on_change=DashboardState.set_filter_value,
                            size="3",
                        ),
                        align="start",
                        spacing="1",
                        width="100%",
                    ),
                ),
                rx.cond(
                    DashboardState.selected_group == "product_category_name",
                    rx.vstack(
                        rx.text("Filtrar Categoría", size="2", weight="bold"),
                        rx.select(
                            DashboardState.categories_options,
                            placeholder="Selecciona una categoría",
                            value=rx.cond(
                                DashboardState.selected_filter_value == "",
                                "Todas",
                                DashboardState.selected_filter_value
                            ),
                            on_change=DashboardState.set_filter_value,
                            size="3",
                        ),
                        align="start",
                        spacing="1",
                        width="100%",
                    ),
                ),
                spacing="3",
                width="100%",
            ),
            style={"padding": "1.5em", "background": "var(--gray-2)"}
        ),
        stats_grid("📊 Análisis Estadístico Descriptivo", DashboardState.statistics_data),
        spacing="4",
        width="100%",
    )


def temporal_analysis_page() -> rx.Component:
    """Página de Análisis Temporal - Ventas por Día, Mes y Año"""
    return rx.vstack(
        # Header
        rx.card(
            rx.hstack(
                rx.heading("📅 Análisis Temporal de Ventas", size="6"),
                rx.spacer(),
                rx.button(
                    "🔄 Cargar Todos los Gráficos",
                    on_click=DashboardState.load_all_temporal_charts,
                    size="3",
                    color_scheme="blue",
                ),
                width="100%",
                align="center",
            ),
            style={"padding": "1.5em", "background": "var(--gray-2)"}
        ),
        
        rx.callout(
            rx.text("📊 Visualiza las tendencias de ventas a lo largo del tiempo. Los filtros globales de estado y categoría se aplican a todos los gráficos."),
            icon="info",
            color_scheme="blue",
        ),
        
        # ==================== GRÁFICO POR AÑO ====================
        rx.card(
            rx.vstack(
                rx.heading("📈 Ventas por Año", size="5", color="blue.11"),
                
                # Selector de métrica
                rx.hstack(
                    rx.vstack(
                        rx.text("Métrica", size="2", weight="bold"),
                        rx.select(
                            DashboardState.temporal_metric_options,
                            value=DashboardState.selected_metric_year,
                            on_change=DashboardState.update_metric_year,
                            placeholder="Seleccionar métrica",
                            size="2",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    spacing="4",
                    width="100%",
                ),
                
                rx.divider(),
                
                # Gráfico - ✅ USAR has_year_data en lugar de .data
                rx.cond(
                    DashboardState.loading_chart_year,
                    rx.center(
                        rx.vstack(
                            rx.spinner(size="3"),
                            rx.text("Cargando datos...", size="2"),
                            spacing="2",
                        ),
                        height="500px",
                    ),
                    rx.cond(
                        DashboardState.has_year_data,  # ✅ Cambio aquí
                        rx.plotly(
                            data=DashboardState.fig_sales_by_year,
                            layout={"responsive": True}
                        ),
                        rx.center(
                            rx.text("No hay datos disponibles. Haz clic en 'Cargar Todos los Gráficos'", 
                                   color="gray", size="3"),
                            height="500px",
                        )
                    )
                ),
                
                spacing="4",
                width="100%",
            ),
            width="100%",
            style={"padding": "2em"}
        ),
        
        # ==================== GRÁFICO POR AÑO-MES ====================
        rx.card(
            rx.vstack(
                rx.heading("📊 Ventas por Año-Mes", size="5", color="green.11"),
                
                # Controles
                rx.hstack(
                    rx.vstack(
                        rx.text("Métrica", size="2", weight="bold"),
                        rx.select(
                            DashboardState.temporal_metric_options,
                            value=DashboardState.selected_metric_year_month,
                            on_change=DashboardState.update_metric_year_month,
                            placeholder="Seleccionar métrica",
                            size="2",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.vstack(
                        rx.text("📅 Fecha Inicio", size="2", weight="bold"),
                        rx.input(
                            type="date",
                            value=DashboardState.start_date_month,
                            on_change=DashboardState.set_start_date_month,
                            size="2",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.vstack(
                        rx.text("📅 Fecha Fin", size="2", weight="bold"),
                        rx.input(
                            type="date",
                            value=DashboardState.end_date_month,
                            on_change=DashboardState.set_end_date_month,
                            size="2",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.button(
                        "✅ Aplicar Fechas",
                        on_click=DashboardState.apply_month_filters,
                        size="2",
                        color_scheme="blue",
                    ),
                    spacing="4",
                    width="100%",
                    align="end",
                ),
                
                rx.divider(),
                
                # Gráfico - ✅ USAR has_year_month_data
                rx.cond(
                    DashboardState.loading_chart_year_month,
                    rx.center(
                        rx.vstack(
                            rx.spinner(size="3"),
                            rx.text("Cargando datos...", size="2"),
                            spacing="2",
                        ),
                        height="500px",
                    ),
                    rx.cond(
                        DashboardState.has_year_month_data,  # ✅ Cambio aquí
                        rx.plotly(
                            data=DashboardState.fig_sales_by_year_month,
                            layout={"responsive": True}
                        ),
                        rx.center(
                            rx.text("No hay datos disponibles. Selecciona un rango de fechas y haz clic en 'Aplicar Fechas'", 
                                   color="gray", size="3"),
                            height="500px",
                        )
                    )
                ),
                
                spacing="4",
                width="100%",
            ),
            width="100%",
            style={"padding": "2em"}
        ),
        
        # ==================== GRÁFICO POR AÑO-MES-DÍA ====================
        rx.card(
            rx.vstack(
                rx.heading("📉 Ventas por Año-Mes-Día", size="5", color="purple.11"),
                
                # Controles
                rx.hstack(
                    rx.vstack(
                        rx.text("Métrica", size="2", weight="bold"),
                        rx.select(
                            DashboardState.temporal_metric_options,
                            value=DashboardState.selected_metric_year_month_day,
                            on_change=DashboardState.update_metric_year_month_day,
                            placeholder="Seleccionar métrica",
                            size="2",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.vstack(
                        rx.text("📅 Fecha Inicio", size="2", weight="bold"),
                        rx.input(
                            type="date",
                            value=DashboardState.start_date_day,
                            on_change=DashboardState.set_start_date_day,
                            size="2",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.vstack(
                        rx.text("📅 Fecha Fin", size="2", weight="bold"),
                        rx.input(
                            type="date",
                            value=DashboardState.end_date_day,
                            on_change=DashboardState.set_end_date_day,
                            size="2",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.button(
                        "✅ Aplicar Fechas",
                        on_click=DashboardState.apply_day_filters,
                        size="2",
                        color_scheme="blue",
                    ),
                    spacing="4",
                    width="100%",
                    align="end",
                ),
                
                rx.callout(
                    rx.text("⚠️ Recomendación: Usa rangos de fechas cortos (1-3 meses) para mejor visualización de datos diarios"),
                    icon="alert-triangle",
                    color_scheme="orange",
                    size="1",
                ),
                
                rx.divider(),
                
                # Gráfico - ✅ USAR has_year_month_day_data
                rx.cond(
                    DashboardState.loading_chart_year_month_day,
                    rx.center(
                        rx.vstack(
                            rx.spinner(size="3"),
                            rx.text("Cargando datos...", size="2"),
                            spacing="2",
                        ),
                        height="500px",
                    ),
                    rx.cond(
                        DashboardState.has_year_month_day_data,  # ✅ Cambio aquí
                        rx.plotly(
                            data=DashboardState.fig_sales_by_year_month_day,
                            layout={"responsive": True}
                        ),
                        rx.center(
                            rx.text("No hay datos disponibles. Selecciona un rango de fechas y haz clic en 'Aplicar Fechas'", 
                                   color="gray", size="3"),
                            height="500px",
                        )
                    )
                ),
                
                spacing="4",
                width="100%",
            ),
            width="100%",
            style={"padding": "2em"}
        ),
        
        spacing="4",
        width="100%",
    )


def index() -> rx.Component:
    """Página principal del dashboard"""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                # Header con loading
                rx.hstack(
                    rx.vstack(
                        rx.heading("Dashboard Analytics - Versión Mejorada", size="8"),
                        rx.text("Sistema de análisis con filtros globales y navegación por secciones", size="4", color="gray"),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.cond(
                        DashboardState.is_loading,
                        rx.spinner(size="3"),
                    ),
                    width="100%",
                    align="center",
                ),
                rx.divider(size="4"),
                
                # Filtros globales (siempre visibles)
                global_filters_section(),
                
                # Contenido según página activa
                rx.cond(
                    DashboardState.current_page == "overview",
                    overview_page(),
                ),
                rx.cond(
                    DashboardState.current_page == "charts",
                    charts_page(),
                ),
                rx.cond(
                    DashboardState.current_page == "analysis",
                    analysis_page(),
                ),
                rx.cond(
                    DashboardState.current_page == "statistics",
                    statistics_page(),
                ),
                rx.cond(
                    DashboardState.current_page == "temporal",
                    temporal_analysis_page(),
                ),
                
                spacing="5",
                width="100%",
                padding="2em",
            ),
            size="4",
        ),
    )


# Configuración de la app
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="gray",
        gray_color="slate",
    )
)
app.add_page(index, on_load=DashboardState.on_mount)