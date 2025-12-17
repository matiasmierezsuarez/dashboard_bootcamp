"""
State - Estado principal del dashboard
VERSIÓN CORREGIDA: Sin sub-estados como variables
"""
import reflex as rx
from datetime import datetime, timedelta
from .database import db
import plotly.graph_objects as go
from plotly.graph_objects import Figure


class DashboardState(rx.State):
    """Estado principal del dashboard"""
    
    # ==================== NAVEGACIÓN ====================
    current_page: str = "overview"
    is_loading: bool = False
    
    # ==================== DATOS PARA GRÁFICOS RECHARTS ====================
    top_states_chart: list[dict] = []
    bottom_states_chart: list[dict] = []
    categories_chart: list[dict] = []

    # ==================== DATOS PARA MÉTRICAS ====================
    top_product_data: dict = {}
    top_seller_data: dict = {}
    top_customer_data: dict = {}
    overview_metrics: dict = {}
    statistics_data: dict = {}

    # ==================== FILTROS GLOBALES ====================
    start_date: str = ""
    end_date: str = ""
    min_available_date: str = ""
    max_available_date: str = ""
    selected_state_filter: str = ""
    selected_category_filter: str = ""
    
    # ==================== FILTROS ADICIONALES PARA ESTADÍSTICAS ====================
    selected_metric: str = "total"
    selected_group: str = "customer_state"
    selected_filter_value: str = ""

    # ==================== OPCIONES PARA FILTROS ====================
    available_states: list[str] = []
    available_categories: list[str] = []

    # ==================== DATOS PARA GRÁFICOS PLOTLY ====================
    fig_states_plotly: go.Figure = go.Figure()
    fig_cities_plotly: go.Figure = go.Figure()
    fig_categories_plotly: go.Figure = go.Figure()
    fig_sellers_plotly: go.Figure = go.Figure()

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

    # ==================== ANÁLISIS TEMPORAL ====================
    fig_sales_by_year: go.Figure = go.Figure()
    fig_sales_by_year_month: go.Figure = go.Figure()
    fig_sales_by_year_month_day: go.Figure = go.Figure()
    
    selected_metric_year: str = "sum_sales"
    selected_metric_year_month: str = "sum_sales"
    selected_metric_year_month_day: str = "sum_sales"
    
    start_date_month: str = ""
    end_date_month: str = ""
    start_date_day: str = ""
    end_date_day: str = ""
    
    loading_chart_year: bool = False
    loading_chart_year_month: bool = False
    loading_chart_year_month_day: bool = False

    has_year_data: bool = False
    has_year_month_data: bool = False
    has_year_month_day_data: bool = False

    # ==================== COMPUTED VARS ====================
    
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
        return bool(self.start_date or self.end_date or self.selected_state_filter or self.selected_category_filter)
    
    @rx.var
    def metric_labels(self) -> dict:
        """Etiquetas para las métricas"""
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
    def temporal_metric_options(self) -> list[str]:
        return list(self.temporal_metric_labels.keys())
    
    # ==================== NAVEGACIÓN ====================
    
    def navigate_to(self, page: str):
        """Cambia la página actual"""
        self.current_page = page
    
    # ==================== EVENTOS PRINCIPALES ====================
    
    def on_mount(self):
        """Se ejecuta al cargar la página - CORREGIDO"""
        self.is_loading = True
        
        # Cargar fechas disponibles
        min_date, max_date = db.get_date_range()
        self.min_available_date = min_date
        self.max_available_date = max_date
        
        # Configurar rango de fechas por defecto (últimos 90 días)
        end = datetime.strptime(max_date, "%Y-%m-%d")
        start = end - timedelta(days=90)
        self.start_date = start.strftime("%Y-%m-%d")
        self.end_date = max_date
        
        # Cargar opciones de filtros
        self.available_states = db.get_available_states()
        self.available_categories = db.get_available_categories()
        
        # Cargar todos los datos iniciales
        self.refresh_all_data()
        self.init_temporal_dates()
        
        self.is_loading = False

    # ==================== MÉTODOS DE DATOS ====================
    
    def refresh_all_data(self):
        """Actualiza todos los datos con filtros globales"""
        state_filter = self.selected_state_filter or None
        category_filter = self.selected_category_filter or None

        # Métricas generales
        self.overview_metrics = db.get_overview_metrics(
            start_date=self.start_date or None,
            end_date=self.end_date or None,
            state_filter=state_filter,
            category_filter=category_filter
        )

        # Gráficos Recharts
        self._load_state_charts(state_filter, category_filter)

        # Top performers
        self._load_top_entities(state_filter, category_filter)

        # Estadísticas
        self.calculate_statistics()
    
    def calculate_statistics(self):
        """Calcula estadísticas con filtros globales"""
        self.statistics_data = db.get_statistics(
            metric=self.selected_metric,
            group_by=self.selected_group if self.selected_filter_value else None,
            filter_value=self.selected_filter_value if self.selected_filter_value else None,
            start_date=self.start_date if self.start_date else None,
            end_date=self.end_date if self.end_date else None,
            state_filter=self.selected_state_filter if self.selected_state_filter else None,
            category_filter=self.selected_category_filter if self.selected_category_filter else None
        )

    def _load_state_charts(self, state_filter, category_filter):
        import pandas as pd
        
        # Top Estados
        df_top = db.get_top_states_by_sales(
            self.start_date, self.end_date, 10,
            state_filter=state_filter,
            category_filter=category_filter
        )
        self.top_states_chart = [
            {
                "estado": row["estado"],
                "ventas": float(row["ventas_totales"]),
                "ordenes": int(row["total_ordenes"]),
            }
            for _, row in df_top.iterrows()
        ] if not df_top.empty else []

        # Bottom Estados
        df_bottom = db.get_bottom_states_by_sales(
            self.start_date, self.end_date, 10,
            state_filter=state_filter,
            category_filter=category_filter
        )
        self.bottom_states_chart = [
            {
                "estado": row["estado"],
                "ventas": float(row["ventas_totales"]),
                "ordenes": int(row["total_ordenes"]),
            }
            for _, row in df_bottom.iterrows()
        ] if not df_bottom.empty else []

        # Categorías
        df_categories = db.get_top_categories(
            self.start_date, self.end_date, 10,
            state_filter=state_filter,
            category_filter=category_filter
        )
        self.categories_chart = [
            {
                "categoria": row["categoria"][:20],
                "ventas": float(row["ventas_totales"]),
                "unidades": int(row["unidades_vendidas"]),
            }
            for _, row in df_categories.iterrows()
        ] if not df_categories.empty else []
    
    def _load_top_entities(self, state_filter, category_filter):
        df_product = db.get_top_product(
            self.start_date, self.end_date,
            state_filter=state_filter,
            category_filter=category_filter
        )
        self.top_product_data = df_product.iloc[0].to_dict() if not df_product.empty else {}

        df_seller = db.get_top_seller(
            self.start_date, self.end_date,
            state_filter=state_filter,
            category_filter=category_filter
        )
        self.top_seller_data = df_seller.iloc[0].to_dict() if not df_seller.empty else {}

        df_customer = db.get_top_customer(
            self.start_date, self.end_date,
            state_filter=state_filter,
            category_filter=category_filter
        )
        self.top_customer_data = df_customer.iloc[0].to_dict() if not df_customer.empty else {}

    # ==================== MÉTODOS DE FILTROS ====================
    
    def set_start_date(self, value: str):
        self.start_date = value
    
    def set_end_date(self, value: str):
        self.end_date = value
    
    def set_state_filter(self, value: str):
        self.selected_state_filter = "" if value == "Todos" else value
    
    def set_category_filter(self, value: str):
        self.selected_category_filter = "" if value == "Todas" else value
    
    def apply_global_filters(self):
        """Aplica filtros globales a todo el dashboard"""
        self.is_loading = True
        
        # Limpiar caché
        db._cache.clear()
        
        try:
            self.refresh_all_data()
            if self.current_page == "charts":
                self.load_all_plotly_charts()
            if self.current_page == "temporal":
                self.load_all_temporal_charts()
        finally:
            self.is_loading = False

    def clear_global_filters(self):
        """Limpia todos los filtros globales"""
        # Limpiar caché
        db._cache.clear()
        
        # Resetear filtros
        self.selected_state_filter = ""
        self.selected_category_filter = ""
        self.start_date = ""
        self.end_date = ""
        
        # Aplicar cambios
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

    # ==================== MÉTODOS PLOTLY ====================
    
    def load_states_plotly(self):
        """Carga el gráfico dinámico de estados con Plotly"""
        import pandas as pd
        import plotly.express as px
        
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
                
                fig = px.bar(
                    df,
                    x=self.selected_metric_state,
                    y="state",
                    orientation='h',
                    title=f"Ventas por Estado (Top {self.num_states_to_show})",
                    color=self.selected_metric_state,
                    color_continuous_scale="Blues"
                )
                self.fig_states_plotly = fig
                
        except Exception as e:
            print(f"Error loading states chart: {e}")
        finally:
            self.loading_chart_states = False
    
    def update_metric_state(self, metric: str):
        self.selected_metric_state = metric
        self.load_states_plotly()
    
    def update_limit_state(self, limit: str):
        try:
            self.num_states_to_show = str(max(5, int(limit)))
        except ValueError:
            self.num_states_to_show = "10"
        self.load_states_plotly()
    
    def load_cities_plotly(self):
        """Carga el gráfico dinámico de ciudades"""
        import pandas as pd
        import plotly.express as px
        
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
                
                fig = px.bar(
                    df,
                    x=self.selected_metric_city,
                    y="city",
                    orientation='h',
                    title=f"Ventas por Ciudad (Top {self.num_cities_to_show})",
                    color=self.selected_metric_city,
                    color_continuous_scale="Greens"
                )
                self.fig_cities_plotly = fig
                
        except Exception as e:
            print(f"Error loading cities chart: {e}")
        finally:
            self.loading_chart_cities = False
    
    def update_metric_city(self, metric: str):
        self.selected_metric_city = metric
        self.load_cities_plotly()
    
    def update_limit_city(self, limit: str):
        try:
            self.num_cities_to_show = str(max(5, int(limit)))
        except ValueError:
            self.num_cities_to_show = "10"
        self.load_cities_plotly()
    
    def load_categories_plotly(self):
        """Carga el gráfico dinámico de categorías"""
        import pandas as pd
        import plotly.express as px
        
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
                
                fig = px.bar(
                    df,
                    x=self.selected_metric_category,
                    y="category",
                    orientation='h',
                    title=f"Ventas por Categoría (Top {self.num_categories_to_show})",
                    color=self.selected_metric_category,
                    color_continuous_scale="Purples"
                )
                self.fig_categories_plotly = fig
                
        except Exception as e:
            print(f"Error loading categories chart: {e}")
        finally:
            self.loading_chart_categories = False
    
    def update_metric_category(self, metric: str):
        self.selected_metric_category = metric
        self.load_categories_plotly()
    
    def update_limit_category(self, limit: str):
        try:
            self.num_categories_to_show = str(max(5, int(limit)))
        except ValueError:
            self.num_categories_to_show = "10"
        self.load_categories_plotly()
    
    def load_sellers_plotly(self):
        """Carga el gráfico dinámico de vendedores"""
        import pandas as pd
        import plotly.express as px
        
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
                
                fig = px.bar(
                    df,
                    x=self.selected_metric_seller,
                    y="seller_display",
                    orientation='h',
                    title=f"Ventas por Vendedor (Top {self.num_sellers_to_show})",
                    color=self.selected_metric_seller,
                    color_continuous_scale="Oranges"
                )
                self.fig_sellers_plotly = fig
                
        except Exception as e:
            print(f"Error loading sellers chart: {e}")
        finally:
            self.loading_chart_sellers = False
    
    def update_metric_seller(self, metric: str):
        self.selected_metric_seller = metric
        self.load_sellers_plotly()
    
    def update_limit_seller(self, limit: str):
        try:
            self.num_sellers_to_show = str(max(5, int(limit)))
        except ValueError:
            self.num_sellers_to_show = "10"
        self.load_sellers_plotly()
    
    def load_all_plotly_charts(self):
        """Carga todos los gráficos Plotly"""
        self.load_states_plotly()
        self.load_cities_plotly()
        self.load_categories_plotly()
        self.load_sellers_plotly()

    # ==================== MÉTODOS TEMPORALES ====================
    
    def init_temporal_dates(self):
        """Inicializa las fechas para los gráficos temporales"""
        self.start_date_month = self.start_date
        self.end_date_month = self.end_date
        self.start_date_day = self.start_date
        self.end_date_day = self.end_date
    
    def load_sales_by_year(self):
        """Carga el gráfico de ventas por año"""
        import pandas as pd
        import plotly.express as px
        
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
                
                fig = px.line(
                    df,
                    x="date_year",
                    y=self.selected_metric_year,
                    title=f"Ventas por Año - {self.temporal_metric_labels.get(self.selected_metric_year)}",
                    markers=True
                )
                self.fig_sales_by_year = fig
                self.has_year_data = True
            else:
                self.has_year_data = False
                
        except Exception as e:
            print(f"Error loading year chart: {e}")
            self.has_year_data = False
        finally:
            self.loading_chart_year = False
    
    def load_sales_by_year_month(self):
        """Carga el gráfico de ventas por año-mes"""
        import pandas as pd
        import plotly.express as px
        
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
                
                fig = px.line(
                    df,
                    x="yyyymm",
                    y=self.selected_metric_year_month,
                    title=f"Ventas por Año-Mes - {self.temporal_metric_labels.get(self.selected_metric_year_month)}",
                    markers=True
                )
                self.fig_sales_by_year_month = fig
                self.has_year_month_data = True
            else:
                self.has_year_month_data = False
                
        except Exception as e:
            print(f"Error loading year-month chart: {e}")
            self.has_year_month_data = False
        finally:
            self.loading_chart_year_month = False
    
    def load_sales_by_year_month_day(self):
        """Carga el gráfico de ventas por año-mes-día"""
        import pandas as pd
        import plotly.express as px
        
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
                
                fig = px.line(
                    df,
                    x="yyyymmdd",
                    y=self.selected_metric_year_month_day,
                    title=f"Ventas por Año-Mes-Día - {self.temporal_metric_labels.get(self.selected_metric_year_month_day)}",
                    markers=True
                )
                self.fig_sales_by_year_month_day = fig
                self.has_year_month_day_data = True
            else:
                self.has_year_month_day_data = False
                
        except Exception as e:
            print(f"Error loading year-month-day chart: {e}")
            self.has_year_month_day_data = False
        finally:
            self.loading_chart_year_month_day = False
    
    def update_metric_year(self, metric: str):
        self.selected_metric_year = metric
        self.load_sales_by_year()
    
    def update_metric_year_month(self, metric: str):
        self.selected_metric_year_month = metric
        self.load_sales_by_year_month()
    
    def update_metric_year_month_day(self, metric: str):
        self.selected_metric_year_month_day = metric
        self.load_sales_by_year_month_day()
    
    def set_start_date_day(self, value: str):
        self.start_date_day = value
    
    def set_end_date_day(self, value: str):
        self.end_date_day = value
    
    def set_start_date_month(self, value: str):
        self.start_date_month = value
    
    def set_end_date_month(self, value: str):
        self.end_date_month = value
    
    def apply_day_filters(self):
        self.load_sales_by_year_month_day()
    
    def apply_month_filters(self):
        self.load_sales_by_year_month()
    
    def apply_year_filters(self):
        self.load_sales_by_year()
    
    def load_all_temporal_charts(self):
        """Carga todos los gráficos temporales"""
        self.load_sales_by_year()
        self.load_sales_by_year_month()
        self.load_sales_by_year_month_day()