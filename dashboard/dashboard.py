"""
Dashboard Analytics - Versión Mejorada con Gráficos Plotly Dinámicos
"""
import reflex as rx
from datetime import datetime, timedelta
from .database import db
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class DashboardState(rx.State):
    """Estado principal del dashboard"""
    
    # ==================== FILTROS DE FECHA ====================
    start_date: str = ""
    end_date: str = ""
    min_available_date: str = ""
    max_available_date: str = ""
    
    # ==================== FILTROS ADICIONALES ====================
    selected_metric: str = "total"
    selected_group: str = "customer_state"
    selected_filter_value: str = ""
    
    # ==================== DATOS PARA GRÁFICOS RECHARTS (ORIGINALES) ====================
    top_states_chart: list[dict] = []
    bottom_states_chart: list[dict] = []
    categories_chart: list[dict] = []
    
    # ==================== DATOS PARA GRÁFICOS PLOTLY (NUEVOS) ====================
    fig_states_plotly: go.Figure = go.Figure()
    fig_cities_plotly: go.Figure = go.Figure()
    fig_categories_plotly: go.Figure = go.Figure()
    fig_sellers_plotly: go.Figure = go.Figure()
    
    # ==================== CONTROLES PARA GRÁFICOS DINÁMICOS ====================
    # Estados
    selected_metric_state: str = "total_sales"
    num_states_to_show: str = "10"
    
    # Ciudades
    selected_metric_city: str = "total_sales"
    num_cities_to_show: str = "10"
    
    # Categorías
    selected_metric_category: str = "total_sales"
    num_categories_to_show: str = "10"
    
    # Vendedores
    selected_metric_seller: str = "total_sales"
    num_sellers_to_show: str = "10"
    
    # Opciones
    metric_options: list[str] = ["total_sales", "avg_sales", "total_orders", "avg_ticket"]
    limit_options: list[str] = ["5", "10", "15", "20", "25"]
    
    # ==================== FLAGS DE CARGA ====================
    loading_chart_states: bool = False
    loading_chart_cities: bool = False
    loading_chart_categories: bool = False
    loading_chart_sellers: bool = False
    
    # ==================== DATOS PARA MÉTRICAS (ORIGINALES) ====================
    top_product_data: dict = {}
    top_seller_data: dict = {}
    top_customer_data: dict = {}
    overview_metrics: dict = {}
    statistics_data: dict = {}
    
    # ==================== OPCIONES PARA FILTROS ====================
    available_states: list[str] = []
    available_categories: list[str] = []
    
    # ==================== ESTADO DE CARGA ====================
    is_loading: bool = False
    
    # ==================== COMPUTED VARS ====================
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
        """Etiquetas amigables para las métricas"""
        return {
            "total_sales": "Ventas Totales ($)",
            "avg_sales": "Promedio de Ventas ($)",
            "total_orders": "Total de Órdenes",
            "avg_ticket": "Ticket Promedio ($)"
        }
    
    # ==================== EVENTOS ORIGINALES ====================
    
    def on_mount(self):
        """Se ejecuta al cargar la página"""
        self.load_initial_data()
    
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
        self.refresh_data()
        self.is_loading = False
    
    def refresh_data(self):
        """Actualiza todos los datos del dashboard"""
        self.is_loading = True
        
        # Métricas generales
        self.overview_metrics = db.get_overview_metrics(
            self.start_date if self.start_date else None,
            self.end_date if self.end_date else None
        )
        
        # Top Estados - preparar para gráfico Recharts
        df_top = db.get_top_states_by_sales(self.start_date, self.end_date, 10)
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
        df_bottom = db.get_bottom_states_by_sales(self.start_date, self.end_date, 10)
        if not df_bottom.empty:
            self.bottom_states_chart = [
                {
                    "estado": row["estado"],
                    "ventas": float(row["ventas_totales"]),
                    "ordenes": int(row["total_ordenes"])
                }
                for _, row in df_bottom.iterrows()
            ]
        
        # Categorías - preparar para gráfico Recharts
        df_categories = db.get_top_categories(self.start_date, self.end_date, 10)
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
        df_product = db.get_top_product(self.start_date, self.end_date)
        self.top_product_data = df_product.iloc[0].to_dict() if not df_product.empty else {}
        
        # Top vendedor
        df_seller = db.get_top_seller(self.start_date, self.end_date)
        self.top_seller_data = df_seller.iloc[0].to_dict() if not df_seller.empty else {}
        
        # Top cliente
        df_customer = db.get_top_customer(self.start_date, self.end_date)
        self.top_customer_data = df_customer.iloc[0].to_dict() if not df_customer.empty else {}
        
        # Estadísticas
        self.calculate_statistics()
        self.is_loading = False
    
    def calculate_statistics(self):
        """Calcula estadísticas"""
        self.statistics_data = db.get_statistics(
            metric=self.selected_metric,
            group_by=self.selected_group if self.selected_filter_value else None,
            filter_value=self.selected_filter_value if self.selected_filter_value else None,
            start_date=self.start_date if self.start_date else None,
            end_date=self.end_date if self.end_date else None
        )
    
    def set_start_date(self, value: str):
        self.start_date = value
    
    def set_end_date(self, value: str):
        self.end_date = value
    
    def apply_date_filter(self):
        self.refresh_data()
        # Recargar también los gráficos Plotly si ya están cargados
        if self.fig_states_plotly.data:
            self.load_states_plotly()
        if self.fig_cities_plotly.data:
            self.load_cities_plotly()
        if self.fig_categories_plotly.data:
            self.load_categories_plotly()
        if self.fig_sellers_plotly.data:
            self.load_sellers_plotly()
    
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
    
    # ==================== NUEVOS EVENTOS PARA GRÁFICOS PLOTLY ====================
    
    @rx.event
    def load_states_plotly(self):
        """Carga el gráfico dinámico de estados con Plotly"""
        self.loading_chart_states = True
        
        try:
            # Obtener datos
            data = db.get_sales_by_state_dynamic(
                start_date=self.start_date if self.start_date else None,
                end_date=self.end_date if self.end_date else None,
                metric=self.selected_metric_state,
                limit=int(self.num_states_to_show)
            )
            
            if data:
                df = pd.DataFrame(data)
                
                # Crear gráfico
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
        """Actualiza la métrica del gráfico de estados"""
        self.selected_metric_state = metric
        self.load_states_plotly()
    
    @rx.event
    def update_limit_state(self, limit: str):
        """Actualiza la cantidad de estados"""
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
            data = db.get_sales_by_city_dynamic(
                start_date=self.start_date if self.start_date else None,
                end_date=self.end_date if self.end_date else None,
                metric=self.selected_metric_city,
                limit=int(self.num_cities_to_show)
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
        """Actualiza la métrica del gráfico de ciudades"""
        self.selected_metric_city = metric
        self.load_cities_plotly()
    
    @rx.event
    def update_limit_city(self, limit: str):
        """Actualiza la cantidad de ciudades"""
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
            data = db.get_sales_by_category_dynamic(
                start_date=self.start_date if self.start_date else None,
                end_date=self.end_date if self.end_date else None,
                metric=self.selected_metric_category,
                limit=int(self.num_categories_to_show)
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
        """Actualiza la métrica del gráfico de categorías"""
        self.selected_metric_category = metric
        self.load_categories_plotly()
    
    @rx.event
    def update_limit_category(self, limit: str):
        """Actualiza la cantidad de categorías"""
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
            data = db.get_sales_by_seller_dynamic(
                start_date=self.start_date if self.start_date else None,
                end_date=self.end_date if self.end_date else None,
                metric=self.selected_metric_seller,
                limit=int(self.num_sellers_to_show)
            )
            
            if data:
                df = pd.DataFrame(data)
                # Truncar IDs largos
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
        """Actualiza la métrica del gráfico de vendedores"""
        self.selected_metric_seller = metric
        self.load_sellers_plotly()
    
    @rx.event
    def update_limit_seller(self, limit: str):
        """Actualiza la cantidad de vendedores"""
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


# ==================== COMPONENTES UI ORIGINALES ====================

def metric_card(title: str, value: str, subtitle: str = "", icon: str = "📊", color: str = "blue") -> rx.Component:
    """Tarjeta de métrica con color"""
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


def filter_section() -> rx.Component:
    """Sección de filtros mejorada"""
    return rx.card(
        rx.vstack(
            rx.heading("🔍 Filtros y Configuración", size="5"),
            rx.divider(),
            
            # Filtros de fecha
            rx.vstack(
                rx.heading("📅 Rango de Fechas", size="3", color="gray"),
                rx.hstack(
                    rx.vstack(
                        rx.text("Desde", size="2", weight="bold"),
                        rx.input(
                            type="date",
                            value=DashboardState.start_date,
                            on_change=DashboardState.set_start_date,
                            min=DashboardState.min_available_date,
                            max=DashboardState.max_available_date,
                            size="3",
                        ),
                        align="start",
                        spacing="1",
                        flex="1",
                    ),
                    rx.vstack(
                        rx.text("Hasta", size="2", weight="bold"),
                        rx.input(
                            type="date",
                            value=DashboardState.end_date,
                            on_change=DashboardState.set_end_date,
                            min=DashboardState.min_available_date,
                            max=DashboardState.max_available_date,
                            size="3",
                        ),
                        align="start",
                        spacing="1",
                        flex="1",
                    ),
                    rx.button(
                        "Aplicar",
                        on_click=DashboardState.apply_date_filter,
                        size="3",
                        style={"margin_top": "1.8em"},
                        color_scheme="blue",
                    ),
                    spacing="3",
                    width="100%",
                ),
                spacing="2",
                width="100%",
            ),
            
            rx.divider(),
            
            # Filtros estadísticos
            rx.vstack(
                rx.heading("📊 Análisis Estadístico", size="3", color="gray"),
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
            
            spacing="4",
            align="start",
            width="100%",
        ),
        style={"padding": "1.5em", "background": "var(--gray-2)"}
    )

# ==================== NUEVOS COMPONENTES PARA GRÁFICOS PLOTLY ====================

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
            # Título
            rx.heading(title, size="6", color=f"{color}.11"),
            
            # Controles
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
            
            # Separador
            rx.divider(),
            
            # Gráfico o loading
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


def plotly_charts_section() -> rx.Component:
    """Sección de gráficos Plotly dinámicos"""
    return rx.vstack(
        # Header con botón para cargar todos
        rx.card(
            rx.hstack(
                rx.heading("📈 Gráficos Interactivos Dinámicos", size="6"),
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
        
        # Grid de gráficos
        rx.grid(
            # Gráfico por Estado
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
            
            # Gráfico por Ciudad
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
            
            # Gráfico por Categoría
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
            
            # Gráfico por Vendedor
            plotly_chart_card(
                title="🏪 Ventas por Vendedor",
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
            "🏪",
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


def charts_section_recharts() -> rx.Component:
    """Sección de gráficos Recharts originales"""
    return rx.vstack(
        rx.heading("📊 Gráficos con Recharts (Originales)", size="6"),
        
        # Gráfico: Top Estados
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
        
        # Gráfico: Categorías
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
        
        # Gráfico: Bottom Estados
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


def index() -> rx.Component:
    """Página principal del dashboard"""
    return rx.container(
        rx.vstack(
            # Header
            rx.hstack(
                rx.vstack(
                    rx.heading("📈 Dashboard Analytics - Versión Mejorada", size="8"),
                    rx.text("Sistema de análisis de ventas con visualizaciones interactivas Recharts + Plotly", size="4", color="gray"),
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
            
            # Filtros
            filter_section(),
            
            # Métricas generales
            overview_metrics(),
            
            # Top performers
            top_performers(),
            
            # NUEVA SECCIÓN: Gráficos Plotly Dinámicos
            plotly_charts_section(),
            
            # Gráficos Recharts Originales
            charts_section_recharts(),
            
            # Estadísticas
            stats_grid("📊 Análisis Estadístico Descriptivo", DashboardState.statistics_data),
            
            spacing="5",
            width="100%",
            padding="2em",
        ),
        size="4",
    )


# Configuración de la app
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="blue",
        gray_color="slate",
    )
)
app.add_page(index, on_load=DashboardState.on_mount)